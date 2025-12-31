import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project import create_app, db
from project.models import Bid
app = create_app()

def check():
    with app.app_context():
        print(f"Model: {Bid}")
        print(f"Tablename: {Bid.__tablename__}")
        try:
            count = Bid.query.count()
            print(f"Row count: {count}")
        except Exception as e:
            print(f"Query failed: {e}")

if __name__ == "__main__":
    check()
