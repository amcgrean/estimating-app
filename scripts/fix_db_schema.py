
import sys
import os
sys.path.append(os.getcwd())

from project import create_app, db
from sqlalchemy import text, inspect

def fix_schema():
    app = create_app()
    with app.app_context():
        # Ensure db.create_all() is called to be safe
        db.create_all()

        inspector = inspect(db.engine)
        tables = inspector.get_table_names()

        # Check missing columns in Customer table
        if 'customer' in tables:
            cols = [c['name'] for c in inspector.get_columns('customer')]
            print(f"Current Customer cols: {cols}")
            
            missing_cols = {
                'sales_agent': 'VARCHAR(100)',
                'branch_id': 'INTEGER REFERENCES branch(branch_id)', 
                # Add any others from inspection if needed
            }

            for col_name, col_type in missing_cols.items():
                if col_name not in cols:
                    print(f"Adding {col_name} to customer...")
                    with db.engine.connect() as conn:
                        try:
                            conn.execute(text(f"ALTER TABLE customer ADD COLUMN {col_name} {col_type}"))
                            conn.commit()
                            print(f"Added {col_name}.")
                        except Exception as e:
                            print(f"Failed to add {col_name}: {e}")
                else:
                    print(f"Column {col_name} already exists.")

        print("Customer schema fix complete.")

if __name__ == "__main__":
    fix_schema()
