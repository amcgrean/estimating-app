import csv
import argparse
import sys
import os
from datetime import datetime
from sqlalchemy import func

# Add parent directory to path so we can import 'project'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project import create_app, db
from project.models import Bid

def parse_date(date_str):
    if not date_str or date_str.lower() == 'none' or date_str.strip() == '':
        return None
    try:
        # Try full timestamp format first
        # Example: 2024-07-26 17:03:03.23 or 2024-07-26 17:03:03
        if '.' in date_str:
             return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
             # Fallback to just date
             return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            print(f"Warning: Could not parse date: {date_str}")
            return None

def sync_bids(csv_path, commit=False):
    app = create_app()
    with app.app_context():
        print(f"Reading CSV from: {csv_path}")
        
        try:
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except Exception as e:
            print(f"Error reading CSV: {e}")
            return

        print(f"Found {len(rows)} rows in CSV.")
        
        added = 0
        updated = 0
        skipped = 0
        
        # Mapping CSV headers to Model attributes
        # Based on typical CSV dumps and model fields
        field_map = {
            'id': 'id',
            'plan_type': 'plan_type',
            'customer_id': 'customer_id',
            'sales_rep_id': 'sales_rep_id',
            'project_name': 'project_name',
            'estimator_id': 'estimator_id',
            'status': 'status',
            'log_date': 'log_date',
            'due_date': 'due_date',
            'completion_date': 'completion_date',
            'bid_date': 'bid_date',
            'flexible_bid_date': 'flexible_bid_date',
            'include_specs': 'include_specs',
            'include_framing': 'include_framing',
            'include_siding': 'include_siding',
            'include_shingle': 'include_shingle', # Note: CSV might say include_shingles (plural) or singular. Model is singular.
            'include_deck': 'include_deck',
            'include_trim': 'include_trim',
            'include_window': 'include_window',
            'include_door': 'include_door',
            'framing_notes': 'framing_notes',
            'siding_notes': 'siding_notes',
            'deck_notes': 'deck_notes',
            'trim_notes': 'trim_notes',
            'window_notes': 'window_notes',
            'door_notes': 'door_notes',
            'shingle_notes': 'shingle_notes',
            'plan_filename': 'plan_filename',
            'email_filename': 'email_filename',
            'notes': 'notes',
            'last_updated_by': 'last_updated_by',
            'last_updated_at': 'last_updated_at',
            'branch_id': 'branch_id'
        }

        # Date fields that need parsing
        date_fields = ['log_date', 'due_date', 'completion_date', 'bid_date', 'last_updated_at']
        
        # Boolean fields
        bool_fields = [
            'flexible_bid_date', 'include_specs', 'include_framing', 'include_siding', 
            'include_shingle', 'include_deck', 'include_trim', 'include_window', 'include_door'
        ]

        for row in rows:
            bid_id = row.get('id')
            if not bid_id:
                continue
            
            try:
                bid_id = int(bid_id)
                bid = Bid.query.get(bid_id)
                
                is_new = False
                if not bid:
                    bid = Bid(id=bid_id)
                    is_new = True
                
                changes = []
                
                for csv_header, model_attr in field_map.items():
                    if csv_header not in row:
                        continue
                        
                    val = row[csv_header]
                    
                    # Handle empty strings as None
                    if val == '':
                        val = None
                    
                    # Special handling for types
                    if model_attr in date_fields and val:
                        val = parse_date(val)
                    elif model_attr in bool_fields:
                        if val is None:
                            val = False
                        else:
                            val = str(val).lower() in ('true', '1', 't', 'yes', 'y')
                    elif model_attr == 'estimator_id':
                        if not val:
                            val = None
                        else:
                            try:
                                val = int(float(val))
                            except:
                                val = None
                    elif model_attr == 'branch_id':
                        if not val:
                            val = None
                        else:
                            try:
                                val = int(float(val))
                            except:
                                val = None
                    elif model_attr == 'customer_id':
                        if not val:
                            continue 
                        try:
                            val = int(float(val))
                        except:
                            continue

                    # Set attribute
                    current_val = getattr(bid, model_attr)
                    
                    if current_val != val:
                        if isinstance(current_val, datetime) and isinstance(val, datetime):
                            if current_val.replace(tzinfo=None) != val.replace(tzinfo=None):
                                setattr(bid, model_attr, val)
                                changes.append(f"{model_attr}: {current_val} -> {val}")
                        else:
                            setattr(bid, model_attr, val)
                            changes.append(f"{model_attr}: {current_val} -> {val}")

                if is_new:
                    # Validate required fields
                    if not bid.project_name:
                         bid.project_name = "Unknown Project"
                         changes.append("project_name set to default")
                    
                    if not bid.customer_id:
                         raise ValueError("Missing customer_id for new bid")

                    db.session.add(bid)

                if changes:
                    status_msg = "NEW" if is_new else "UPDATE"
                    print(f"[{status_msg}] Bid {bid_id}:")
                    for c in changes:
                        print(f"  - {c}")
                    
                    if is_new:
                        added += 1
                    else:
                        updated += 1
                else:
                    skipped += 1
            
            except Exception as e:
                print(f"Error processing Bid {bid_id}: {e}")
                db.session.rollback()
                continue

        print(f"\nSummary:")
        print(f"  Added: {added}")
        print(f"  Updated: {updated}")
        print(f"  Skipped (No changes): {skipped}")

        if commit:
            print("\nCommitting changes to database...")
            try:
                db.session.commit()
                # Reset sequences if needed (Postgres specific)
                if added > 0:
                   print("Resetting primary key sequence...")
                   db.session.execute(func.setval('bid_id_seq', func.max(Bid.id)))
                   db.session.commit()
                print("Done.")
            except Exception as e:
                db.session.rollback()
                print(f"Error committing: {e}")
        else:
            print("\nDRY RUN: No changes committed. Use --commit to apply.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sync Bids from CSV to DB')
    parser.add_argument('--csv', default='bid.csv', help='Path to CSV file')
    parser.add_argument('--commit', action='store_true', help='Commit changes to DB')
    
    args = parser.parse_args()
    
    csv_path = os.path.join(os.getcwd(), args.csv)
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
    else:
        sync_bids(csv_path, commit=args.commit)
