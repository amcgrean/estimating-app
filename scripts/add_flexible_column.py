import sqlite3
import os

# Define the database path
db_path = os.path.join('instance', 'bids.db')

def add_flexible_bid_date_column():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if column already exists
        cursor.execute("PRAGMA table_info(bid)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'flexible_bid_date' not in columns:
            print("Adding 'flexible_bid_date' column to 'bid' table...")
            cursor.execute("ALTER TABLE bid ADD COLUMN flexible_bid_date BOOLEAN DEFAULT 0")
            print("Column added successfully.")
        else:
            print("'flexible_bid_date' column already exists.")

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    add_flexible_bid_date_column()
