import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from project import create_app, db
from project.models import User, UserType

app = create_app()
with app.app_context():
    # Check Admin types
    admin_types = UserType.query.filter(UserType.name.like("Admin%")).all()
    print(f"Admin Types: {[ut.name for ut in admin_types]}")
    
    # Check User amcgrean
    u = User.query.filter_by(username='amcgrean').first()
    if u:
        print(f"User amcgrean: {u.usertype.name}")
    else:
        print("User amcgrean not found.")
