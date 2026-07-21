"""
Summarize missing estimators in Neon by year.
"""
import sqlalchemy as sa
from collections import Counter

NEON = 'postgresql://neondb_owner:npg_1E4CvgZbaVBW@ep-fragrant-waterfall-ad8fjcey-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'

engine = sa.create_engine(NEON)

with engine.connect() as conn:
    result = conn.execute(sa.text(
        """
        SELECT extract(year from b.log_date) as yr, count(*) as c
        FROM bid b
        WHERE b.estimator_id IS NULL
        GROUP BY yr
        ORDER BY yr ASC
        """
    ))
    rows = result.fetchall()
    print("NULL estimators in Neon by Year:")
    for yr, c in rows:
        print(f"{int(yr)}: {c} bids")
