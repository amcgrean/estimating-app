import os
import sys
import csv

# Add project root to path
sys.path.append(os.getcwd())

from project import create_app, db
from project.models import Customer, Branch
from sqlalchemy import inspect, text

def import_customers():
    # Use standard create_app to pick up User's Env Vars
    app = create_app()
    
    with app.app_context():
        print(f"Using Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Try raw connection
        try:
            with db.engine.connect() as conn:
                conn.execute(text("SELECT 1 FROM customer LIMIT 1"))
            print("Successfully connected to 'customer' table.")
        except Exception as e:
            print(f"CRITICAL ERROR: Could not select from 'customer' table.")
            print(f"This implies the database at '{app.config['SQLALCHEMY_DATABASE_URI']}' is empty of app data or not the one used by the running app.")
            print(f"Error details: {e}")
            return

        inspector = inspect(db.engine)
        
        # Check for sales_agent column
        columns = [c['name'] for c in inspector.get_columns('customer')]
        if 'sales_agent' not in columns:
            print("Adding sales_agent column to customer table...")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE customer ADD COLUMN sales_agent VARCHAR(150)"))
                conn.commit()
            print("Column added.")
        else:
            print("'sales_agent' column already exists.")
        
        # Load Branches
        # Need to handle if Branch table is empty?
        branches_query = Branch.query.all()
        if not branches_query:
            print("WARNING: Branch table is empty. No branches will be mapped.")
        
        branches = {b.branch_code: b.branch_id for b in branches_query}
        print(f"Loaded {len(branches)} branches.")
        
        # Read CSV
        csv_path = 'customers.csv'
        if not os.path.exists(csv_path):
            print(f"CSV file not found: {csv_path}")
            return
            
        count_new = 0
        count_updated = 0
        
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            print(f"CSV Headers detected: {reader.fieldnames}")
            for row in reader:
                code = row.get('cust_code')
                name = row.get('shipto_name')
                agent = row.get('default_agent') # Maps to sales_agent
                branch_code = row.get('default_branch')
                
                if not code:
                    continue
                    
                branch_id = branches.get(branch_code)
                
                customer = Customer.query.filter_by(customerCode=code).first()
                if customer:
                    customer.sales_agent = agent
                    if branch_id:
                        customer.branch_id = branch_id
                    count_updated += 1
                else:
                    new_cust = Customer(
                        customerCode=code,
                        name=name,
                        sales_agent=agent,
                        branch_id=branch_id
                    )
                    db.session.add(new_cust)
                    count_new += 1
                    
                if (count_new + count_updated) % 100 == 0:
                    db.session.commit()
                    print(f"Processed {count_new + count_updated} records...")
                    
        db.session.commit()
        print(f"Import Complete. New: {count_new}, Updated: {count_updated}")

if __name__ == "__main__":
    import_customers()
