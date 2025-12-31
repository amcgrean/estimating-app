import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project import create_app, db
from sqlalchemy import text

app = create_app()

def add_columns():
    with app.app_context():
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"Connecting to database: {db_uri.split('@')[-1] if '@' in db_uri else db_uri}...")
        
        print("Using db.session for migration...")
        try:
            # We must commit the transaction for ALTER TABLE to stick
            # But session handles transactions.
            
            new_columns = [
                ('bid_date', 'TIMESTAMP'),
                ('include_specs', 'BOOLEAN DEFAULT FALSE'),
                ('framing_notes', 'TEXT'),
                ('siding_notes', 'TEXT'),
                ('deck_notes', 'TEXT'),
                ('trim_notes', 'TEXT'),
                ('window_notes', 'TEXT'),
                ('door_notes', 'TEXT'),
                ('shingle_notes', 'TEXT'),
                ('plan_filename', 'VARCHAR(255)'),
                ('email_filename', 'VARCHAR(255)')
            ]

            for col_name, col_type in new_columns:
                print(f"Adding {col_name}...")
                sql = text(f"ALTER TABLE bid ADD COLUMN IF NOT EXISTS {col_name} {col_type}")
                db.session.execute(sql)
            
            db.session.commit()
            print("Successfully updated table schema via session.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error updating schema: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    add_columns()
