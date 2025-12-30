
from project import db, create_app
from project.models import Customer
from sqlalchemy import text

app = create_app()
with app.app_context():
    print("--- Making Customers Global ---")
    
    # Set branch_id to NULL for all customers
    try:
        db.session.execute(text('UPDATE customer SET branch_id = NULL'))
        db.session.commit()
        print("All customers are now global (Branch ID set to NULL).")
    except Exception as e:
        print(f"Error updating customers: {e}")
        db.session.rollback()
