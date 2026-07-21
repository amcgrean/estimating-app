import os
import sqlite3
import csv
from sqlalchemy import create_engine, text

# Neon DB URL from user
NEON_DB_URL = "postgresql://neondb_owner:npg_1E4CvgZbaVBW@ep-fragrant-waterfall-ad8fjcey-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"

def get_csv_ids(path):
    ids = set()
    with open(path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get('id'):
                ids.add(int(row['id']))
    return ids

def get_sqlite_ids(path):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM bid")
        return {r[0] for r in cur.fetchall()}
    except:
        cur.execute("SELECT id FROM Bid")
        return {r[0] for r in cur.fetchall()}
    finally:
        conn.close()

def get_neon_ids(url):
    engine = create_engine(url)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT id FROM bid"))
        return {r[0] for r in res.fetchall()}

if __name__ == "__main__":
    csv_path = "bid.csv"
    sqlite_path = "bids (79).db"
    
    print("Fetching IDs...")
    csv_ids = get_csv_ids(csv_path)
    sqlite_ids = get_sqlite_ids(sqlite_path)
    neon_ids = get_neon_ids(NEON_DB_URL)
    
    print(f"CSV IDs: {len(csv_ids)}")
    print(f"SQLite IDs: {len(sqlite_ids)}")
    print(f"Neon IDs: {len(neon_ids)}")
    
    # In SQLite but not in Neon
    sqlite_not_in_neon = sqlite_ids - neon_ids
    print(f"\nIDs in SQLite ({sqlite_path}) but NOT in Neon: {len(sqlite_not_in_neon)}")
    if sqlite_not_in_neon:
        print(f"Sample IDs: {list(sqlite_not_in_neon)[:10]}")
        
    # In CSV but not in Neon
    csv_not_in_neon = csv_ids - neon_ids
    print(f"\nIDs in CSV ({csv_path}) but NOT in Neon: {len(csv_not_in_neon)}")
    if csv_not_in_neon:
        print(f"Sample IDs: {list(csv_not_in_neon)[:10]}")
        
    # In Neon but not in SQLite
    neon_not_in_sqlite = neon_ids - sqlite_ids
    print(f"\nIDs in Neon but NOT in SQLite ({sqlite_path}): {len(neon_not_in_sqlite)}")
    if neon_not_in_sqlite:
        print(f"Sample IDs: {list(neon_not_in_sqlite)[:10]}")
