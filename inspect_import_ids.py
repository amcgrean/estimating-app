import sys
import os
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

from project import create_app, db
from project.models import Designer, Estimator, Design

def inspect_data():
    app = create_app()
    with app.app_context():
        print(f"Using Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        with open('debug_ids_output.txt', 'w', encoding='utf-8') as f:
            f.write("--- Designers ---\n")
            designers = Designer.query.all()
            for d in designers:
                f.write(f"ID: {d.id}, Name: {d.name}, Username: {d.username}\n")
                
            f.write("\n--- Estimators ---\n")
            estimators = Estimator.query.all()
            for e in estimators:
                f.write(f"ID: {e.estimatorID}, Name: {e.estimatorName}, Username: {e.estimatorUsername}\n")

            f.write("\n--- Imported Designs (Sample) ---\n")
            plans_to_check = ['1026-26', '1027-26', '1025-26', '1379-20'] 
            for plan in plans_to_check:
                d = Design.query.filter_by(planNumber=plan).first()
                if d:
                    designer_name = d.designer.name if d.designer else "None"
                    f.write(f"Plan: {d.planNumber}, DesignerID: {d.designer_id}, Designer: {designer_name}\n")
                else:
                    f.write(f"Plan: {plan} NOT FOUND\n")
            
            # Also check for designs with ID 6, 7, 8 (Old Estimator IDs)
            f.write("\n--- Checking for Old Estimator IDs (6, 7, 8) in Design.designer_id ---\n")
            for old_id in [6, 7, 8]:
                count = Design.query.filter_by(designer_id=old_id).count()
                f.write(f"Designs with designer_id={old_id}: {count}\n")
                
        print("Debug output written to debug_ids_output.txt")

if __name__ == "__main__":
    inspect_data()
