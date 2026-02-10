import sys
import os
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

from project import create_app, db
from project.models import User, Estimator, Design

def inspect_data():
    app = create_app()
    with app.app_context():
        print(f"Using Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        usernames = ['amyl', 'mikeb', 'mikew']
        print(f"Checking for users: {usernames}")
        
        for username in usernames:
            user = User.query.filter_by(username=username).first()
            if user:
                print(f"User found: {user.username}, ID: {user.id}, EstimatorID: {user.estimatorID}, DesignerID: {user.designer_id}, IsDesigner: {user.is_designer}")
            else:
                print(f"User NOT found: {username}")

            # Check Estimator record
            est = Estimator.query.filter_by(estimatorUsername=username).first()
            if est:
                print(f"Estimator found: {est.estimatorName}, ID: {est.estimatorID}, Type: {est.type}")
            else:
                print(f"Estimator NOT found for username: {username}")

        print(f"Total Designs in DB: {Design.query.count()}")
        print(f"Total Estimators in DB: {Estimator.query.count()}")
        print(f"Total Users in DB: {User.query.count()}")

if __name__ == "__main__":
    inspect_data()
