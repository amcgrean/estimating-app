
import sys
import os
sys.path.append(os.getcwd())
from project import create_app, db
from project.models import User

def check_login_query():
    app = create_app()
    with app.app_context():
        print("Attempting to query User by username='admin'...")
        try:
            user = User.query.filter_by(username='admin').first()
            if user:
                print(f"Successfully fetched user: {user.username}")
                # Access attributes to ensure they are loaded
                print(f"ID: {user.id}")
                print(f"Created At: {user.created_at}")
                print(f"Updated At: {user.updated_at}")
                print("Login query simulation SUCCESS.")
            else:
                print("User 'admin' not found.")
        except Exception as e:
            print(f"Login query simulation FAILED: {e}")

if __name__ == "__main__":
    check_login_query()
