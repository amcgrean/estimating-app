"""
Cross-check estimator_id between local SQLite and Neon using customerCode + project_name.
Focuses on bids from 2026-02-01 onward.
"""
import sqlite3
import sqlalchemy as sa

LOCAL_DB = r'C:\Users\amcgrean\python\pa-bid-request\bids (80).db'
NEON = 'postgresql://neondb_owner:npg_1E4CvgZbaVBW@ep-fragrant-waterfall-ad8fjcey-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'

def get_local_bids():
    conn = sqlite3.connect(LOCAL_DB)
    cur = conn.cursor()
    query = """
    SELECT b.id, b.project_name, b.log_date, b.estimator_id, c.customerCode, e.estimatorName
    FROM bid b
    JOIN customer c ON b.customer_id = c.id
    LEFT JOIN estimator e ON b.estimator_id = e.estimatorID
    WHERE date(b.log_date) >= '2026-02-01'
    """
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return rows

def get_neon_bids():
    engine = sa.create_engine(NEON)
    with engine.connect() as conn:
        query = sa.text("""
        SELECT b.id, b.project_name, b.log_date, b.estimator_id, cu."customerCode", e."estimatorName", b.branch_id
        FROM bid b
        JOIN customer cu ON b.customer_id = cu.id
        LEFT JOIN estimator e ON b.estimator_id = e."estimatorID"
        WHERE b.log_date >= '2026-02-01'
        """)
        res = conn.execute(query)
        return res.fetchall()

def main():
    print("Fetching local bids...")
    local_bids = get_local_bids()
    print(f"Found {len(local_bids)} local bids since Feb 1st.")

    print("Fetching Neon bids...")
    neon_bids = get_neon_bids()
    print(f"Found {len(neon_bids)} Neon bids since Feb 1st.")

    # Create a map for Neon bids: (customerCode, project_name) -> list of bids
    neon_map = {}
    for n_id, n_proj, n_log, n_est_id, n_cc, n_est_name, n_branch in neon_bids:
        key = (n_cc.strip().upper(), n_proj.strip().upper())
        if key not in neon_map:
            neon_map[key] = []
        neon_map[key].append({
            'id': n_id,
            'project': n_proj,
            'log_date': n_log,
            'est_id': n_est_id,
            'est_name': n_est_name,
            'branch_id': n_branch
        })

    mismatches = []
    matches_found = 0
    
    print("\nComparing...")
    for l_id, l_proj, l_log, l_est_id, l_cc, l_est_name in local_bids:
        key = (l_cc.strip().upper(), l_proj.strip().upper())
        if key in neon_map:
            matches_found += 1
            for n_bid in neon_map[key]:
                if l_est_id != n_bid['est_id']:
                    mismatches.append({
                        'local_id': l_id,
                        'neon_id': n_bid['id'],
                        'project': l_proj,
                        'cust_code': l_cc,
                        'local_est': f"{l_est_id} ({l_est_name})",
                        'neon_est': f"{n_bid['est_id']} ({n_bid['est_name']})",
                        'branch': n_bid['branch_id']
                    })

    print(f"Total matches found by (CustomerCode, ProjectName): {matches_found}")
    print(f"Total estimator ID mismatches: {len(mismatches)}")

    if mismatches:
        print("\n--- Estimator ID Mismatches (Feb 1st onward) ---")
        print(f"{'Neon ID':<8} {'Branch':<8} {'Local Est':<20} {'Neon Est':<20} {'Project'}")
        print("-" * 100)
        for m in mismatches:
            branch_label = "Grimes" if m['branch'] == 1 else "Coralville" if m['branch'] == 3 else f"Other({m['branch']})"
            print(f"{m['neon_id']:<8} {branch_label:<8} {m['local_est']:<20} {m['neon_est']:<20} {m['project']}")

if __name__ == "__main__":
    main()
