
from project import db, create_app
from project.models import User, Branch

app = create_app()
with app.app_context():
    print("--- User Branch Check ---")
    users = User.query.filter(User.username.in_(['jasonr', 'amcgrean', 'admin_username'])).all()
    for u in users:
        branch_name = u.branch.branch_name if u.branch else "None"
        print(f"User: {u.username}, Branch: {branch_name} (ID: {u.user_branch_id})")
