
from project import create_app, db
from sqlalchemy import text

def fix_schema():
    app = create_app()
    with app.app_context():
        print(f"Connecting to: {app.config['SQLALCHEMY_DATABASE_URI']}")
        with db.engine.connect() as conn:
            # 1. Create Job Table if not exists
            # We can use the raw SQL for Postgres
            try:
                print("Checking/Creating Job table...")
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS job (
                        id SERIAL PRIMARY KEY,
                        customer_id INTEGER NOT NULL,
                        job_reference VARCHAR(50),
                        job_name VARCHAR(255) NOT NULL,
                        status VARCHAR(50),
                        FOREIGN KEY(customer_id) REFERENCES customer(id)
                    );
                """))
                conn.execute(text("CREATE INDEX IF NOT EXISTS ix_job_customer_id ON job (customer_id);"))
                print("Job table processed.")
            except Exception as e:
                print(f"Error creating Job table: {e}")

            # 2. Add columns to Bid and Design
            for table_name in ['bid', 'design']:
                print(f"Checking {table_name} for job_id...")
                try:
                    # Check column existence
                    result = conn.execute(text(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name='{table_name}' AND column_name='job_id';
                    """))
                    if result.rowcount == 0:
                        print(f"Adding job_id to {table_name}...")
                        conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN job_id INTEGER REFERENCES job(id);"))
                    else:
                        print(f"job_id already exists in {table_name}.")
                except Exception as e:
                    print(f"Error altering {table_name}: {e}")
            
            conn.commit()
            print("Schema fix complete.")

if __name__ == "__main__":
    fix_schema()
