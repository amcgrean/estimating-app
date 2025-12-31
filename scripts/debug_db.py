import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project import create_app, db
from sqlalchemy import text

app = create_app()

def debug():
    with app.app_context():
        print("DEBUG: Starting connection...")
        try:
            conn = db.engine.connect()
            print("DEBUG: Connected.")
            
            print("DEBUG: Executing trivial query...")
            res = conn.execute(text("SELECT 1")).scalar()
            print(f"DEBUG: Result: {res}")
            
            print("DEBUG: Attempting ALTER...")
            conn.execute(text("ALTER TABLE bid ADD COLUMN IF NOT EXISTS bid_date TIMESTAMP"))
            conn.commit() # SQLAlchemy 2.0 style, or try/except
            print("DEBUG: ALTER successful.")
            
            conn.close()
        except Exception as e:
            print(f"DEBUG: Error details: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    debug()
