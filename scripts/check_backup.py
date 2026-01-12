
import sqlite3
import os

def check_backup():
    db_path = 'instance/bids_backup.db'
    if not os.path.exists(db_path):
        print(f"{db_path} does not exist.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tables in {db_path}:")
        for t in tables:
            table_name = t[0]
            try:
                cursor.execute(f"SELECT count(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  - {table_name}: {count}")
            except Exception as e:
                print(f"  - {table_name}: Error {e}")
        
        conn.close()
    except Exception as e:
        print(f"Error checking backup: {e}")

if __name__ == "__main__":
    check_backup()
