"""
List Neon bids where estimator_id IS NULL (or missing).
"""
import sqlalchemy as sa

NEON = 'postgresql://neondb_owner:npg_1E4CvgZbaVBW@ep-fragrant-waterfall-ad8fjcey-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'

engine = sa.create_engine(NEON)

with engine.connect() as conn:
    result = conn.execute(sa.text(
        """
        SELECT b.id, b.project_name, b.log_date, b.branch_id, cu."customerCode"
        FROM bid b
        JOIN customer cu ON b.customer_id = cu.id
        WHERE b.estimator_id IS NULL
        ORDER BY b.log_date ASC
        """
    ))
    rows = result.fetchall()
    print(f'Found {len(rows)} Neon bids with NULL estimator_id:')
    for r in rows:
        print(f'ID {r.id:<6} | Branch: {r.branch_id} | Log Date: {r.log_date} | Project: {r.project_name} | CustomerCode: {r.customerCode}')
