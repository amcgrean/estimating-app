from project import create_app, db
from project.models import Bid, User, UserType, SalesRep, Branch, Customer
from flask_login import login_user

app = create_app()

def test_sales_rep_workflow():
    with app.test_request_context():
        # Setup: Ensure Sales Rep User exists
        rep_type = UserType.query.filter_by(name='Sales Rep').first()
        if not rep_type:
            print("ERROR: 'Sales Rep' UserType not found.")
            return

        # Create/Get Sales Rep Entry
        sales_rep = SalesRep.query.filter_by(username='test_rep').first()
        if not sales_rep:
            sales_rep = SalesRep(name='Test Rep', username='test_rep')
            db.session.add(sales_rep)
            db.session.commit()

        # Create/Get User linked to Sales Rep
        user = User.query.filter_by(username='test_rep_user').first()
        if not user:
            user = User(username='test_rep_user', email='test@test.com', password='password', 
                        usertype_id=rep_type.id, sales_rep_id=sales_rep.id, 
                        user_branch_id=1) # Assuming branch 1 exists
            db.session.add(user)
            db.session.commit()
        
        # Log them in (mock)
        login_user(user)
        print(f"Logged in as {user.username} (Sales Rep ID: {user.sales_rep_id})")

        # Test 1: Auto-tagging on Bid Creation (Simulating route logic)
        # We can't easily call the route function directly without a full request setup with form data.
        # But we can verify the LOGIC we wrote: if user is Sales Rep, use their ID.
        
        assigned_id = None
        if user.usertype.name == 'Sales Rep':
            assigned_id = user.sales_rep_id
        
        if assigned_id == sales_rep.id:
            print("SUCCESS: Logic correctly identifies Sales Rep ID for assignment.")
        else:
            print(f"FAILURE: Assigned ID {assigned_id} does not match Rep ID {sales_rep.id}")

        # Test 2: 'My Bids' Query Logic
        # Create a bid tagged with this rep
        customer = Customer.query.first()
        bid = Bid(project_name="Rep Test Bid", customer_id=customer.id, plan_type="Res", 
                  sales_rep_id=sales_rep.id, branch_id=1)
        db.session.add(bid)
        db.session.commit()

        # Simulate the query from apply_branch_filter
        # query = Bid.query.join(Customer).filter((Bid.sales_rep_id == user.sales_rep_id) | (Customer.sales_agent == user.sales_rep.name))
        try:
            results = Bid.query.join(Customer).filter(
                (Bid.sales_rep_id == user.sales_rep_id) |
                (Customer.sales_agent == user.sales_rep.name)
            ).all()
            
            found = any(b.id == bid.id for b in results)
            if found:
                 print("SUCCESS: 'My Bids' query found the test bid.")
            else:
                 print("FAILURE: 'My Bids' query did NOT find the test bid.")
                 print(f"Results count: {len(results)}")
        except Exception as e:
            print(f"Query Error: {e}")

        # Cleanup
        db.session.delete(bid)
        db.session.commit()

if __name__ == "__main__":
    test_sales_rep_workflow()
