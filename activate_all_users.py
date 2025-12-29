from project import create_app, db
from project.models import User

def activate_all_users():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        if not users:
            print("No users found in the database.")
            return

        for user in users:
            user.is_active = True
            print(f"Activating user: {user.username}")

        db.session.commit()

        activated_users = User.query.filter_by(is_active=True).all()
        if len(activated_users) == len(users):
            print(f"All users have been activated successfully.")
        else:
            print(f"Some users might not have been activated. Activated users: {len(activated_users)} / {len(users)}")

if __name__ == '__main__':
    activate_all_users()
