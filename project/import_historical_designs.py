import sys
import os
import csv
import datetime
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

from project import create_app, db
from project.models import Customer, Designer, Design, User

# Plan Number,Plan Name,Customer ID (Int),Project Address,Contractor,Log Date (YYYY-MM-DD),Designer ID (Int),Status,Plan Description,Notes

def import_designs():
    app = create_app()
    with app.app_context():
        print(f"Using Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        csv_file = r"project\import_templates\historical_designs_template.csv"
        
        imported_count = 0
        skipped_count = 0
        
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                plan_number = row.get('Plan Number')
                
                # Check for duplicate plan number
                existing = Design.query.filter_by(planNumber=plan_number).first()
                if existing:
                    print(f"Skipping duplicate Plan Number: {plan_number}")
                    skipped_count += 1
                    continue

                try:
                    # Parse Data
                    customer_id = int(row.get('Customer ID (Int)'))
                    
                    # Designer
                    designer_id_str = row.get('Designer ID (Int)')
                    designer_id = int(designer_id_str) if designer_id_str and designer_id_str.strip() else None
                    
                    # Date
                    date_str = row.get('Log Date (YYYY-MM-DD)')
                    log_date = None
                    if date_str:
                        try:
                            log_date = datetime.datetime.strptime(date_str, '%m/%d/%Y')
                        except ValueError:
                            try:
                                log_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
                            except ValueError:
                                print(f"Warning: Could not parse date {date_str} for plan {plan_number}")
                    
                    # Create Design
                    new_design = Design(
                        planNumber=plan_number,
                        plan_name=row.get('Plan Name'),
                        customer_id=customer_id,
                        project_address=row.get('Project Address'),
                        contractor=row.get('Contractor'),
                        log_date=log_date,
                        designer_id=designer_id,
                        status=row.get('Status') or 'Active',
                        plan_description=row.get('Plan Description'),
                        notes=row.get('Notes'),
                        # Set default branch? 
                        # We don't have branch in CSV. 
                        # We can try to infer from customer or user, 
                        # but for now let's leave None or default to 1 if required?
                        # Model allows nullable branch_id.
                    )
                    
                    # Infer branch from customer if possible
                    customer = Customer.query.get(customer_id)
                    if customer and customer.branch_id:
                        new_design.branch_id = customer.branch_id
                    
                    db.session.add(new_design)
                    imported_count += 1
                    
                    if imported_count % 50 == 0:
                        db.session.commit()
                        print(f"Committed {imported_count} designs...")

                except Exception as e:
                    print(f"Error importing row {row}: {e}")
                    skipped_count += 1
            
            db.session.commit()
            print(f"Import Complete.")
            print(f"Imported: {imported_count}")
            print(f"Skipped: {skipped_count}")

if __name__ == "__main__":
    import_designs()
