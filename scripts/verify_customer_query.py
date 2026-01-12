
import sys
import os
sys.path.append(os.getcwd())
from project import create_app, db
from project.models import Customer

def check_customer_query():
    app = create_app()
    with app.app_context():
        try:
            print("Querying Customer with sales_agent...")
            # Simple query to trigger load
            c = Customer.query.first()
            if c:
                print(f"Customer Found: {c.name}")
                print(f"Sales Agent: {c.sales_agent}")
                print("Customer query simulation SUCCESS.")
            else:
                print("No customers found, but query succeeded.")
        except Exception as e:
            print(f"Customer query simulation FAILED: {e}")

if __name__ == "__main__":
    check_customer_query()
