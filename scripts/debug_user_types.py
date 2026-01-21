import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from project import create_app, db
from project.models import User, UserType

app = create_app()
with app.app_context():
    # List all User Types
    print("--- User Types ---")
    user_types = UserType.query.all()
    for ut in user_types:
        print(f"ID: {ut.id}, Name: '{ut.name}'")

    # List a few users and their types to identify the current user's role
    print("\n--- Sample Users ---")
    users = User.query.limit(20).all()
    for u in users:
        print(f"User: {u.username}, Type: '{u.usertype.name}' (ID: {u.usertype_id})")
