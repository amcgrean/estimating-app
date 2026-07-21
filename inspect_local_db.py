"""
Inspect the schema of bids (80).db to confirm column names for bid and customer tables.
"""
import sqlite3

def inspect():
    db_path = 'bids (80).db'
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    tables = ['bid', 'customer', 'estimator']
    for table in tables:
        print(f"\n--- Schema for table: {table} ---")
        try:
            cur.execute(f"PRAGMA table_info({table})")
            info = cur.fetchall()
            for col in info:
                print(f"ID: {col[0]}, Name: {col[1]}, Type: {col[2]}, NotNull: {col[3]}, Default: {col[4]}, PK: {col[5]}")
        except Exception as e:
            print(f"Error inspecting {table}: {e}")
            
    conn.close()

if __name__ == "__main__":
    inspect()
