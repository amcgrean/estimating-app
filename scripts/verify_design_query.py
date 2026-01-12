
import sys
import os
sys.path.append(os.getcwd())
from project import create_app, db
from project.models import Design

def check_design_query():
    app = create_app()
    with app.app_context():
        print("Attempting to query Designs...")
        try:
            design = Design.query.first()
            if design:
                print(f"Successfully fetched design ID: {design.id}")
                # Access attributes to ensure they are loaded
                print(f"Plan Name: {design.plan_name}")
                # Check for potentially new columns if any
                print(f"Status: {design.status}")
                print("Design query simulation SUCCESS.")
            else:
                print("No designs found.")
        except Exception as e:
            print(f"Design query simulation FAILED: {e}")

if __name__ == "__main__":
    check_design_query()
