
import sys
import os
sys.path.append(os.getcwd())

from flask import Flask
from flask_bcrypt import Bcrypt
from sqlalchemy import create_engine, text

def reset_admin_sql():
    # Setup minimal app for bcrypt
    app = Flask(__name__)
    bcrypt = Bcrypt(app)
    
    # DB Connection
    db_url = "sqlite:///instance/bids.db"
    engine = create_engine(db_url)
    
    password_hash = bcrypt.generate_password_hash("password123").decode('utf-8')
    
    with engine.connect() as conn:
        # Check if admin exists
        current_admin = conn.execute(text("SELECT username FROM user WHERE username='admin'")).fetchone()
        
        if current_admin:
            print("Updating 'admin' password...")
            # Try updating 'password' column first
            try:
                conn.execute(text("UPDATE user SET password = :pwd WHERE username='admin'"), {"pwd": password_hash})
                conn.commit()
                print("Updated 'password' column.")
            except Exception as e:
                print(f"Failed to update 'password' column: {e}")
                # Try 'password_hash' column
                try:
                    conn.execute(text("UPDATE user SET password_hash = :pwd WHERE username='admin'"), {"pwd": password_hash})
                    conn.commit()
                    print("Updated 'password_hash' column.")
                except Exception as e2:
                    print(f"Failed to update 'password_hash' column: {e2}")
        else:
            print("User 'admin' does not exist. Inserting...")
            # Insert logic is complex due to many columns, skipping for now as backup likely has admin
            # Or try insertion with minimal columns
            try:
                conn.execute(text("""
                    INSERT INTO user (username, email, password, usertype_id, active) 
                    VALUES ('admin', 'admin@example.com', :pwd, 1, 1)
                """), {"pwd": password_hash})
                conn.commit()
                print("Inserted 'admin' user.")
            except Exception as e:
                print(f"Insert failed: {e}")

if __name__ == "__main__":
    reset_admin_sql()
