"""
Final check: examine the 38 'missing' local bids and see if their project names
already exist in Neon under any customer code.
"""
import sqlite3
import sqlalchemy as sa

LOCAL_DB = r'C:\Users\amcgrean\python\pa-bid-request\bids (80).db'
NEON = 'postgresql://neondb_owner:npg_1E4CvgZbaVBW@ep-fragrant-waterfall-ad8fjcey-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'

def get_missing_local():
    conn = sqlite3.connect(LOCAL_DB)
    cur = conn.cursor()
    # These were the IDs that didn't match fuzzy (CC, Proj)
    # I'll just fetch all post-Feb-1 bids and check them against a Neon name map
    cur.execute("SELECT id, project_name, customer_id FROM bid WHERE date(log_date) >= '2026-02-01'")
    rows = cur.fetchall()
    conn.close()
    return rows

def check():
    local_bids = get_missing_local()
    
    engine = sa.create_engine(NEON)
    with engine.connect() as conn:
        res = conn.execute(sa.text("SELECT id, project_name, customer_id FROM bid"))
        neon_names = {r[1].strip().upper(): r[0] for r in res.fetchall() if r[1]}

        found_by_name = []
        actually_missing = []

        for l_id, l_name, l_cust_id in local_bids:
            name_key = l_name.strip().upper()
            if name_key in neon_names:
                found_by_name.append((l_id, l_name, neon_names[name_key]))
            else:
                actually_missing.append((l_id, l_name))

        print(f"Total post-Feb local bids: {len(local_bids)}")
        print(f"Found in Neon by Name (any CC): {len(found_by_name)}")
        print(f"Truly missing: {len(actually_missing)}")
        
        if found_by_name:
            print("\nExamples found by name but failed (CC, Proj) match:")
            for l_id, l_name, n_id in found_by_name[:5]:
                print(f"  Local ID {l_id} ('{l_name}') -> Neon ID {n_id}")

if __name__ == "__main__":
    check()
