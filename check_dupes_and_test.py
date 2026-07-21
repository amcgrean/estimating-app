"""
Check Neon DB for:
  1. Duplicate bids (same project_name + customer_id + log_date proximity)
  2. Test records created by aaronm or amcgrean (or with test-like project names)
"""
from sqlalchemy import create_engine, text

NEON = 'postgresql://neondb_owner:npg_1E4CvgZbaVBW@ep-fragrant-waterfall-ad8fjcey-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'

engine = create_engine(NEON)
with engine.connect() as c:

    # ---- 1. DUPLICATES: Same project_name + customer_id, multiple bid IDs ----
    print("=" * 60)
    print("DUPLICATE CHECK (same project_name + customer_id)")
    print("=" * 60)
    res = c.execute(text("""
        SELECT project_name, customer_id, count(*) as cnt, array_agg(id ORDER BY id) as ids
        FROM bid
        WHERE project_name IS NOT NULL
        GROUP BY project_name, customer_id
        HAVING count(*) > 1
        ORDER BY cnt DESC, project_name
    """))
    dupes = res.fetchall()
    if dupes:
        print(f"Found {len(dupes)} duplicate groups:\n")
        for row in dupes:
            print(f"  '{row[0]}'  customer_id={row[1]}  count={row[2]}  ids={row[3]}")
    else:
        print("No duplicates found.")

    # ---- 2. TEST RECORDS: created/updated by aaronm or amcgrean ----
    print("\n" + "=" * 60)
    print("TEST RECORD CHECK (last_updated_by IN aaronm, amcgrean)")
    print("=" * 60)
    res2 = c.execute(text("""
        SELECT id, project_name, status, log_date, last_updated_by, last_updated_at, branch_id
        FROM bid
        WHERE last_updated_by IN ('aaronm', 'amcgrean')
        ORDER BY last_updated_at DESC
    """))
    user_records = res2.fetchall()
    if user_records:
        print(f"Found {len(user_records)} bids last updated by aaronm/amcgrean:\n")
        for r in user_records:
            print(f"  Bid {r[0]}  branch={r[6]}  status={r[2]}  updated_by={r[4]}  date={r[5]}  project='{r[1]}'")
    else:
        print("No records last updated by aaronm or amcgrean.")

    # ---- 3. TEST-LIKE project names ----
    print("\n" + "=" * 60)
    print("TEST-LIKE PROJECT NAMES (test, demo, sample, aaronm, amcgrean)")
    print("=" * 60)
    res3 = c.execute(text("""
        SELECT id, project_name, status, log_date, last_updated_by, branch_id
        FROM bid
        WHERE lower(project_name) LIKE '%test%'
           OR lower(project_name) LIKE '%demo%'
           OR lower(project_name) LIKE '%sample%'
           OR lower(project_name) LIKE '%aaronm%'
           OR lower(project_name) LIKE '%amcgrean%'
           OR lower(project_name) LIKE '%aaron%'
        ORDER BY log_date DESC
    """))
    test_records = res3.fetchall()
    if test_records:
        print(f"Found {len(test_records)} bids with test-like names:\n")
        for r in test_records:
            print(f"  Bid {r[0]}  branch={r[5]}  status={r[2]}  by={r[4]}  date={r[3]}  project='{r[1]}'")
    else:
        print("No test-like project names found.")

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
