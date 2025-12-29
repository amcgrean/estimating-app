import sqlite3

# Path to your SQLite database
db_path = '/home/amcgrean/mysite/instance/bids.db'

conn = sqlite3.connect(db_path)
c = conn.cursor()

# Check for any locks
c.execute("PRAGMA database_list;")
print(c.fetchall())

# Unlock the database
c.execute("PRAGMA locking_mode = EXCLUSIVE;")
conn.commit()

c.close()
conn.close()
