from project import create_app, db
from project.models import User, SalesRep

app = create_app()

def inspect_austinb():
    with app.app_context():
        user = User.query.filter_by(username='austinb').first()
        if not user:
            print("User 'austinb' not found.")
            return

        print(f"User: {user.username}, ID: {user.id}")
        print(f"UserType ID: {user.usertype_id}")
        print(f"Sales Rep ID: {user.sales_rep_id}")

        if user.sales_rep_id:
            rep = SalesRep.query.get(user.sales_rep_id)
            if rep:
                print(f"Linked Sales Rep: {rep.name} (ID: {rep.id})")
            else:
                print(f"ERROR: Sales Rep with ID {user.sales_rep_id} does not exist.")
        else:
            print("User has NO sales_rep_id set.")

        # Check if 'austinb' exists in SalesRep table by username/name potentially not linked?
        potential_reps = SalesRep.query.filter(SalesRep.name.ilike('%austin%')).all()
        print("Potential Sales Rep matches in table:")
        for r in potential_reps:
            print(f" - {r.name} (ID: {r.id}, Username: {r.username})")

if __name__ == "__main__":
    inspect_austinb()
