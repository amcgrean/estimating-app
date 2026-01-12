
import sys
import os
sys.path.append(os.getcwd())

from project import create_app, db
from project.models import User, Branch

def check_branches():
    app = create_app()
    with app.app_context():
        # Get count of users with NULL branch
        missing_branch_count = User.query.filter(User.user_branch_id == None).count()
        total_users = User.query.count()
        
        print(f"Total Users: {total_users}")
        print(f"Users missing branch: {missing_branch_count}")
        
        if missing_branch_count > 0:
            print("Fixing missing branches (Defaulting to Grimes - ID 1)...")
            # Batch update
            User.query.filter(User.user_branch_id == None).update({User.user_branch_id: 1})
            db.session.commit()
            print("Fixed.")
        else:
            print("All users have a valid branch.")

        # Print a sample
        print("\nSample Users:")
        for u in User.query.limit(5).all():
            branch_name = u.branch.branch_name if u.branch else "None"
            print(f"- {u.username}: {branch_name} (ID: {u.user_branch_id})")

if __name__ == "__main__":
    check_branches()
