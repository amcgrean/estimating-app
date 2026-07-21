import os
import sys
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

try:
    from project import create_app, db
    from project.models import Customer, Job
    
    app = create_app()
    with app.app_context():
        cust_count = Customer.query.count()
        job_count = Job.query.count()
        print(f"Customer count: {cust_count}")
        print(f"Job count: {job_count}")
        
        # Check for specific customer from CSV
        cust = Customer.query.filter_by(customerCode='ZZDE1000').first()
        if cust:
            print(f"Customer ZZDE1000 found: {cust.name}")
            jobs = Job.query.filter_by(customer_id=cust.id).all()
            print(f"Job count for ZZDE1000: {len(jobs)}")
        else:
            print("Customer ZZDE1000 NOT found.")

        # Check for QUOT2025
        cust_quot = Customer.query.filter_by(customerCode='QUOT2025').first()
        if cust_quot:
             print(f"Customer QUOT2025 found: {cust_quot.name}")
        else:
             print("Customer QUOT2025 NOT found.")

        # Check for recent jobs
        recent_jobs = Job.query.order_by(Job.id.desc()).limit(5).all()
        print("\nLatest 5 Jobs in DB:")
        for j in recent_jobs:
            print(f"ID: {j.id}, Ref: {j.job_reference}, Name: {j.job_name}, Status: {j.status}")

except Exception as e:
    import traceback
    traceback.print_exc()
