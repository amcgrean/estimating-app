import os
import sqlite3
import csv
import sys
from sqlalchemy import create_engine, text

# Neon DB URL from user
NEON_DB_URL = "postgresql://neondb_owner:npg_1E4CvgZbaVBW@ep-fragrant-waterfall-ad8fjcey-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"

def check_csv(path):
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        return len(rows)

def check_sqlite(path):
    if not os.path.exists(path):
        return None
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    try:
        cur.execute("SELECT count(*) FROM bid")
        return cur.fetchone()[0]
    except Exception as e:
        try:
            cur.execute("SELECT count(*) FROM Bid") # Try capitalized
            return cur.fetchone()[0]
        except:
             return f"Error: {e}"
    finally:
        conn.close()

def check_neon(url):
    engine = create_engine(url)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT count(*) FROM bid"))
        return res.scalar()

if __name__ == "__main__":
    csv_path = "bid.csv"
    sqlite_path = "bids (79).db"
    
    print(f"Checking CSV {csv_path}...")
    csv_count = check_csv(csv_path)
    print(f"CSV Count: {csv_count}")
    
    print(f"Checking SQLite {sqlite_path}...")
    sqlite_count = check_sqlite(sqlite_path)
    print(f"SQLite Count: {sqlite_count}")
    
    print(f"Checking Neon DB...")
    try:
        neon_count = check_neon(NEON_DB_URL)
        print(f"Neon Count: {neon_count}")
    except Exception as e:
        print(f"Error checking Neon: {e}")
    
    if csv_count and sqlite_count:
        if csv_count != sqlite_count:
            print(f"WARNING: CSV count ({csv_count}) does not match SQLite count ({sqlite_count})")
        else:
            print("CSV and SQLite counts match.")
            
    if neon_count is not None and csv_count is not None:
        if neon_count < csv_count:
            print(f"RESULT: Neon DB is missing {csv_count - neon_count} bids compared to CSV.")
        elif neon_count > csv_count:
            print(f"RESULT: Neon DB has {neon_count - csv_count} more bids than CSV.")
        else:
            print("RESULT: Neon DB count matches CSV count.")
