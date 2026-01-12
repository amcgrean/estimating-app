from project import create_app, db
from project.models import User, SalesRep

app = create_app()

def fix_austinb():
    with app.app_context():
        user = User.query.filter_by(username='austinb').first()
        if not user:
            print("User 'austinb' not found.")
            return

        if user.sales_rep_id:
            print(f"User already has sales_rep_id: {user.sales_rep_id}")
            return

        rep = SalesRep.query.filter_by(username='austinb').first()
        if not rep:
             print("Sales Rep 'austinb' not found to link.")
             return
        
        print(f"Linking User {user.username} (ID: {user.id}) to Sales Rep {rep.name} (ID: {rep.id})")
        user.sales_rep_id = rep.id
        db.session.commit()
        print("Done.")

if __name__ == "__main__":
    fix_austinb()
