from project import create_app, db
from project.models import Bid, Customer, Design, EWP, Project, Branch

def migrate_to_grimes():
    app = create_app()
    with app.app_context():
        # Confirm Grimes branch exists
        grimes = Branch.query.get(1)
        if not grimes or grimes.branch_name != 'Grimes':
            print("Error: Grimes branch (ID: 1) not found or naming mismatch.")
            return

        print(f"Starting migration to branch: {grimes.branch_name} (ID: 1)")

        # List of models to update
        models = [Bid, Customer, Design, EWP, Project]
        
        for model in models:
            # Count records with NULL branch_id
            count = model.query.filter(model.branch_id == None).count()
            if count > 0:
                print(f"Updating {count} records in {model.__name__}...")
                model.query.filter(model.branch_id == None).update({model.branch_id: 1}, synchronize_session=False)
            else:
                print(f"No NULL branch_id records found in {model.__name__}.")

        try:
            db.session.commit()
            print("Migration completed successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {str(e)}")

if __name__ == "__main__":
    migrate_to_grimes()
