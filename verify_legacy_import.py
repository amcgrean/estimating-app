import sys
import os
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

from project import create_app, db
from project.models import Bid

def verify_import():
    app = create_app()
    with app.app_context():
        print(f"Using Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Check Total Bids
        total_bids = Bid.query.count()
        print(f"Total Bids in DB: {total_bids}")
        
        # Check Bids >= 8816
        legacy_bids = Bid.query.filter(Bid.id >= 8816).order_by(Bid.id.asc()).all()
        print(f"Bids with ID >= 8816: {len(legacy_bids)}")
        
        if legacy_bids:
            print("\n--- Sample Imported Bids ---")
            for b in legacy_bids[:5]:
                est_name = b.estimator.estimatorName if b.estimator else "None"
                sales_name = b.sales_rep.username if b.sales_rep else "None"
                print(f"ID: {b.id}, Project: {b.project_name}, Est: {est_name} ({b.estimator_id}), Sales: {sales_name}, Notes: {b.notes[:50]}...")

if __name__ == "__main__":
    verify_import()
