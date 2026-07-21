"""
Find post-Jan-1 bids that are in local (80).db (all branch 3)
but have a different branch_id in Neon, then fix them.

Usage:
    python scripts/fix_branch3_neon.py           # dry run (shows what would change)
    python scripts/fix_branch3_neon.py --commit  # apply updates
"""
import sqlite3
import argparse
from sqlalchemy import create_engine, text

LOCAL_DB = r'C:\Users\amcgrean\python\pa-bid-request\bids (80).db'
NEON = 'postgresql://neondb_owner:npg_1E4CvgZbaVBW@ep-fragrant-waterfall-ad8fjcey-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'

def run(commit=False):
    # Get all post-Jan-1 bid IDs from local (all are branch 3)
    conn = sqlite3.connect(LOCAL_DB)
    cur = conn.cursor()
    cur.execute("SELECT id, project_name, log_date FROM bid WHERE log_date >= '2026-01-01' ORDER BY log_date")
    local_rows = {r[0]: (r[1], r[2]) for r in cur.fetchall()}
    conn.close()
    print(f"Local post-Jan-1 bids (all branch 3): {len(local_rows)}")

    engine = create_engine(NEON)
    with engine.connect() as c:
        # Get Neon branch_id for those same bid IDs
        id_list = ','.join(str(i) for i in local_rows.keys())
        res = c.execute(text(f"""
            SELECT id, branch_id, project_name, log_date
            FROM bid
            WHERE id IN ({id_list})
            ORDER BY id
        """))
        neon_data = {r[0]: {'branch_id': r[1], 'project_name': r[2], 'log_date': r[3]} for r in res.fetchall()}

        # Breakdown of current branch_id values in Neon for these bids
        from collections import Counter
        branch_counts = Counter(v['branch_id'] for v in neon_data.values())
        print(f"\nCurrent branch_id breakdown in Neon for these {len(neon_data)} bids:")
        for branch_id, cnt in sorted(branch_counts.items(), key=lambda x: (x[0] is None, x[0])):
            print(f"  branch_id={branch_id}: {cnt} bids")

        # Find bids where Neon branch_id != 3
        to_fix = {bid_id: data for bid_id, data in neon_data.items() if data['branch_id'] != 3}
        print(f"\nBids to update (branch_id != 3): {len(to_fix)}")
        for bid_id, data in sorted(to_fix.items()):
            print(f"  Bid {bid_id}  branch_id={data['branch_id']} -> 3  {data['log_date']}  {data['project_name']}")

        if not commit:
            print("\nDRY RUN complete. Use --commit to apply changes.")
            return

        if to_fix:
            print("\nApplying branch_id=3 updates to Neon...")
            ids_to_fix = list(to_fix.keys())
            # Use parameterized ANY() for safety
            c.execute(text("""
                UPDATE bid SET branch_id = 3
                WHERE id = ANY(:ids)
            """), {'ids': ids_to_fix})
            c.commit()
            print(f"Done. Updated {len(ids_to_fix)} bids to branch_id=3.")
        else:
            print("Nothing to update.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--commit', action='store_true')
    args = parser.parse_args()
    run(commit=args.commit)
