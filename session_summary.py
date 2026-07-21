"""
1. Check the 1 NULL branch_id post-Jan-1 bid
2. Summary of all changes made to Neon DB today (2026-03-18)
"""
from sqlalchemy import create_engine, text

NEON = 'postgresql://neondb_owner:npg_1E4CvgZbaVBW@ep-fragrant-waterfall-ad8fjcey-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'
TODAY = '2026-03-18'

engine = create_engine(NEON)
with engine.connect() as c:

    # ---- NULL branch bid ----
    print("=" * 60)
    print("NULL BRANCH BID (post Jan 1)")
    print("=" * 60)
    res = c.execute(text("""
        SELECT b.id, b.project_name, b.status, b.log_date, b.estimator_id,
               b.last_updated_by, b.last_updated_at,
               e."estimatorName"
        FROM bid b
        LEFT JOIN estimator e ON e."estimatorID" = b.estimator_id
        WHERE b.branch_id IS NULL AND b.log_date >= '2026-01-01'
    """))
    for r in res.fetchall():
        print(f"  Bid {r[0]}")
        print(f"    Project:     {r[1]}")
        print(f"    Status:      {r[2]}")
        print(f"    Log Date:    {r[3]}")
        print(f"    Estimator:   {r[7]} (id={r[4]})")
        print(f"    Updated By:  {r[5]}  at  {r[6]}")

    # ---- INSERTED today ----
    print("\n" + "=" * 60)
    print(f"BIDS INSERTED TODAY ({TODAY})")
    print("=" * 60)
    res2 = c.execute(text(f"""
        SELECT b.id, b.project_name, b.status, b.branch_id, br.branch_name,
               b.log_date, b.last_updated_by,
               e."estimatorName"
        FROM bid b
        LEFT JOIN branch br ON br.branch_id = b.branch_id
        LEFT JOIN estimator e ON e."estimatorID" = b.estimator_id
        WHERE b.log_date >= '{TODAY}'
        ORDER BY b.id
    """))
    inserted = res2.fetchall()
    print(f"Total: {len(inserted)}")
    for r in inserted:
        print(f"  Bid {r[0]}  branch={r[3]} ({r[4]})  status={r[2]}  estimator={r[7]}  '{r[1]}'")

    # ---- UPDATED today (last_updated_at = today but log_date is older) ----
    print("\n" + "=" * 60)
    print(f"BIDS WITH FIELDS UPDATED TODAY ({TODAY}) via sync")
    print("=" * 60)
    res3 = c.execute(text(f"""
        SELECT b.id, b.project_name, b.status, b.branch_id, br.branch_name,
               b.log_date, b.last_updated_by, b.last_updated_at,
               e."estimatorName"
        FROM bid b
        LEFT JOIN branch br ON br.branch_id = b.branch_id
        LEFT JOIN estimator e ON e."estimatorID" = b.estimator_id
        WHERE date(b.last_updated_at) = '{TODAY}'
          AND b.log_date < '{TODAY}'
        ORDER BY b.id
    """))
    updated = res3.fetchall()
    print(f"Total: {len(updated)} bids had status/fields synced today")
    for r in updated:
        print(f"  Bid {r[0]}  branch={r[3]} ({r[4]})  status={r[2]}  estimator={r[8]}  log={r[5]}  '{r[1]}'")

    # ---- BRANCH changes (bulk updates we did - approximate via branch_id=1 bids in range) ----
    print("\n" + "=" * 60)
    print("BRANCH ID ASSIGNMENTS (post-Jan-1 final state)")
    print("=" * 60)
    res4 = c.execute(text("""
        SELECT b.branch_id, br.branch_name, count(*) as cnt
        FROM bid b
        LEFT JOIN branch br ON br.branch_id = b.branch_id
        WHERE b.log_date >= '2026-01-01'
        GROUP BY b.branch_id, br.branch_name
        ORDER BY b.branch_id
    """))
    for row in res4.fetchall():
        print(f"  branch_id={row[0]} ({row[1]}): {row[2]} bids")

    print("\n" + "=" * 60)
    print("OVERALL NEON BID COUNT")
    print("=" * 60)
    res5 = c.execute(text("SELECT count(*) FROM bid"))
    print(f"  Total bids: {res5.scalar()}")
