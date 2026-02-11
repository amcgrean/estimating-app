import sys
import os
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

from project import create_app, db
from project.models import Bid

def verify_fix():
    app = create_app()
    with app.app_context():
        print(f"Using Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        bids = Bid.query.filter(Bid.id >= 8816).all()
        print(f"Checking {len(bids)} imported bids...")
        
        branch_20gr_count = 0
        designer_note_count = 0
        est_none_count = 0
        
        for b in bids:
            if b.branch and b.branch.branch_code == '20GR':
                branch_20gr_count += 1
            
            if b.notes and "Legacy Import: Assigned to" in b.notes:
                designer_note_count += 1
                print(f"  Bid {b.id} has designer note: {b.notes}")
                
            if b.estimator_id is None:
                est_none_count += 1
                
        print(f"Bids with Branch 20GR: {branch_20gr_count}/{len(bids)}")
        print(f"Bids with Designer Notes: {designer_note_count}")
        print(f"Bids with Evaluator=None: {est_none_count}")

if __name__ == "__main__":
    verify_fix()
