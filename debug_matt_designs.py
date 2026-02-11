import sys
import os
import csv
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

from project import create_app, db
from project.models import Designer, Design

def debug_matt():
    app = create_app()
    with app.app_context():
        print(f"Using Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # 1. Check Designer 4
        d4 = Designer.query.get(4)
        if d4:
            print(f"Designer ID 4 found: {d4.name} ({d4.username})")
        else:
            print("Designer ID 4 NOT FOUND in Designer table.")
            
        # 2. Check Designs with designer_id = 4
        count_d4 = Design.query.filter_by(designer_id=4).count()
        print(f"Designs in DB with designer_id=4: {count_d4}")
        
        # 3. Check CSV for Designer ID 4
        csv_file = r"project\import_templates\historical_designs_template.csv"
        csv_count_4 = 0
        plans_for_4 = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    did = row.get('Designer ID (Int)')
                    if did and did.strip() == '4':
                        csv_count_4 += 1
                        plans_for_4.append(row.get('Plan Number'))
        except Exception as e:
            print(f"Error reading CSV: {e}")
            
        print(f"Rows in CSV with Designer ID 4: {csv_count_4}")
        if plans_for_4:
            print(f"Sample Plans for Designer 4: {plans_for_4[:5]}")
            
            # Check if these specific plans exist and what their designer_id is
            print("\nChecking a few plans from CSV in DB:")
            for plan in plans_for_4[:5]:
                d = Design.query.filter_by(planNumber=plan).first()
                if d:
                    d_name = d.designer.name if d.designer else "None"
                    print(f"  Plan {plan}: DB Designer ID = {d.designer_id} ({d_name})")
                else:
                    print(f"  Plan {plan}: Not found in DB")

if __name__ == "__main__":
    debug_matt()
