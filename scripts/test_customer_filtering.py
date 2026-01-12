
import sys
import os
sys.path.append(os.getcwd())
from project import create_app, db
from project.models import Customer, Branch

def test_filtering():
    app = create_app()
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            # 1. Identify distinct branches and customers
            # Find a customer specific to a branch
            # Let's see if we have data to test
            branches = Branch.query.all()
            print(f"Branches: {[b.branch_name for b in branches]}")
            
            # Let's check Grimes (1) vs Coralville (3)
            # Find a customer IN Grimes
            c_grimes = Customer.query.filter_by(branch_id=1).first()
            # Find a customer IN Coralville
            c_coral = Customer.query.filter_by(branch_id=3).first()
            
            if not c_grimes or not c_coral:
                print("WARNING: Insufficient data to test filtering (need customers in specific branches).")
                # Try to create temp query
                count_1 = Customer.query.filter_by(branch_id=1).count()
                count_3 = Customer.query.filter_by(branch_id=3).count()
                print(f"Grimes Customers: {count_1}")
                print(f"Coralville Customers: {count_3}")
            else:
                print(f"Testing Grimes Customer: {c_grimes.name}")
                print(f"Testing Coralville Customer: {c_coral.name}")

            # 2. Login as admin
            client.post('/login', data={'username': 'admin', 'password': 'password123'}, follow_redirects=True)
            
            # 3. Request Add Bid page for Grimes (ID 1)
            resp_1 = client.get('/add_bid?branch_id=1')
            html_1 = resp_1.data.decode('utf-8')
            
            # 4. Request Add Bid page for Coralville (ID 3)
            resp_3 = client.get('/add_bid?branch_id=3')
            html_3 = resp_3.data.decode('utf-8')
            
            print("\n--- RESULTS ---")
            
            # Check Grimes Page
            has_grimes_c = c_grimes.name in html_1 if c_grimes else False
            has_coral_c = c_coral.name in html_1 if c_coral else False
            print(f"Branch 1 (Grimes) Page:")
            print(f"  - Contains Grimes Customer ({c_grimes.name if c_grimes else 'N/A'}): {has_grimes_c}")
            print(f"  - Contains Coralville Customer ({c_coral.name if c_coral else 'N/A'}): {has_coral_c}")
            
            # Check Coralville Page
            has_grimes_c_3 = c_grimes.name in html_3 if c_grimes else False
            has_coral_c_3 = c_coral.name in html_3 if c_coral else False
            print(f"Branch 3 (Coralville) Page:")
            print(f"  - Contains Grimes Customer: {has_grimes_c_3}")
            print(f"  - Contains Coralville Customer: {has_coral_c_3}")

            if has_grimes_c and not has_coral_c and has_coral_c_3 and not has_grimes_c_3:
                print("\nSUCCESS: Filtering is working correctly server-side.")
            else:
                print("\nFAILURE: Filtering logic does not match expectations.")

if __name__ == "__main__":
    test_filtering()
