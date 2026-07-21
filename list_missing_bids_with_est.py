"""
List the 38 bids that safe_sync_bids_to_neon would insert, showing their local log_date and estimator_id.
"""
import sqlite3
import sqlalchemy as sa
from difflib import SequenceMatcher

LOCAL_DB = r'C:\Users\amcgrean\python\pa-bid-request\bids (80).db'
NEON = 'postgresql://neondb_owner:npg_1E4CvgZbaVBW@ep-fragrant-waterfall-ad8fjcey-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'

def similar(a, b):
    if not a or not b:
        return 0
    return SequenceMatcher(None, a.upper(), b.upper()).ratio()

def get_local_bids():
    conn = sqlite3.connect(LOCAL_DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT b.id, b.project_name, b.log_date, b.estimator_id, c.customerCode
        FROM bid b
        JOIN customer c ON b.customer_id = c.id
        WHERE date(b.log_date) >= '2026-02-01'
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def get_neon_bids():
    engine = sa.create_engine(NEON)
    with engine.connect() as conn:
        res = conn.execute(sa.text("""
            SELECT b.id, b.project_name, cu."customerCode"
            FROM bid b
            JOIN customer cu ON b.customer_id = cu.id
            WHERE b.log_date >= '2026-01-01'
        """))
        return res.fetchall()

def main():
    local = get_local_bids()
    neon = get_neon_bids()
    neon_by_cc = {}
    for n_id, n_proj, n_cc in neon:
        cc = n_cc.strip().upper()
        neon_by_cc.setdefault(cc, []).append({'id': n_id, 'project': n_proj})

    missing = []
    for l_id, l_proj, l_log, l_est, l_cc in local:
        cc = l_cc.strip().upper()
        best_score = 0
        best_match = None
        if cc in neon_by_cc:
            for n in neon_by_cc[cc]:
                score = similar(l_proj, n['project'])
                if score > best_score:
                    best_score = score
                    best_match = n
        if not (best_match and best_score > 0.85):
            missing.append((l_id, l_proj, l_log, l_est, l_cc))

    print(f"Found {len(missing)} bids that would be inserted (showing estimator_id):")
    for bid in missing:
        est_display = 'NULL' if bid[3] is None else str(bid[3])
        print(f"ID {bid[0]:<5} | Log Date: {bid[2]} | Estimator ID: {est_display} | Project: {bid[1]} | CustomerCode: {bid[4]}")

if __name__ == '__main__':
    main()
