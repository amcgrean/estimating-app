"""
1. Fix branch assignments: revert post-Jan-1 local bids from branch_id=3 back to branch_id=1 (Grimes)
2. Delete test bid 8796 (cascade: bid_value first, then bid)
"""
import sqlite3
from sqlalchemy import create_engine, text

LOCAL_DB = r'C:\Users\amcgrean\python\pa-bid-request\bids (80).db'
NEON = 'postgresql://neondb_owner:npg_1E4CvgZbaVBW@ep-fragrant-waterfall-ad8fjcey-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'

# Get all local post-Jan-1 bid IDs (these belong to Grimes = branch_id=1)
conn = sqlite3.connect(LOCAL_DB)
cur = conn.cursor()
cur.execute("SELECT id FROM bid WHERE log_date >= '2026-01-01'")
local_ids = [r[0] for r in cur.fetchall()]
conn.close()
print(f"Local post-Jan-1 bids (should all be Grimes / branch_id=1): {len(local_ids)}")

engine = create_engine(NEON)
with engine.connect() as c:

    # --- Show current branch state before fix ---
    res = c.execute(text("""
        SELECT b.branch_id, br.branch_name, count(*) as cnt
        FROM bid b
        LEFT JOIN branch br ON br.branch_id = b.branch_id
        WHERE b.log_date >= '2026-01-01'
        GROUP BY b.branch_id, br.branch_name
        ORDER BY b.branch_id
    """))
    print("\nCurrent branch breakdown (before fix):")
    for row in res.fetchall():
        print(f"  branch_id={row[0]} ({row[1]}): {row[2]} bids")

    # --- Fix: set all local post-Jan-1 bids to branch_id=1 (Grimes) ---
    result = c.execute(text("""
        UPDATE bid SET branch_id = 1
        WHERE id = ANY(:ids)
    """), {'ids': local_ids})
    c.commit()
    print(f"\nUpdated {result.rowcount} bids to branch_id=1 (Grimes)")

    # --- Delete test bid 8796 (cascade bid_value first) ---
    bv = c.execute(text("DELETE FROM bid_value WHERE bid_id = 8796"))
    c.commit()
    print(f"\nDeleted {bv.rowcount} bid_value row(s) for Bid 8796")
    c.execute(text("DELETE FROM bid WHERE id = 8796"))
    c.commit()
    print("Deleted Bid 8796 ('austin test')")

    # --- Verify final state ---
    res2 = c.execute(text("""
        SELECT b.branch_id, br.branch_name, count(*) as cnt
        FROM bid b
        LEFT JOIN branch br ON br.branch_id = b.branch_id
        WHERE b.log_date >= '2026-01-01'
        GROUP BY b.branch_id, br.branch_name
        ORDER BY b.branch_id
    """))
    print("\nFinal branch breakdown (after fix):")
    for row in res2.fetchall():
        print(f"  branch_id={row[0]} ({row[1]}): {row[2]} bids")
