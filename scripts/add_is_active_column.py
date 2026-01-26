
import sys
import os
from sqlalchemy import create_engine, text

# Add project to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project import create_app, db

def add_is_active_column():
    app = create_app()
    with app.app_context():
        # Get DB URI from config or env
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        print(f"Connecting to database: {db_uri}")
        
        engine = create_engine(db_uri)
        
        with engine.connect() as conn:
            # Check if column exists (simple check by trying to select it, or just alter table and catch error if needed)
            # Better to just try add it. 
            
            print("Attempting to add 'is_active' column to 'bid_field' table...")
            
            # SQLite syntax is slightly different from Postgres for some ALTERs, but ADD COLUMN is standardish
            # EXCEPT SQLite doesn't support adding NOT NULL without DEFAULT in same statement sometimes?
            # Also Postgres needs specific syntax.
            
            # Detection logic
            is_sqlite = 'sqlite' in db_uri
            is_postgres = 'postgresql' in db_uri
            
            try:
                if is_sqlite:
                    # SQLite supports ADD COLUMN
                    conn.execute(text("ALTER TABLE bid_field ADD COLUMN is_active BOOLEAN DEFAULT 1 NOT NULL"))
                else:
                    # Postgres
                    conn.execute(text("ALTER TABLE bid_field ADD COLUMN is_active BOOLEAN DEFAULT TRUE NOT NULL"))
                    
                print("Column 'is_active' added successfully.")
            except Exception as e:
                print(f"Migration failed (Column might already exist?): {e}")

            if not is_sqlite:
                # Commit for postgres (autocommit might not be on)
                conn.commit()
                
if __name__ == "__main__":
    add_is_active_column()
