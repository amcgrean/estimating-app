import sqlite3
import bcrypt

# Connect to the database
conn = sqlite3.connect('/home/amcgrean/mysite/instance/bids.db')
cursor = conn.cursor()

# Select all users
cursor.execute("SELECT id FROM user")
users = cursor.fetchall()

# Update the password field with a hashed value
for user in users:
    hashed_password = bcrypt.generate_password_hash('default_password').decode('utf-8')
    cursor.execute("UPDATE user SET password = ? WHERE id = ?", (hashed_password, user[0]))

# Commit the changes
conn.commit()

# Close the connection
conn.close()