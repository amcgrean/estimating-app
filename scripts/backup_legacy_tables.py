
import os
import csv
from datetime import datetime
from project import create_app, db
from sqlalchemy import text

app = create_app()

LEGACY_TABLES = ['framing', 'siding', 'shingle', 'deck', 'trim', 'window', 'door']
BACKUP_DIR = os.path.join(os.getcwd(), 'backups', 'legacy_tables')

def backup_tables():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        
    print(f"Starting backup to {BACKUP_DIR}...")
    
    with app.app_context():
        for table_name in LEGACY_TABLES:
            try:
                # Check if table exists
                query = text(f"SELECT * FROM {table_name}")
                result = db.session.execute(query)
                keys = result.keys()
                rows = result.fetchall()
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{table_name}_{timestamp}.csv"
                filepath = os.path.join(BACKUP_DIR, filename)
                
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(keys)
                    writer.writerows(rows)
                    
                print(f"[SUCCESS] Backed up {table_name}: {len(rows)} rows -> {filename}")
                
            except Exception as e:
                print(f"[WARNING] Could not backup {table_name}: {e}")

def drop_tables():
    print("\n--- DROPPING TABLES ---")
    confirm = input("Are you sure you want to DROP legacy tables? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Aborted.")
        return

    with app.app_context():
        for table_name in LEGACY_TABLES:
            try:
                db.session.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
                print(f"[SUCCESS] Dropped table {table_name}")
            except Exception as e:
                print(f"[ERROR] Failed to drop {table_name}: {e}")
        
        db.session.commit()
        print("Done.")

if __name__ == "__main__":
    backup_tables()
    # Uncomment to drop
    # drop_tables()
