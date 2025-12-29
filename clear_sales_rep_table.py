from project import create_app, db
from project.models import SalesRep

def clear_sales_rep_table():
    try:
        # Create application context
        app = create_app()
        with app.app_context():
            # Clear the sales_rep table
            db.session.query(SalesRep).delete()
            db.session.commit()
            print("All entries from the sales_rep table have been deleted.")
            return True
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting entries from the sales_rep table: {e}")
        return False

if __name__ == "__main__":
    clear_sales_rep_table()
