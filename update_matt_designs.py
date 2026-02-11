import sys
import os
import csv
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

from project import create_app, db
from project.models import Designer, Design

def update_matt_designs():
    app = create_app()
    with app.app_context():
        print(f"Using Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Verify Matt exists
        matt = Designer.query.get(4)
        if not matt:
            print("Error: Designer ID 4 (Matt Hackett) not found in database.")
            return

        print(f"Target Designer: {matt.name} (ID: {matt.id})")
        
        csv_file = r"project\import_templates\historical_designs_template.csv"
        updated_count = 0
        skipped_count = 0 # Not found in DB
        already_correct_count = 0
        
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                designer_id_str = row.get('Designer ID (Int)')
                
                # Only process rows for Designer ID 4
                if designer_id_str and designer_id_str.strip() == '4':
                    plan_number = row.get('Plan Number')
                    
                    design = Design.query.filter_by(planNumber=plan_number).first()
                    
                    if design:
                        if design.designer_id != 4:
                            old_designer_name = design.designer.name if design.designer else "None"
                            design.designer_id = 4
                            print(f"Updated Plan {plan_number}: {old_designer_name} -> {matt.name}")
                            updated_count += 1
                        else:
                            already_correct_count += 1
                    else:
                        print(f"Warning: Plan {plan_number} not found in database (skipped import previously?)")
                        skipped_count += 1
                        
            db.session.commit()
            print("\n--- Update Complete ---")
            print(f"Updated: {updated_count}")
            print(f"Already Correct: {already_correct_count}")
            print(f"Not Found (Skipped): {skipped_count}")

if __name__ == "__main__":
    update_matt_designs()
