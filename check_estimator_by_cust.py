"""
Cross‑check estimator_id between the local SQLite (bids (80).db) and Neon for
all bids logged on or after 2026‑02‑01. The join is performed on `customer_code`
(and optionally `project_name`) because bid IDs diverge between the Grimes and
Coralville branches.
"""
import sqlite3
from sqlalchemy import create_engine, text

LOCAL_DB = r'C:\Users\amcgrean\python\pa-bid-request\bids (80).db'
NEON = 'postgresql://neondb_owner:npg_1E4CvgZbaVBW@ep-fragrant-waterfall-ad8fjcey-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'

# Load local bids (id, estimator_id, customer_code, log_date, project_name)
conn = sqlite3.connect(LOCAL_DB)
cur = conn.cursor()
cur.execute("""
    SELECT id, estimator_id, customer_code, log_date, project_name
    FROM bid
    WHERE date(log_date) >= '2026-02-01'
""")
local_rows = cur.fetchall()
conn.close()

# Build a map keyed by (customer_code, project_name) – project_name helps disambiguate
local_map = {}
for bid_id, est_id, cust_code, log_date, proj in local_rows:
    key = (cust_code, proj)
    local_map[key] = {
        'bid_id': bid_id,
        'estimator_id': int(est_id) if est_id is not None else None,
        'log_date': log_date,
        'project': proj,
    }

# Query Neon for the same fields
engine = create_engine(NEON)
with engine.connect() as c:
    res = c.execute(text("""
        SELECT b.id, b.estimator_id, b.customer_code, b.log_date, b.project_name, e."estimatorName"
        FROM bid b
        LEFT JOIN estimator e ON e."estimatorID" = b.estimator_id
        WHERE b.log_date >= '2026-02-01'
    """))
    neon_rows = res.fetchall()

# Compare using the same (customer_code, project_name) key
mismatches = []
for nid, n_est, n_cust, n_log, n_proj, n_name in neon_rows:
    key = (n_cust, n_proj)
    if key not in local_map:
        continue  # not present locally – ignore (could be older Coralville only)
    l = local_map[key]
    local_est = l['estimator_id']
    neon_est = int(n_est) if n_est is not None else None
    if local_est != neon_est:
        mismatches.append({
            'customer_code': n_cust,
            'project': n_proj,
            'local_bid_id': l['bid_id'],
            'neon_bid_id': nid,
            'local_est': local_est,
            'neon_est': neon_est,
            'neon_name': n_name,
            'log_date': n_log,
        })

print(f"Checked {len(local_rows)} local bids (Feb‑01 onward).")
print(f"Found {len(mismatches)} estimator mismatches.")
if mismatches:
    print("\nMismatches (customer_code, project):")
    print("{:<12} {:<30} {:>8} {:>8} {:>12} {:<20}".format('CustCode','Project','LocalEst','NeonEst','BidID','NeonName'))
    print('-'*100)
    for m in mismatches:
        print(f"{m['customer_code']:<12} {m['project'][:30]:<30} {str(m['local_est']):>8} {str(m['neon_est']):>8} {m['neon_bid_id']:>12} {m['neon_name'] or '' :<20}")
else:
    print("All estimator IDs match for the Feb‑onward records.")
