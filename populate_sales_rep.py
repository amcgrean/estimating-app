from project import create_app, db
from project.models import User, SalesRep

def populate_sales_rep():
    app = create_app()
    with app.app_context():
        try:
            # Clear the sales_rep table
            db.session.query(SalesRep).delete()
            db.session.commit()

            # Create SalesRep entries and update User entries
            users = User.query.all()
            for user in users:
                if not SalesRep.query.filter_by(username=user.username).first():
                    # Create a new SalesRep entry
                    sales_rep = SalesRep(name=user.username, username=user.username)
                    db.session.add(sales_rep)
                    db.session.commit()  # Commit to get the new sales_rep.id

                    # Update the user's sales_rep_id to the new SalesRep id
                    user.sales_rep_id = sales_rep.id
                    db.session.commit()

            print("SalesRep table populated and User entries updated successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error populating the sales_rep table: {e}")

if __name__ == "__main__":
    populate_sales_rep()
