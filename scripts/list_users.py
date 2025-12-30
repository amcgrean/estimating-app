from project import create_app, db
from project.models import User

app = create_app()
with app.app_context():
    users = User.query.all()
    for u in users:
        print(f"Username: {u.username}, ID: {u.id}, IsActive: {u.is_active}")
