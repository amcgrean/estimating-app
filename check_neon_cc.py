"""
Check CustomerCode for specific bids in Neon.
"""
from sqlalchemy import create_engine, text

NEON = 'postgresql://neondb_owner:npg_1E4CvgZbaVBW@ep-fragrant-waterfall-ad8fjcey-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'

def check():
    engine = create_engine(NEON)
    with engine.connect() as c:
        for bid_id in [8878, 4653]:
            print(f"\nChecking Bid {bid_id} in Neon...")
            res = c.execute(text("""
                SELECT b.id, b.project_name, cu."customerCode", cu.name
                FROM bid b
                JOIN customer cu ON b.customer_id = cu.id
                WHERE b.id = :id
            """), {'id': bid_id})
            for r in res:
                print(f"  ID: {r[0]}, Name: {r[1]}, CC: {r[2]}, CustName: {r[3]}")

if __name__ == "__main__":
    check()
