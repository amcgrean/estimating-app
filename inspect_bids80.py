import sqlite3
import sys

db_path = r"C:\Users\amcgrean\python\pa-bid-request\bids (80).db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# List all tables
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = cur.fetchall()
print("Tables:")
for t in tables:
    print(f"  {t[0]}")
    cur2 = conn.cursor()
    cur2.execute(f"PRAGMA table_info([{t[0]}])")
    cols = cur2.fetchall()
    for c in cols:
        print(f"    col: {c[1]} ({c[2]})")
    try:
        cur2.execute(f"SELECT count(*) FROM [{t[0]}]")
        cnt = cur2.fetchone()[0]
        print(f"    row count: {cnt}")
    except Exception as e:
        print(f"    count error: {e}")

conn.close()
