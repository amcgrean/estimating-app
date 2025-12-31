
import os
import sys
import psycopg2
from urllib.parse import urlparse

# Add project root to path to find .env if needed, though we rely on os.environ
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to load .env manually if variable not set
if not os.environ.get('DATABASE_URL'):
    try:
        from dotenv import load_dotenv
        load_dotenv('.env')
        print("Loaded .env")
    except ImportError:
        print("dotenv not found")

def migrate():
    db_url = (
        os.environ.get("DATABASE_URL") 
        or os.environ.get("POSTGRES_URL") 
        or os.environ.get("SQLALCHEMY_DATABASE_URI")
    )
    if not db_url:
        print("ERROR: No DB URL found in env (checked DATABASE_URL, POSTGRES_URL, SQLALCHEMY_DATABASE_URI).")
        return

    # Fix postgres:// legacy scheme if present
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    print(f"Connecting to DB...")
    
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        columns = [
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
        
        for col, col_type in columns:
            print(f"Adding {col}...")
            try:
                cur.execute(f"ALTER TABLE bid ADD COLUMN IF NOT EXISTS {col} {col_type}")
                print(f"  Added/Checked {col}")
            except Exception as e:
                print(f"  Error adding {col}: {e}")
        
        conn.close()
        print("Migration complete.")
        
    except Exception as e:
        print(f"Connection/Migration failed: {e}")

if __name__ == "__main__":
    migrate()
