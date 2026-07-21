"""
Inspect the schema of Neon DB for 'bid' and 'customer' tables.
"""
from sqlalchemy import create_engine, text

NEON = 'postgresql://neondb_owner:npg_1E4CvgZbaVBW@ep-fragrant-waterfall-ad8fjcey-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'

def inspect():
    engine = create_engine(NEON)
    with engine.connect() as c:
        tables = ['bid', 'customer', 'estimator']
        for table in tables:
            print(f"\n--- Schema for table: {table} ---")
            res = c.execute(text(f"SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name = '{table}'"))
            for r in res:
                print(f"Column: {r[0]}, Type: {r[1]}, Nullable: {r[2]}")

if __name__ == "__main__":
    inspect()
