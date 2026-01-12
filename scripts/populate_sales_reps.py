import csv
import os
from project import create_app, db
from project.models import SalesRep

app = create_app()

def populate_sales_reps():
    csv_file_path = 'sales_agents.csv'
    
    if not os.path.exists(csv_file_path):
        print(f"Error: {csv_file_path} not found.")
        return

    with app.app_context():
        print("Starting Sales Rep population...")
        
        with open(csv_file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            updated = 0
            
            for row in reader:
                name = row.get('name', '').strip()
                username = row.get('username', '').strip()
                
                if not name or not username:
                    print(f"Skipping invalid row: {row}")
                    continue
                
                # specific clean up for the row 'Carla Filloon,carlaf  lamas' if it was malformed in cat output
                # The cat output showed: Carla Filloon,carlaf  lamas
                # Wait, "carlaf  lamas"? That looks like "carlaflamas" maybe? Or two fields?
                # The header is name,username.
                # "Carla Filloon" is name. "carlaf  lamas" might be username "carlaflamas"?
                # Let's just trust the CSV parser.
                
                existing = SalesRep.query.filter_by(username=username).first()
                if existing:
                    if existing.name != name:
                        existing.name = name
                        updated += 1
                        print(f"Updated: {username} -> {name}")
                else:
                    new_rep = SalesRep(name=name, username=username)
                    db.session.add(new_rep)
                    count += 1
                    print(f"Added: {name} ({username})")
            
            try:
                db.session.commit()
                print(f"\nSuccess! Added {count} new reps, Updated {updated} existing reps.")
            except Exception as e:
                db.session.rollback()
                print(f"Error committing to database: {e}")

if __name__ == "__main__":
    populate_sales_reps()
