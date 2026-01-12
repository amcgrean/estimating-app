from project import create_app, db
from project.models import Bid, Customer, Branch
from datetime import datetime

app = create_app()

def test_flexible_bid_date():
    with app.app_context():
        # Get a customer and branch for the bid (assuming they exist from previous steps or default data)
        # Using branch 3 (Coralville) as per recent context
        branch = Branch.query.filter_by(branch_id=3).first()
        if not branch:
             branch = Branch.query.first()
             
        customer = Customer.query.first()
        if not customer:
            print("No customers found. Cannot Create Bid.")
            return

        print(f"Using Customer: {customer.name}, Branch: {branch.branch_name}")

        # Create a test bid
        test_bid = Bid(
            plan_type="Residential",
            customer_id=customer.id,
            project_name="Flexible Date Test Project",
            status="Incomplete",
            branch_id=branch.branch_id,
            bid_date=datetime.utcnow(),
            flexible_bid_date=True,  # Testing the new field
            notes="Testing flexible date flag."
        )

        try:
            db.session.add(test_bid)
            db.session.commit()
            print(f"Bid created with ID: {test_bid.id}")

            # Verify retrieval
            retrieved_bid = Bid.query.get(test_bid.id)
            if retrieved_bid.flexible_bid_date:
                print("SUCCESS: flexible_bid_date is True.")
            else:
                print("FAILURE: flexible_bid_date is False or None.")
                print(f"Value: {retrieved_bid.flexible_bid_date}")

            # Clean up
            db.session.delete(test_bid)
            db.session.commit()
            print("Test bid deleted.")

        except Exception as e:
            print(f"An error occurred: {e}")
            db.session.rollback()

if __name__ == "__main__":
    test_flexible_bid_date()
