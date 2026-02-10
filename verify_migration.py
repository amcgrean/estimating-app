import sys
import os
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

from project import create_app, db
from project.models import Designer, User, Design, Estimator

def verify_migration():
    app = create_app()
    with app.app_context():
        print("Verifying Migration...")
        
        # 1. Check Designer Table
        designers = Designer.query.all()
        print(f"Designers found: {len(designers)}")
        for d in designers:
            print(f" - {d.id}: {d.name} ({d.username})")
            
        # 2. Check User Records (is_designer)
        users = User.query.filter_by(is_designer=True).all()
        print(f"Users marked as Designer: {len(users)}")
        for u in users:
            print(f" - {u.username} (Designer ID: {u.designer_id})")
            
        # 3. Check Design Records
        designs = Design.query.all()
        print(f"Total Designs: {len(designs)}")
        valid_links = 0
        invalid_links = 0
        assigned_designs = 0
        
        for d in designs:
            if d.designer_id:
                assigned_designs += 1
                # Check if designer exists
                designer = Designer.query.get(d.designer_id)
                if designer:
                    valid_links += 1
                else:
                    invalid_links += 1
                    print(f"WARNING: Design {d.id} has invalid designer_id: {d.designer_id}")
        
        print(f"Designs with assigned designer: {assigned_designs}")
        print(f"Valid links to Designer table: {valid_links}")
        print(f"Invalid links: {invalid_links}")
        
        if invalid_links == 0 and len(designers) > 0:
            print("SUCCESS: Migration appears successful.")
        else:
            print("WARNING: Issues check output.")

if __name__ == "__main__":
    verify_migration()
