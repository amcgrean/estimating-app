"""
Find post-Jan-1 bids associated with estimator 'jasonr' that we incorrectly
moved to branch_id=1 (Grimes), and revert them to branch_id=3 (Coralville).
"""
import argparse
from sqlalchemy import create_engine, text

NEON = 'postgresql://neondb_owner:npg_1E4CvgZbaVBW@ep-fragrant-waterfall-ad8fjcey-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'

def run(commit=False):
    engine = create_engine(NEON)
    with engine.connect() as c:

        # Find jasonr's estimator ID
        res = c.execute(text("""
            SELECT e."estimatorID", e."estimatorName", e."estimatorUsername"
            FROM estimator e
            WHERE lower(e."estimatorUsername") = 'jasonr'
               OR lower(e."estimatorName") LIKE '%jason%'
        """))
        estimators = res.fetchall()
        print("Matching estimators:")
        for e in estimators:
            print(f"  ID={e[0]}  Name={e[1]}  Username={e[2]}")

        if not estimators:
            print("No estimator found for jasonr.")
            return

        est_ids = [e[0] for e in estimators]

        # Find post-Jan-1 bids with jasonr as estimator on branch_id=1
        id_list = ','.join(str(i) for i in est_ids)
        res2 = c.execute(text(f"""
            SELECT b.id, b.project_name, b.status, b.log_date, b.branch_id, b.estimator_id,
                   e."estimatorUsername"
            FROM bid b
            JOIN estimator e ON e."estimatorID" = b.estimator_id
            WHERE b.estimator_id IN ({id_list})
              AND b.log_date >= '2026-01-01'
              AND b.branch_id = 1
            ORDER BY b.log_date
        """))
        bids = res2.fetchall()
        print(f"\nPost-Jan-1 bids with jasonr as estimator currently on branch_id=1 (Grimes): {len(bids)}")
        for b in bids:
            print(f"  Bid {b[0]}  {b[3]}  status={b[2]}  estimator={b[6]}  '{b[1]}'")

        if not bids:
            print("Nothing to fix.")
            return

        if not commit:
            print(f"\nDRY RUN — {len(bids)} bids would be moved back to branch_id=3 (Coralville). Use --commit to apply.")
            return

        # Fix: move them back to Coralville (branch_id=3)
        bid_ids = [b[0] for b in bids]
        c.execute(text("UPDATE bid SET branch_id = 3 WHERE id = ANY(:ids)"), {'ids': bid_ids})
        c.commit()
        print(f"\nReverted {len(bid_ids)} bids to branch_id=3 (Coralville).")

        # Final branch breakdown
        res3 = c.execute(text("""
            SELECT b.branch_id, br.branch_name, count(*) as cnt
            FROM bid b
            LEFT JOIN branch br ON br.branch_id = b.branch_id
            WHERE b.log_date >= '2026-01-01'
            GROUP BY b.branch_id, br.branch_name
            ORDER BY b.branch_id
        """))
        print("\nFinal branch breakdown (post Jan 1 bids):")
        for row in res3.fetchall():
            print(f"  branch_id={row[0]} ({row[1]}): {row[2]} bids")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--commit', action='store_true')
    args = parser.parse_args()
    run(commit=args.commit)
