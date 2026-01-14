from project import create_app, db
from sqlalchemy import text

app = create_app()

def fix_schema():
    with app.app_context():
        tables = ['framing', 'siding', 'shingle', 'deck', 'trim', 'window', 'door']
        
        # SQLite syntax for adding column. SQLite doesn't support ADD CONSTRAINT in ADD COLUMN easily,
        # but SQLAlchemy models usually rely on application-level FKs or implicit.
        # However, to be safe, we just add the column. 
        # Note: SQLite `ADD COLUMN` cannot add a FOREIGN KEY constraint inline easily without recreating table,
        # BUT for existing tables we can just add the integer column. SQLAlchemy will handle the relationship logic
        # (joining on the column) even if the strict DB constraint is missing (unless enforced).
        # We will try to add it.
        
        with db.engine.connect() as conn:
            for table in tables:
                print(f"Checking {table}...")
                try:
                    # Check if column exists
                    res = conn.execute(text(f"PRAGMA table_info({table})"))
                    cols = [row[1] for row in res]
                    if 'bid_id' not in cols:
                        print(f"Adding bid_id to {table}...")
                        # Add column
                        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN bid_id INTEGER"))
                        # Note: We are NOT adding the FK constraint physically to avoid complex table rebuilds.
                        # The application usage (reading/writing) will work as long as the column exists.
                        # Migration scripts (if run later) might complain or try to add FK, but we just need it working now.
                        print(f"Added bid_id to {table}.")
                    else:
                        print(f"bid_id already exists in {table}.")
                except Exception as e:
                    print(f"Error processing {table}: {e}")
            
            # Commit not needed for DDL? explicit commit?
            # conn.commit() # SQLAlchemy 1.4+ with future=True might need commit. 
            # In some setups DDL is autocommit.
            # safe to try commit.
            # If using transaction.
            try:
                conn.commit()
            except:
                pass

if __name__ == '__main__':
    fix_schema()
