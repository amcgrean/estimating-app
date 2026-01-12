import sqlite3
import os

# Define the database path
db_path = os.path.join('instance', 'bids.db')

def add_sales_rep_id_column():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if column already exists
        cursor.execute("PRAGMA table_info(bid)")
        columns = [info[1] for info in cursor.fetchall()]
        
        column_name = 'sales_rep_id'
        
        if column_name not in columns:
            print(f"Adding '{column_name}' column to 'bid' table...")
            # We add it as nullable integer first. 
            # SQLite doesn't strictly enforce FKs in ALTER TABLE ADD COLUMN unless enabled, 
            # and usually it's just an integer column that we map in SQLAlchemy.
            cursor.execute(f"ALTER TABLE bid ADD COLUMN {column_name} INTEGER")
            print("Column added successfully.")
        else:
            print(f"'{column_name}' column already exists.")

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    add_sales_rep_id_column()
