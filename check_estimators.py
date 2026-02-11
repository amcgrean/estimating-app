import sys
import os
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

from project import create_app, db
from project.models import Estimator, Designer

def check_estimators():
    app = create_app()
    with app.app_context():
        print(f"Using Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        print("\n--- Current Estimators ---")
        estimators = Estimator.query.all()
        for e in estimators:
            print(f"ID: {e.estimatorID}, Name: {e.estimatorName}")
            
        print("\n--- Current Designers ---")
        designers = Designer.query.all()
        for d in designers:
            print(f"ID: {d.id}, Name: {d.name}")

if __name__ == "__main__":
    check_estimators()
