import os
import sys
import csv
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

from project import create_app, db
from project.models import Customer, Job, Branch

def import_data():
    app = create_app()
    with app.app_context():
        print(f"Using Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # 1. Update Schema Manually (Safety Check)
        with db.engine.connect() as conn:
            # Check for Job table
            try:
                conn.execute(text("SELECT 1 FROM job LIMIT 1"))
            except Exception:
                print("Job table not found. Creating tables...")
                db.create_all()
        
            # Check for columns in Bid/Design
            # This logic is a bit complex for raw SQL across different DBs (SQLite/Postgres)
            # relying on db.create_all() for new tables or manual alter for existing
            pass

        # Ensure Job Table Exists (db.create_all should handle it if models are imported)
        db.create_all()
        print("Database schema ensured.")

        # 2. Cache Branches
        branches = Branch.query.all()
        if not branches:
            print("No branches found in DB.")
        branch_map = {b.branch_code: b.branch_id for b in branches}
        print(f"Loaded {len(branch_map)} branches.")
        
        # 3. Import Customers
        customers_csv = os.path.join('project', 'import files', 'customers.csv')
        job_csv = os.path.join('project', 'import files', 'jobs.csv')
        
        print("Importing Customers...")
        cust_map = {c.customerCode: c.id for c in Customer.query.all()} # Pre-load map
        
        new_customers = []
        
        with open(customers_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                code = row.get('cust_code')
                name = row.get('shipto_name')
                agent = row.get('sales_agent_1')
                branch_code = row.get('agent_default_branch')
                
                if not code or code in cust_map:
                    continue # Skip existing for speed
                    
                branch_id = branch_map.get(branch_code)
                new_customers.append({
                    'customerCode': code,
                    'name': name,
                    'sales_agent': agent,
                    'branch_id': branch_id
                })
        
        if new_customers:
            print(f"Bulk inserting {len(new_customers)} customers...")
            db.session.bulk_insert_mappings(Customer, new_customers)
            db.session.commit()
            print("Customers Committed.")
            
            # Refresh map
            cust_map = {c.customerCode: c.id for c in Customer.query.all()}

        # 4. Import Jobs
        print("Importing Jobs...")
        
        existing_jobs = set()
        jobs_query = db.session.query(Job.customer_id, Job.job_reference).all()
        for j in jobs_query:
            existing_jobs.add((j.customer_id, j.job_reference))
            
        new_jobs = []
        with open(job_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                acct_num = row.get('Account Number')
                job_ref = row.get('Job Reference')
                job_name = row.get('Job Name')
                status = row.get('Job Status')
                
                if not acct_num or acct_num not in cust_map:
                    continue
                
                cust_id = cust_map[acct_num]
                
                if (cust_id, job_ref) in existing_jobs:
                    continue
                
                new_jobs.append({
                    'customer_id': cust_id,
                    'job_reference': job_ref,
                    'job_name': job_name,
                    'status': status
                })
        
        if new_jobs:
            print(f"Bulk inserting {len(new_jobs)} jobs...")
            # Chunking to avoid memory issues
            chunk_size = 2000
            for i in range(0, len(new_jobs), chunk_size):
                chunk = new_jobs[i:i + chunk_size]
                db.session.bulk_insert_mappings(Job, chunk)
                db.session.commit()
                print(f"Committed chunk {i}...")

        print(f"Import Complete.")

if __name__ == "__main__":
    import_data()
