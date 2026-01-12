
import sys
import os
sys.path.append(os.getcwd())
from project import create_app, db
from project.models import Bid

def check_bid_query():
    app = create_app()
    with app.app_context():
        print("Attempting to query Bids...")
        try:
            bid = Bid.query.first()
            if bid:
                print(f"Successfully fetched bid ID: {bid.id}")
                # Access attributes to ensure they are loaded
                print(f"Project: {bid.project_name}")
                print(f"Bid Date: {bid.bid_date}")
                print(f"Notes: {bid.notes}")
                print("Bid query simulation SUCCESS.")
            else:
                print("No bids found (empty table), but query succeeded.")
        except Exception as e:
            print(f"Bid query simulation FAILED: {e}")

if __name__ == "__main__":
    check_bid_query()
