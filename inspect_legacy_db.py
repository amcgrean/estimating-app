import sqlite3

db_path = r"C:\Users\amcgrean\python\pa-bid-request\legacy bids.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    with open('legacy_db_schema.txt', 'w', encoding='utf-8') as f:
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        f.write("--- Tables in Legacy DB ---\n")
        table_names = [t[0] for t in tables]
        for t in table_names:
            f.write(t + '\n')
            
        for t_name in table_names:
            f.write(f"\n--- '{t_name}' Table Schema ---\n")
            cursor.execute(f"PRAGMA table_info({t_name});")
            cols = cursor.fetchall()
            for col in cols:
                f.write(str(col) + '\n')
            
            # Sample row
            try:
                cursor.execute(f"SELECT * FROM {t_name} LIMIT 1;")
                row = cursor.fetchone()
                f.write(f"Sample: {row}\n")
            except:
                pass

        f.write("\n--- Sample Bid Row (id >= 8816) ---\n")
        cursor.execute("SELECT * FROM bid WHERE id >= 8816 LIMIT 1;")
        row = cursor.fetchone()
        f.write(str(row) + '\n')
    
    print("Full schema written to legacy_db_schema.txt")
    conn.close()

except Exception as e:
    print(f"Error: {e}")
