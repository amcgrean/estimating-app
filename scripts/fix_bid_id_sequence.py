
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project import create_app, db
from sqlalchemy import text

app = create_app()

def fix_bid_sequence():
    with app.app_context():
        print("Checking max Bid ID...")
        try:
            # 1. Get the current maximum ID
            result = db.session.execute(text("SELECT MAX(id) FROM bid"))
            max_id = result.scalar()
            
            if max_id is None:
                print("No bids found in table.")
                max_id = 0
            
            print(f"Current Max ID in table: {max_id}")
            
            # 2. Reset the sequence
            # We use pg_get_serial_sequence to dynamically get the sequence name associated with bid.id
            print("Resetting ID sequence...")
            sql = text("SELECT setval(pg_get_serial_sequence('bid', 'id'), :new_val)")
            
            # setval sets the *last* value, so next value will be new_val + 1? 
            # or sets the *next* value if is_called is false?
            # Standard: setval(seq, val) sets the current value. The next nextval() returns val+1.
            # So we set it to max_id.
            
            db.session.execute(sql, {'new_val': max_id})
            db.session.commit()
            
            print(f"Success! Sequence reset to {max_id}. The next bid will have ID {max_id + 1}.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error fixing sequence: {e}")

if __name__ == "__main__":
    fix_bid_sequence()
