import os
import psycopg2

conn = psycopg2.connect(os.environ["DATABASE_URL"])
conn.autocommit = True
with conn.cursor() as cur:
    cur.execute("DROP TABLE IF EXISTS design_new;")
    print("Dropped design_new if it existed.")
conn.close()
