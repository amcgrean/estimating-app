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

        # 2. Map existing branches (code -> id)
        branches = Branch.query.all()
        branch_map = {b.branch_code: b.branch_id for b in branches}
        print(f"Loaded {len(branch_map)} branches.")
        
        # 3. Import Customers
        customers_csv = os.path.join('project', 'import files', 'customers.csv')
        job_csv = os.path.join('project', 'import files', 'jobs_20260205.csv')
        
        print("Importing Customers...")
        cust_map = {} # Map cust_code -> cust_id for jobs
        count_new = 0
        count_updated = 0
        
        with open(customers_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            # Expected Headers: cust_code,shipto_name,sales_agent_1,agent_default_branch
            
            for row in reader:
                code = row.get('cust_code')
                name = row.get('shipto_name')
                agent = row.get('sales_agent_1')
                branch_code = row.get('agent_default_branch')
                
                if not code:
                    continue
                    
                branch_id = branch_map.get(branch_code)
                
                customer = Customer.query.filter_by(customerCode=code).first()
                if customer:
                    customer.name = name
                    customer.sales_agent = agent
                    if branch_id:
                        customer.branch_id = branch_id
                    count_updated += 1
                    cust_map[code] = customer.id
                else:
                    new_cust = Customer(
                        customerCode=code,
                        name=name,
                        sales_agent=agent,
                        branch_id=branch_id
                    )
                    db.session.add(new_cust)
                    db.session.flush() # Get ID
                    cust_map[code] = new_cust.id
                    count_new += 1
                
                if (count_new + count_updated) % 500 == 0:
                    db.session.commit()
                    print(f"Processed {count_new + count_updated} customers...")
        
        db.session.commit()
        print(f"Customer Import Complete. New: {count_new}, Updated: {count_updated}")

        # 4. Import Jobs
        print("Importing Jobs...")
        count_jobs = 0
        with open(job_csv, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            # Headers: Account Number,Job Reference,Job Name,Job Status
            
            for row in reader:
                acct_num = row.get('Account Number')
                job_ref = row.get('Job Reference')
                job_name = row.get('Job Name')
                status = row.get('Job Status')
                
                # STRICT VALIDATION: Only import if customer exists
                if not acct_num or acct_num not in cust_map:
                    continue
                    
                cust_id = cust_map[acct_num]
                
                # Check if job exists
                job = Job.query.filter_by(customer_id=cust_id, job_reference=job_ref).first()
                
                if job:
                    job.job_name = job_name
                    job.status = status
                else:
                    job = Job(
                        customer_id=cust_id,
                        job_reference=job_ref,
                        job_name=job_name,
                        status=status
                    )
                    db.session.add(job)
                
                count_jobs += 1
                if count_jobs % 1000 == 0:
                    db.session.commit()
                    print(f"Processed {count_jobs} jobs...")
        
        db.session.commit()
        print(f"Import Complete. Processed {count_jobs} jobs.")

if __name__ == "__main__":
    import_data()
