
import sys
import os
sys.path.append(os.getcwd())

from project import create_app, db
from project.models import User, Bid, Customer, Design, Branch
from sqlalchemy import text

def check_db_stats():
    app = create_app()
    with app.app_context():
        print(f"DB URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        try:
            counts = {
                "User": User.query.count(),
                "Bid": Bid.query.count(),
                "Customer": Customer.query.count(),
                "Design": Design.query.count(),
                "Branch": Branch.query.count(),
            }
            for model, count in counts.items():
                print(f"{model} count: {count}")
                
            # Sample data
            if counts["Customer"] > 0:
                print(f"Sample Customer: {Customer.query.first().name}")
        except Exception as e:
            print(f"Error querying DB: {e}")
            try:
                msg = str(e)
                if "no such table" in msg:
                    print(f"Missing table detected: {msg}")
            except:
                pass

if __name__ == "__main__":
    check_db_stats()
