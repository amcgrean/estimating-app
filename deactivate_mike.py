from project import create_app, db
from project.models import User

app = create_app()

with app.app_context():
    # Find user 'mikew' (ID 68 from previous check)
    user = User.query.filter_by(username='mikew').first()
    if user:
        if user.is_active:
            print(f"Deactivating user: {user.username} (ID: {user.id})")
            user.is_active = False
            db.session.commit()
            print("User deactivated successfully. He should no longer appear in designer options.")
        else:
            print(f"User {user.username} is already inactive.")
    else:
        print("User 'mikew' not found.")
