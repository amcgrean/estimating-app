import sys
import os
import csv
import datetime
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

from project import create_app, db
from project.models import Customer, Designer

def verify_import():
    app = create_app()
    with app.app_context():
        print(f"Using Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Load all valid IDs
        valid_customer_ids = {c.id for c in Customer.query.all()}
        valid_designer_ids = {d.id for d in Designer.query.all()}
        
        print(f"Valid Customer IDs: {len(valid_customer_ids)}")
        print(f"Valid Designer IDs: {valid_designer_ids}")
        
        csv_file = r"project\import_templates\historical_designs_template.csv"
        
        print(f"Verifying {csv_file}...")
        
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            row_count = 0
            errors = 0
            
            for row in reader:
                row_count += 1
                
                # Check Customer ID
                cust_id_str = row.get('Customer ID (Int)')
                if cust_id_str:
                    try:
                        cust_id = int(cust_id_str)
                        if cust_id not in valid_customer_ids:
                            print(f"Row {row_count}: Invalid Customer ID {cust_id}")
                            errors += 1
                    except ValueError:
                        print(f"Row {row_count}: Malformed Customer ID '{cust_id_str}'")
                        errors += 1
                else:
                    print(f"Row {row_count}: Missing Customer ID")
                    errors += 1
                    
                # Check Designer ID
                des_id_str = row.get('Designer ID (Int)')
                if des_id_str:
                    try:
                        des_id = int(des_id_str)
                        if des_id not in valid_designer_ids:
                            print(f"Row {row_count}: Invalid Designer ID {des_id}")
                            errors += 1
                    except ValueError:
                         # It's possible for Designer to be empty if not assigned?
                         # The CSV header says (Int), let's assume it should be an int.
                         # If it's empty string, is that allowed?
                         if des_id_str.strip() == '':
                             pass # Maybe allow empty?
                         else:
                            print(f"Row {row_count}: Malformed Designer ID '{des_id_str}'")
                            errors += 1
                
                # Check Date
                date_str = row.get('Log Date (YYYY-MM-DD)')
                if date_str:
                    try:
                        # Format is M/D/YYYY in the file preview (e.g. 2/9/2026)
                        # The header says YYYY-MM-DD but the data is M/D/YYYY.
                        # I need to handle both or checking consistent format.
                        # Let's try parsing M/D/YYYY first as that's what I saw.
                        datetime.datetime.strptime(date_str, '%m/%d/%Y')
                    except ValueError:
                        try:
                             datetime.datetime.strptime(date_str, '%Y-%m-%d')
                        except ValueError:
                            print(f"Row {row_count}: Invalid Date Format '{date_str}'")
                            errors += 1
                            
        print(f"Checked {row_count} rows.")
        
        with open('verification_report.txt', 'w', encoding='utf-8') as report:
            if errors == 0:
                msg = "SUCCESS: Validation passed. Ready to upload."
                print(msg)
                report.write(msg)
            else:
                msg = f"FAILURE: Found {errors} errors. See console for details."
                print(msg)
                report.write(msg + "\n")
                # I should have collected errors in a list to write them here.
                # Let's modify the script to collect errors.

    # Rerunning logic with error collection
    errors_list = []
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        row_count = 0
        for row in reader:
            row_count += 1
            # Check Customer ID
            cust_id_str = row.get('Customer ID (Int)')
            if cust_id_str:
                try:
                    cust_id = int(cust_id_str)
                    if cust_id not in valid_customer_ids:
                        errors_list.append(f"Row {row_count}: Invalid Customer ID {cust_id}")
                except ValueError:
                    errors_list.append(f"Row {row_count}: Malformed Customer ID '{cust_id_str}'")
            else:
                errors_list.append(f"Row {row_count}: Missing Customer ID")

            # Check Designer ID
            des_id_str = row.get('Designer ID (Int)')
            if des_id_str:
                try:
                    des_id = int(des_id_str)
                    if des_id not in valid_designer_ids:
                        errors_list.append(f"Row {row_count}: Invalid Designer ID {des_id}")
                except ValueError:
                     if des_id_str.strip() != '':
                        errors_list.append(f"Row {row_count}: Malformed Designer ID '{des_id_str}'")
            
            # Check Date
            date_str = row.get('Log Date (YYYY-MM-DD)')
            if date_str:
                try:
                    datetime.datetime.strptime(date_str, '%m/%d/%Y')
                except ValueError:
                    try:
                         datetime.datetime.strptime(date_str, '%Y-%m-%d')
                    except ValueError:
                        errors_list.append(f"Row {row_count}: Invalid Date Format '{date_str}'")

    with open('verification_report.txt', 'w', encoding='utf-8') as report:
        if not errors_list:
            report.write("SUCCESS: Validation passed. Ready to upload.")
        else:
            report.write(f"FAILURE: Found {len(errors_list)} errors.\n")
            for err in errors_list[:20]: # Show first 20 errors
                report.write(err + "\n")
            if len(errors_list) > 20:
                report.write(f"... and {len(errors_list) - 20} more errors.")

if __name__ == "__main__":
    verify_import()
