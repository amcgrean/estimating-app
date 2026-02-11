import sys
import os
import sqlite3
from sqlalchemy import text
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from project import create_app, db
from project.models import Bid, Customer, User, Estimator

def get_legacy_connection():
    legacy_db_path = r"C:\Users\amcgrean\python\pa-bid-request\legacy bids.db"
    return sqlite3.connect(legacy_db_path)

def import_legacy_bids():
    app = create_app()
    with app.app_context():
        print(f"Using Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # 1. Load Mappings
        print("Loading Mappings...")
        
        # Current Customers: Code -> ID
        # Note: Customer model might not have 'customerCode' explicitly defined in the snippet I saw earlier, 
        # but import_data.py uses it. I'll double check if I need to fetch it differently.
        # Assuming Customer has customerCode based on previous usage.
        customers = Customer.query.all()
        # Create map, normalizing code to uppercase just in case
        customer_map = {c.customerCode.strip().upper(): c for c in customers if c.customerCode}
        print(f"Loaded {len(customer_map)} Customers.")
        
        # Current Estimators: Name -> ID
        estimators = Estimator.query.all()
        # Create map: Name -> ID. Normalize name for better matching?
        estimator_map = {e.estimatorName.strip(): e.estimatorID for e in estimators}
        print(f"Loaded {len(estimator_map)} Estimators: {list(estimator_map.keys())}")
        
        # Sales Reps: Username -> ID
        sales_reps = User.query.filter(User.usertype_id == 2).all() # Assuming 2 is Sales Rep based on context? 
        # Or just getting all users to be safe if sales_agent strings map to usernames
        all_users = User.query.all()
        user_map = {u.username.strip().lower(): u.id for u in all_users}
        print(f"Loaded {len(user_map)} Users for Sales Rep mapping.")

        # 2. Connect to Legacy DB
        conn = get_legacy_connection()
        conn.row_factory = sqlite3.Row # Access columns by name
        cursor = conn.cursor()
        
        # Get Legacy Estimators Map (ID -> Name)
        print("Fetching Legacy Estimators...")
        cursor.execute("SELECT estimatorID, estimatorName FROM estimator")
        legacy_est_rows = cursor.fetchall()
        legacy_est_map = {row['estimatorID']: row['estimatorName'] for row in legacy_est_rows}
        
        # Get Legacy Customers Map (ID -> Code)
        print("Fetching Legacy Customers...")
        cursor.execute("SELECT id, customerCode FROM customer")
        legacy_cust_rows = cursor.fetchall()
        legacy_cust_map = {row['id']: row['customerCode'].strip().upper() for row in legacy_cust_rows if row['customerCode']}
        
        # 3. Fetch Bids
        print("Fetching Bids >= 8816...")
        cursor.execute("SELECT * FROM bid WHERE id >= 8816")
        bids = cursor.fetchall()
        print(f"Found {len(bids)} bids to import.")
        
        imported_count = 0
        skipped_count = 0
        
        for row in bids:
            bid_id = row['id']
            
            # Check if exists
            if Bid.query.get(bid_id):
                print(f"Bid {bid_id} already exists. Skipping.")
                skipped_count += 1
                continue
                
            # Map Customer
            legacy_cust_id = row['customer_id']
            cust_code = legacy_cust_map.get(legacy_cust_id)
            
            if not cust_code:
                print(f"Bid {bid_id}: Skipped - Legacy Customer ID {legacy_cust_id} not found in legacy map.")
                continue
                
            new_customer = customer_map.get(cust_code)
            if not new_customer:
                print(f"Bid {bid_id}: Skipped - Customer Code '{cust_code}' not found in new DB.")
                continue
                
            customer_id = new_customer.id
            
            # Map Estimator
            legacy_est_id = row['estimator_id']
            legacy_est_name = legacy_est_map.get(legacy_est_id)
            
            new_est_id = None
            est_note = ""
            
            if legacy_est_id:
                if legacy_est_name:
                     # Try to match by name
                     if legacy_est_name.strip() in estimator_map:
                         new_est_id = estimator_map[legacy_est_name.strip()]
                     else:
                         # No match (likely a Designer like Amy/Mike or old employee)
                         est_note = f"\n[Legacy Import: Assigned to {legacy_est_name}]"
                else:
                    est_note = f"\n[Legacy Import: Unknown Estimator ID {legacy_est_id}]"

            # Map Sales Rep (helper logic from customer)
            sales_rep_id = None
            if new_customer.sales_agent:
                # sales_agent in Customer is likely a username string?
                agent_username = new_customer.sales_agent.strip().lower()
                sales_rep_id = user_map.get(agent_username)
            
            # Parse Dates
            def parse_date(date_str):
                if not date_str: return None
                try:
                    # SQLite dates usually 'YYYY-MM-DD HH:MM:SS.ssssss' or 'YYYY-MM-DD'
                    if '.' in date_str:
                        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
                    elif len(date_str) > 10:
                        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    else:
                        return datetime.strptime(date_str, '%Y-%m-%d')
                except:
                    return None

            log_date = parse_date(row['log_date']) or datetime.utcnow()
            due_date = parse_date(row['due_date'])
            completion_date = parse_date(row['completion_date'])
            
            # Create Bid
            # Combine notes
            notes = (row['notes'] or "") + est_note
            
            new_bid = Bid(
                id=bid_id,
                plan_type=row['plan_type'],
                customer_id=customer_id,
                project_name=row['project_name'],
                estimator_id=new_est_id,
                sales_rep_id=sales_rep_id,
                status=row['status'],
                log_date=log_date,
                due_date=due_date,
                completion_date=completion_date,
                notes=notes,
                last_updated_by=row['last_updated_by'] or 'Legacy Import',
                last_updated_at=parse_date(row['last_updated_at'])
            )
            
            db.session.add(new_bid)
            imported_count += 1
            
        print(f"Committing {imported_count} bids...")
        db.session.commit()
        print("Done.")
        conn.close()

if __name__ == "__main__":
    import_legacy_bids()
