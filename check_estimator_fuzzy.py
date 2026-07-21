"""
Improved cross-check script for estimator IDs.
Joins on customerCode and uses fuzzy project name matching.
"""
import sqlite3
import sqlalchemy as sa
from difflib import SequenceMatcher

LOCAL_DB = r'C:\Users\amcgrean\python\pa-bid-request\bids (80).db'
NEON = 'postgresql://neondb_owner:npg_1E4CvgZbaVBW@ep-fragrant-waterfall-ad8fjcey-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'

def similar(a, b):
    return SequenceMatcher(None, a.upper(), b.upper()).ratio()

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
    local_bids = get_local_bids()
    neon_bids = get_neon_bids()

    # Map Neon bids by customerCode
    neon_by_cc = {}
    for n_id, n_proj, n_log, n_est_id, n_cc, n_est_name, n_branch in neon_bids:
        cc = n_cc.strip().upper()
        if cc not in neon_by_cc:
            neon_by_cc[cc] = []
        neon_by_cc[cc].append({
            'id': n_id,
            'project': n_proj,
            'log_date': n_log,
            'est_id': n_est_id,
            'est_name': n_est_name,
            'branch_id': n_branch
        })

    results = []
    unmatched_local = []
    
    for l_id, l_proj, l_log, l_est_id, l_cc, l_est_name in local_bids:
        cc = l_cc.strip().upper()
        best_match = None
        best_score = 0
        
        if cc in neon_by_cc:
            for n_bid in neon_by_cc[cc]:
                score = similar(l_proj, n_bid['project'])
                if score > best_score:
                    best_score = score
                    best_match = n_bid
        
        if best_match and best_score > 0.7:  # Threshold for fuzzy match
            results.append({
                'local_id': l_id,
                'neon_id': best_match['id'],
                'project_local': l_proj,
                'project_neon': best_match['project'],
                'l_est': f"{l_est_id} ({l_est_name})",
                'n_est': f"{best_match['est_id']} ({best_match['est_name']})",
                'match_score': best_score,
                'branch': best_match['branch_id'],
                'l_est_id': l_est_id,
                'n_est_id': best_match['est_id']
            })
        else:
            unmatched_local.append((l_id, l_proj, l_cc))

    print(f"Total Local Bids: {len(local_bids)}")
    print(f"Matched Bids: {len(results)}")
    print(f"Unmatched Local Bids: {len(unmatched_local)}")

    mismatches = [r for r in results if r['l_est_id'] != r['n_est_id']]
    print(f"Estimator Mismatches in Matched Bids: {len(mismatches)}")

    if mismatches:
        print("\n--- Estimator ID Mismatches (Matched via Fuzzy Project Name) ---")
        print(f"{'Neon ID':<8} {'Branch':<12} {'Local Est':<20} {'Neon Est':<20} {'Project (Neon)'}")
        print("-" * 110)
        for m in mismatches:
            branch_label = "Grimes" if m['branch'] == 1 else "Coralville" if m['branch'] == 3 else f"Other({m['branch']})"
            print(f"{m['neon_id']:<8} {branch_label:<12} {m['l_est']:<20} {m['n_est']:<20} {m['project_neon']}")

    if unmatched_local:
        print("\n--- Unmatched Local Bids (No similar project in Neon for same CustomerCode) ---")
        for u in unmatched_local[:10]:
            print(f"ID: {u[0]}, Project: {u[1]}, CC: {u[2]}")
        if len(unmatched_local) > 10:
            print(f"... and {len(unmatched_local) - 10} more.")

if __name__ == "__main__":
    main()
