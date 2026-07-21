"""
Analyze ID collisions between local SQLite and Neon.
Finds all cases where the same ID exists in both but refers to different projects.
"""
import sqlite3
import sqlalchemy as sa
from difflib import SequenceMatcher

LOCAL_DB = r'C:\Users\amcgrean\python\pa-bid-request\bids (80).db'
NEON = 'postgresql://neondb_owner:npg_1E4CvgZbaVBW@ep-fragrant-waterfall-ad8fjcey-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'

def similar(a, b):
    if not a or not b: return 0
    return SequenceMatcher(None, a.upper(), b.upper()).ratio()

def main():
    # 1. Fetch Local Bids (all, for full ID check)
    conn = sqlite3.connect(LOCAL_DB)
    cur = conn.cursor()
    cur.execute("SELECT id, project_name, log_date FROM bid")
    local_bids = {r[0]: {'project': r[1], 'log_date': r[2]} for r in cur.fetchall()}
    conn.close()

    # 2. Fetch Neon Bids
    engine = sa.create_engine(NEON)
    with engine.connect() as conn:
        res = conn.execute(sa.text("SELECT id, project_name, log_date, branch_id FROM bid"))
        neon_bids = {r[0]: {'project': r[1], 'log_date': r[2], 'branch': r[3]} for r in res.fetchall()}

    # 3. Find Shared IDs and calculate similarity
    collisions = []
    print(f"Comparing {len(local_bids)} local bids with {len(neon_bids)} Neon bids...")
    
    shared_ids = set(local_bids.keys()) & set(neon_bids.keys())
    print(f"Total shared IDs: {len(shared_ids)}")

    for bid_id in sorted(shared_ids):
        l_proj = local_bids[bid_id]['project']
        n_proj = neon_bids[bid_id]['project']
        score = similar(l_proj, n_proj)
        
        if score < 0.6:  # Significant difference
            collisions.append({
                'id': bid_id,
                'l_proj': l_proj,
                'n_proj': n_proj,
                'l_date': local_bids[bid_id]['log_date'],
                'n_date': neon_bids[bid_id]['log_date'],
                'branch': neon_bids[bid_id]['branch'],
                'score': score
            })

    print(f"\nFound {len(collisions)} ID collisions (Project Name similarity < 60%)")
    
    if collisions:
        print(f"\n{'ID':<8} {'Branch':<8} {'Local Project':<40} {'Neon Project'}")
        print("-" * 100)
        for c in collisions:
            branch_label = "Grimes" if c['branch'] == 1 else "Coralville" if c['branch'] == 3 else f"Other({c['branch']})"
            print(f"{c['id']:<8} {branch_label:<8} {c['l_proj'][:40]:<40} {c['n_proj'][:40]}")
            
    # Also check for IDs that exist locally but are DIFFERENT project IDs in Neon 
    # (i.e. if Jamie Hatch is 8880 locally but 4653 in Neon)
    # This requires searching Neon by project name for unmatched local IDs.
    # (Already did a sample of this, but listing all would be too much here)

if __name__ == "__main__":
    main()
