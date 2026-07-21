from sqlalchemy import create_engine, text
NEON = 'postgresql://neondb_owner:npg_1E4CvgZbaVBW@ep-fragrant-waterfall-ad8fjcey-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'
engine = create_engine(NEON)
with engine.connect() as c:
    # Confirm bid 8796 is gone
    res = c.execute(text("SELECT count(*) FROM bid WHERE id = 8796"))
    print(f"Bid 8796 remaining: {res.scalar()} (should be 0)")

    # Final branch breakdown post-Jan-1
    res2 = c.execute(text("""
        SELECT b.branch_id, br.branch_name, count(*) as cnt
        FROM bid b
        LEFT JOIN branch br ON br.branch_id = b.branch_id
        WHERE b.log_date >= '2026-01-01'
        GROUP BY b.branch_id, br.branch_name
        ORDER BY b.branch_id
    """))
    print("\nFinal branch breakdown (post Jan 1 bids):")
    for row in res2.fetchall():
        print(f"  branch_id={row[0]} ({row[1]}): {row[2]} bids")
