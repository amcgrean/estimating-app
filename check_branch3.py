import sqlite3
from sqlalchemy import create_engine, text

LOCAL_DB = r'C:\Users\amcgrean\python\pa-bid-request\bids (80).db'
NEON = 'postgresql://neondb_owner:npg_1E4CvgZbaVBW@ep-fragrant-waterfall-ad8fjcey-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'

# Local - all records are branch 3, no branch filter needed
conn = sqlite3.connect(LOCAL_DB)
cur = conn.cursor()
cur.execute("SELECT count(*) FROM bid WHERE log_date >= '2026-01-01'")
local_count = cur.fetchone()[0]
conn.close()
print(f"Local bids (80).db  - log_date >= 2026-01-01 (all branch 3): {local_count}")

# Neon - filter branch_id = 3
engine = create_engine(NEON)
with engine.connect() as c:
    res = c.execute(text("SELECT count(*) FROM bid WHERE branch_id = 3 AND log_date >= '2026-01-01'"))
    neon_count = res.scalar()
print(f"Neon DB             - branch_id=3, log_date >= 2026-01-01:   {neon_count}")
print(f"Difference:           {local_count - neon_count}")
