
from project import db, create_app
from project.models import Customer, Branch
from sqlalchemy import or_

app = create_app()
with app.app_context():
    print("--- Customer Branch Check ---")
    total_customers = Customer.query.count()
    print(f"Total customers: {total_customers}")
    
    customers_no_branch = Customer.query.filter(Customer.branch_id == None).count()
    print(f"Customers with no branch: {customers_no_branch}")
    
    branches = Branch.query.all()
    for b in branches:
        count = Customer.query.filter(Customer.branch_id == b.branch_id).count()
        print(f"Branch '{b.branch_name}' (ID: {b.branch_id}): {count} customers")
        
        # Test the filter used in the route
        filtered_count = Customer.query.filter(or_(Customer.branch_id == b.branch_id, Customer.branch_id == None)).count()
        print(f"  -> Filtered count for this branch (incl. NULL): {filtered_count}")

    # Specific check for branch 0 (All)
    print("Branch 0 (All) should show all customers.")
