import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project import create_app, db
from sqlalchemy import inspect

app = create_app()

def check():
    with app.app_context():
        try:
            print("Inspecting tables...")
            insp = inspect(db.engine)
            tables = insp.get_table_names()
            print(f"Tables: {tables}")
            
            if 'bid' in tables:
                cols = [c['name'] for c in insp.get_columns('bid')]
                print(f"Columns in 'bid': {cols}")
            elif 'bids' in tables:
                cols = [c['name'] for c in insp.get_columns('bids')]
                print(f"Columns in 'bids': {cols}")
            
            if 'bid_date' in cols:
                print("SUCCESS: bid_date exists.")
            else:
                print("FAILURE: bid_date MISSING.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    check()
