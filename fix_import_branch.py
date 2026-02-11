import sys
import os
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

from project import create_app, db
from project.models import Bid, Branch

def fix_import():
    app = create_app()
    with app.app_context():
        print(f"Using Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # 1. Find Branch 20GR
        branch_20gr = Branch.query.filter_by(branch_code='20GR').first()
        if not branch_20gr:
            print("Error: Branch '20GR' not found.")
            return
            
        print(f"Found Branch: {branch_20gr.branch_name} (ID: {branch_20gr.branch_id}, Code: {branch_20gr.branch_code})")
        
        # 2. Update Bids >= 8816
        bids = Bid.query.filter(Bid.id >= 8816).all()
        print(f"Found {len(bids)} imported bids to update.")
        
        updated_count = 0
        for b in bids:
            b.branch_id = branch_20gr.branch_id
            updated_count += 1
            
        db.session.commit()
        print(f"Updated {updated_count} bids with branch_id = {branch_20gr.branch_id}")

        # 3. Check for 'Designer' notes to clarify user concern
        print("\n--- Bids with 'Legacy Import' Notes (Designer assignments) ---")
        designer_bids = Bid.query.filter(Bid.id >= 8816, Bid.notes.like('%Legacy Import: Assigned to%')).count()
        print(f"Total bids assigned to Legacy Designers (Amy, Mike, etc.): {designer_bids}")
        

if __name__ == "__main__":
    fix_import()
