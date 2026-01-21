import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from project import create_app, db
from project.models import User, Customer, Branch, Bid, BidValue
from flask_login import login_user

app = create_app()
app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF for testing

with app.app_context():
    # Setup Data
    user = User.query.filter_by(username='amcgrean').first()
    if not user:
        print("User 'amcgrean' not found, picking first user.")
        user = User.query.first()
        
    customer = Customer.query.first()
    branch = Branch.query.first()
    
    if not user or not customer or not branch:
        print("Missing required test data (User/Customer/Branch). Aborting.")
        sys.exit(1)

    print(f"Testing as User: {user.username} (ID: {user.id})")
    
    # Create Test Client
    with app.test_client() as client:
        # Simulate Login
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            sess['_fresh'] = True

        # Payload
        data = {
            'project_name': 'E2E Test Bid Specs',
            'plan_type': 'Residential',
            'customer_id': customer.id,
            'branch_id': branch.branch_id,
            'sales_rep_id': 0, # Optional
            'estimator_id': 0, # Optional
            'notes': 'Automated Test',
            # DYNAMIC FIELD TEST
            'dynamic_field_5': 'Test Value Tyvek',
            'status': 'Incomplete'
        }
        
        print("Submitting Bid...")
        response = client.post('/add_bid', data=data, follow_redirects=True)
        
        # Check Outcome
        if response.status_code == 200:
            print("Submission processed (Result 200 OK - likely followed redirect to index).")
        else:
            print(f"Submission failed? Status: {response.status_code}")
            
        # Verify DB
        bid = Bid.query.filter_by(project_name='E2E Test Bid Specs').order_by(Bid.id.desc()).first()
        if bid:
            print(f"Bid Created! ID: {bid.id}")
            
            # Check Spec
            val = BidValue.query.filter_by(bid_id=bid.id, field_id=5).first()
            if val:
                print(f"SUCCESS: Found Spec Value: '{val.value}'")
                if val.value == 'Test Value Tyvek':
                    print("VERIFICATION PASSED: Data matches input.")
                else:
                     print("VERIFICATION FAILED: Data mismatch.")
                
                # Verify Retrieval in Manage Bid
                print("Verifying Manage Bid UI...")
                resp = client.get(f'/manage_bid/{bid.id}')
                if resp.status_code == 200:
                    content = resp.data.decode('utf-8')
                    if 'Test Value Tyvek' in content:
                        print("UI VERIFICATION PASSED: Value found in Manage Bid page.")
                    else:
                        print("UI VERIFICATION FAILED: Value NOT found in HTML.")
                        # print(content) # Debug
                else:
                    print(f"UI VERIFICATION FAILED: Status {resp.status_code}")

            else:
                print("FAILURE: No BidValue found for field_id=5.")
                
            # Cleanup
            print("Cleaning up test data...")
            BidValue.query.filter_by(bid_id=bid.id).delete()
            db.session.delete(bid)
            db.session.commit()
            print("Cleanup complete.")
            
        else:
            print("FAILURE: Bid was not found in database.")
            # validation errors?
            if b'Whoops!' in response.data:
                 print("Form Validation Errors detected in response.")
                 # rudimentary error extraction
                 lines = response.data.decode('utf-8').split('\n')
                 for line in lines:
                     if 'invalid-feedback' in line or 'alert-danger' in line or 'Whoops!' in line:
                         print(f"ERROR LINE: {line.strip()}")
                     if 'Not a valid choice' in line:
                         print(f"CHOICE ERROR: {line.strip()}")

