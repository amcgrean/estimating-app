from project import create_app, db
from sqlalchemy import text

app = create_app()

def fix_migration_head():
    with app.app_context():
        # Check current revision
        result = db.session.execute(text("SELECT version_num FROM alembic_version"))
        current_rev = result.scalar()
        print(f"Current DB Revision: {current_rev}")
        
        # The revision that became a dead end because we re-pointed the history
        DEAD_END_REV = 'b2c3d4e5f6a7' 
        # The revision it *should* come from now (which allows upgrade to c3d4e...)
        NEW_PARENT_REV = 'd9319f6e738f'
        
        if current_rev == DEAD_END_REV:
            print(f"Detected broken dead-end revision {DEAD_END_REV}.")
            print(f"Updating alembic_version to {NEW_PARENT_REV} to re-link history...")
            
            # Update the version number
            db.session.execute(text(f"UPDATE alembic_version SET version_num = '{NEW_PARENT_REV}' WHERE version_num = '{DEAD_END_REV}'"))
            db.session.commit()
            
            print(f"Successfully updated revision to {NEW_PARENT_REV}.")
            print("You can now run 'flask db upgrade'.")
        else:
            print(f"Current revision is not {DEAD_END_REV}. No fix applied.")
            print("If upgrade is still failing, check 'check_migration_status.py' output.")

if __name__ == '__main__':
    fix_migration_head()
