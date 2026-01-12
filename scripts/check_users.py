
import sys
import os
sys.path.append(os.getcwd())

from project import create_app, db
from project.models import User
from sqlalchemy import text

def check_users():
    app = create_app()
    with app.app_context():
        print(f"DB URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        try:
            user_count = User.query.count()
            print(f"User count: {user_count}")
            users = User.query.all()
            for u in users:
                print(f"User: {u.username} (ID: {u.id})")
        except Exception as e:
            print(f"Error querying users: {e}")
            # Try raw SQL if model fails
            try:
                with db.engine.connect() as conn:
                    result = conn.execute(text("SELECT count(*) FROM user"))
                    print(f"Raw SQL count: {result.scalar()}")
            except Exception as e2:
                print(f"Raw SQL failed: {e2}")

if __name__ == "__main__":
    check_users()
