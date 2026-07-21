"""
Full summary of all Coralville (branch_id=3) bids touched this session:
  - Current branch_id=3 bids (post Jan 1)
  - Cross-check: any jasonr bids pre-Jan-1 also on branch 3?
  - Status of each bid
"""
from sqlalchemy import create_engine, text

NEON = 'postgresql://neondb_owner:npg_1E4CvgZbaVBW@ep-fragrant-waterfall-ad8fjcey-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'

engine = create_engine(NEON)
with engine.connect() as c:

    # All current branch_id=3 bids (any date) with jasonr as estimator
    res = c.execute(text("""
        SELECT b.id, b.project_name, b.status, b.log_date,
               b.due_date, b.completion_date,
               b.last_updated_by, b.last_updated_at,
               e."estimatorName", e."estimatorUsername",
               b.branch_id
        FROM bid b
        LEFT JOIN estimator e ON e."estimatorID" = b.estimator_id
        WHERE b.branch_id = 3
          AND b.log_date >= '2026-01-01'
        ORDER BY b.log_date
    """))
    bids = res.fetchall()

    print(f"All branch_id=3 (Coralville) bids post-Jan-1: {len(bids)}")
    print(f"{'Bid':>6}  {'Log Date':<26}  {'Status':<12}  {'Estimator':<16}  {'Updated By':<14}  Project")
    print("-" * 110)
    for r in bids:
        bid_id     = r[0]
        project    = r[1] or ''
        status     = r[2] or ''
        log_date   = str(r[3])[:19] if r[3] else ''
        updated_by = r[6] or ''
        estimator  = r[8] or ''
        print(f"  {bid_id:>6}  {log_date:<26}  {status:<12}  {estimator:<16}  {updated_by:<14}  {project}")

    print(f"\nTotal: {len(bids)}")

    # Summary counts
    complete   = sum(1 for r in bids if r[2] == 'Complete')
    incomplete = sum(1 for r in bids if r[2] == 'Incomplete')
    print(f"  Complete:   {complete}")
    print(f"  Incomplete: {incomplete}")

    # Any jasonr bids with branch_id != 3 (safety check - should be 0 post-Jan-1)
    res2 = c.execute(text("""
        SELECT count(*) FROM bid b
        JOIN estimator e ON e."estimatorID" = b.estimator_id
        WHERE lower(e."estimatorUsername") = 'jasonr'
          AND b.log_date >= '2026-01-01'
          AND b.branch_id != 3
    """))
    wrong_branch = res2.scalar()
    print(f"\nSafety check — jasonr bids post-Jan-1 NOT on branch_id=3: {wrong_branch} (should be 0)")
