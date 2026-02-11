import sqlite3

db_path = r"C:\Users\amcgrean\python\pa-bid-request\legacy bids.db"

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    with open('legacy_estimators.txt', 'w', encoding='utf-8') as f:
        f.write("--- Legacy Estimators ---\n")
        cursor.execute("SELECT estimatorID, estimatorName, type FROM estimator")
        rows = cursor.fetchall()
        for r in rows:
            f.write(str(r) + '\n')
            
    print("Estimators written to legacy_estimators.txt")
    conn.close()

except Exception as e:
    print(f"Error: {e}")
