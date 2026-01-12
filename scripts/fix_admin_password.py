
import sys
import os
sys.path.append(os.getcwd())
from project import create_app, db
from project.models import User

def reset_admin_password():
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(username='admin').first()
        if user:
            print(f"Resetting password for: {user.username}")
            # Uses the model's set_password (which now uses bcrypt)
            user.set_password('password123') 
            db.session.commit()
            print("Password reset to 'password123' using bcrypt.")
        else:
            print("Admin user not found.")

if __name__ == "__main__":
    reset_admin_password()
