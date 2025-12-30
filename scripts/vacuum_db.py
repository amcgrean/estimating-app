import sqlite3

def vacuum_database(db_path):
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("VACUUM")
        conn.close()
        print("Database vacuumed successfully")
    except sqlite3.OperationalError as e:
        print(f"Error during vacuum: {e}")

if __name__ == '__main__':
    db_path = '/home/amcgrean/mysite/instance/bids.db'
    vacuum_database(db_path)
