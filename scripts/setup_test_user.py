
import sys
import os
sys.path.append(os.getcwd())
from project import create_app, db
from project.models import User, Branch
from werkzeug.security import generate_password_hash

def setup_test_user():
    app = create_app()
    with app.app_context():
        # 1. Find a user in a different branch (e.g., ID 3 = Coralville)
        # We look for someone who isn't 'admin'
        target_branch_id = 3 # Coralville
        
        user = User.query.filter(User.user_branch_id == target_branch_id).first()
        
        if not user:
            print(f"No user found in Branch {target_branch_id}. Finding a candidate to move...")
            # Pick a random user that isn't admin
            user = User.query.filter(User.username != 'admin').first()
            if user:
                print(f"Moving user '{user.username}' to Branch {target_branch_id}...")
                user.user_branch_id = target_branch_id
                db.session.commit()
            else:
                print("No suitable users found to modify.")
                return

        if user:
            # 2. Reset password so we can login
            print(f"User selected: {user.username} (Branch ID: {user.user_branch_id})")
            user.set_password('password123')
            db.session.commit()
            print(f"Password for '{user.username}' reset to 'password123'")

if __name__ == "__main__":
    setup_test_user()
