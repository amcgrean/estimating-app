"""
Compare estimator_id values between bids (80).db and Neon
for all bids that exist in both.
"""
import sqlite3
from sqlalchemy import create_engine, text

LOCAL_DB = r'C:\Users\amcgrean\python\pa-bid-request\bids (80).db'
NEON = 'postgresql://neondb_owner:npg_1E4CvgZbaVBW@ep-fragrant-waterfall-ad8fjcey-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'

# Load local estimator_ids
conn = sqlite3.connect(LOCAL_DB)
cur = conn.cursor()
cur.execute("SELECT id, estimator_id, project_name FROM bid ORDER BY id")
local = {r[0]: {'estimator_id': r[1], 'project': r[2]} for r in cur.fetchall()}
conn.close()

# Load Neon estimator_ids + names
engine = create_engine(NEON)
with engine.connect() as c:
    res = c.execute(text("""
        SELECT b.id, b.estimator_id, b.project_name, e."estimatorName"
        FROM bid b
        LEFT JOIN estimator e ON e."estimatorID" = b.estimator_id
        ORDER BY b.id
    """))
    neon = {r[0]: {'estimator_id': r[1], 'project': r[2], 'name': r[3]} for r in res.fetchall()}

# Compare
mismatches = []
for bid_id, ldata in local.items():
    if bid_id not in neon:
        continue
    ndata = neon[bid_id]
    local_est = int(ldata['estimator_id']) if ldata['estimator_id'] else None
    neon_est  = int(ndata['estimator_id']) if ndata['estimator_id'] else None
    if local_est != neon_est:
        mismatches.append({
            'bid_id': bid_id,
            'project': ldata['project'],
            'local_est': local_est,
            'neon_est': neon_est,
            'neon_name': ndata['name'],
        })

print(f"Bids checked: {len(local)}")
print(f"Estimator_id mismatches: {len(mismatches)}")

if mismatches:
    print(f"\n{'Bid':>6}  {'Local Est':>10}  {'Neon Est':>10}  {'Neon Name':<20}  Project")
    print("-" * 90)
    for m in mismatches:
        print(f"  {m['bid_id']:>6}  {str(m['local_est']):>10}  {str(m['neon_est']):>10}  {str(m['neon_name']):<20}  {m['project']}")
else:
    print("All estimator_ids match between local and Neon.")
