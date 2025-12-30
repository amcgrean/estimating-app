import sqlite3

# Connect to the database
conn = sqlite3.connect('/home/amcgrean/mysite/instance/bids.db')
cursor = conn.cursor()

# Select all users
cursor.execute("SELECT id FROM user")
users = cursor.fetchall()

# Update the password field with a plain text value
for user in users:
    password = 'default_password'
    cursor.execute("UPDATE user SET password = ? WHERE id = ?", (password, user[0]))

# Commit the changes
conn.commit()

# Close the connection
conn.close()