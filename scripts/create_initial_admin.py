
import sys
import os
sys.path.append(os.getcwd())

from project import create_app, db
from project.models import User, UserType, UserSecurity
from werkzeug.security import generate_password_hash
from sqlalchemy import text

def create_initial_admin():
    app = create_app()
    with app.app_context():
        # 1. Ensure UserTypes exist
        print("Checking UserTypes...")
        user_types = [
            (1, 'Administrator'), (2, 'Estimator'), (3, 'Designer'),
            (4, 'Picker'), (5, 'Manager'), (6, 'EWP'),
            (7, 'Service Tech'), (8, 'Installer'), (9, 'Door Builder'),
            (10, 'Sales Rep'), (11, 'Customer')
        ]
        
        for ut_id, ut_name in user_types:
            existing = UserType.query.get(ut_id)
            if not existing:
                print(f"Creating UserType: {ut_name}")
                new_ut = UserType(id=ut_id, name=ut_name)
                db.session.add(new_ut)
            else:
                 if existing.name != ut_name:
                     existing.name = ut_name
        
        db.session.commit()

        # 2. Ensure UserSecurity exists for Administrator (ID 1)
        print("Checking UserSecurity for Admin...")
        admin_security = UserSecurity.query.filter_by(user_type_id=1).first()
        if not admin_security:
            print("Creating Admin Security Profile...")
            admin_security = UserSecurity(
                user_type_id=1,
                admin=True, estimating=True, bid_request=True, design=True,
                ewp=True, service=True, install=True, picking=True,
                work_orders=True, dashboards=True,
                security_10=True, security_11=True, security_12=True,
                security_13=True, security_14=True, security_15=True,
                security_16=True, security_17=True, security_18=True,
                security_19=True, security_20=True
            )
            db.session.add(admin_security)
            db.session.commit()
        else:
            print("Admin Security Profile exists.")

        # 3. Create Admin User
        print("Checking for 'admin' user...")
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            print("Creating 'admin' user...")
            admin_user = User(
                username='admin',
                email='admin@example.com',
                usertype_id=1, # Administrator
                is_active=True,
                is_admin=True,
                user_branch_id=1 # Default to Grimes
            )
            admin_user.set_password('password123')
            db.session.add(admin_user)
            db.session.commit()
            print("User 'admin' created with password 'password123'")
        else:
            print("User 'admin' already exists. Resetting password to 'password123'...")
            admin_user.set_password('password123')
            db.session.add(admin_user)
            db.session.commit()
            print("User 'admin' password reset.")

if __name__ == "__main__":
    create_initial_admin()
