import os
import sys
import sqlite3
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from project import create_app, db
from project.models import Bid

LEGACY_DB_PATH = r"C:\Users\amcgrean\Downloads\bids (76).db"

def sync_bids():
    if not os.path.exists(LEGACY_DB_PATH):
        print(f"Error: Legacy database not found via path: {LEGACY_DB_PATH}")
        return

    print("Connecting to legacy database...")
    conn_legacy = sqlite3.connect(LEGACY_DB_PATH)
    conn_legacy.row_factory = sqlite3.Row
    cur_legacy = conn_legacy.cursor()
    
    try:
        cur_legacy.execute("SELECT * FROM bid") # Assuming table name is 'bid'
        legacy_bids = cur_legacy.fetchall()
    except sqlite3.OperationalError:
         try:
            cur_legacy.execute("SELECT * FROM Bid") # Try capitalized
            legacy_bids = cur_legacy.fetchall()
         except Exception as e:
            print(f"Error reading legacy bids: {e}")
            return

    print(f"Found {len(legacy_bids)} bids in legacy database.")

    app = create_app()
    with app.app_context():
        print(f"Syncing to active database: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        count_added = 0
        count_updated = 0
        count_skipped = 0
        
        # Cache existing bids for faster lookup
        # Fetching all IDs might be memory intensive if millions, but 8700 is fine.
        existing_bids_map = {b.id: b for b in Bid.query.all()}
        
        for row in legacy_bids:
            bid_id = row['id']
            legacy_status = row['status']
            legacy_estimator = row['estimator_id']
            if legacy_estimator == 0:
                legacy_estimator = None
            
            # Helper to parse dates if they are strings in SQLite
            def parse_date(val):
                if not val:
                    return None
                if isinstance(val, (datetime, float, int)): # Already date or timestamp
                     # logic to handle timestamp if needed, likely string in sqlite
                     return val
                try:
                    # SQLite often stores as 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'
                    if len(val) > 10:
                        return datetime.strptime(val, '%Y-%m-%d %H:%M:%S.%f')
                    return datetime.strptime(val, '%Y-%m-%d').date()
                except:
                     try:
                        return datetime.strptime(val, '%Y-%m-%d')
                     except:
                        return None # Fallback

            if bid_id in existing_bids_map:
                existing_bid = existing_bids_map[bid_id]
                updated = False
                
                # Check for updates
                if existing_bid.status != legacy_status:
                    existing_bid.status = legacy_status
                    updated = True
                
                if existing_bid.estimator_id != legacy_estimator:
                    existing_bid.estimator_id = legacy_estimator
                    updated = True
                
                if updated:
                    count_updated += 1
                else:
                    count_skipped += 1
            else:
                # Insert new bid
                # Mapping columns. Assuming names match mostly.
                try:
                    new_bid = Bid(
                        id=bid_id,
                        plan_type=row['plan_type'],
                        # customer_id might need validation if customer doesn't exist? 
                        # For now assume sync is raw data integrity.
                        customer_id=row['customer_id'], 
                        project_name=row['project_name'],
                        estimator_id=legacy_estimator,
                        status=legacy_status,
                        due_date=parse_date(row['due_date']) if isinstance(row['due_date'], str) else row['due_date'],
                        notes=row['notes'],
                        # Handle other fields if model requires
                        branch_id=row['branch_id'] if 'branch_id' in row.keys() else None 
                    )
                    
                    # Handle fields that might be missing in legacy or named diff
                    if 'created_at' in row.keys():
                         new_bid.created_at = parse_date(row['created_at']) if isinstance(row['created_at'], str) else row['created_at']
                    
                    db.session.add(new_bid)
                    count_added += 1
                except Exception as e:
                    print(f"Error preparing insert for ID {bid_id}: {e}")

            if (count_added + count_updated) % 100 == 0:
                db.session.commit()
                print(f"Processed {count_added + count_updated + count_skipped}...")

        db.session.commit()
        print("Scync Complete.")
        print(f"Added: {count_added}")
        print(f"Updated: {count_updated}")
        print(f"Skipped: {count_skipped}")

if __name__ == "__main__":
    sync_bids()
