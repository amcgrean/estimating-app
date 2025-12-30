import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables if present
load_dotenv()

from project import create_app, db
# We must import models so they are registered with the metadata
from project import models 

# Configuration
SOURCE_DB = "sqlite:///instance/bids.db"
TARGET_DB = os.environ.get("DATABASE_URL")

def migrate():
    if not TARGET_DB:
        print("ERROR: DATABASE_URL environment variable is not set.")
        return

    print(f"Connecting to Source: {SOURCE_DB}")
    print(f"Connecting to Target: {TARGET_DB[:25]}...")

    source_engine = create_engine(SOURCE_DB)
    target_engine = create_engine(TARGET_DB)

    # Use the app context and models to create the target schema
    # Use the app context and models to create the target schema
    app = create_app()
    with app.app_context():
        print("Resetting target database (Drop & Recreate)...")
        db.metadata.drop_all(bind=target_engine)
        db.metadata.create_all(bind=target_engine)

    # Reflect schema from source ONLY for reading data
    print("Reflecting source tables...")
    source_meta = MetaData()
    source_meta.reflect(bind=source_engine)

    # Transfer data
    Session = sessionmaker(bind=target_engine)
    session = Session()

    # Track valid IDs for foreign key validation
    valid_ids = {} 

    # Sort tables by dependency using the models' metadata
    print("\nStarting data transfer...")
    
    for target_table in db.metadata.sorted_tables:
        if target_table.name not in source_meta.tables:
            print(f"Skipping table {target_table.name} (not in source DB)")
            continue

        print(f"Migrating table: {target_table.name}...", end=" ")
        source_table = source_meta.tables[target_table.name]
        
        # Read from source
        with source_engine.connect() as conn:
            result = conn.execute(source_table.select())
            rows = [dict(row._mapping) for row in result]

        if not rows:
            print("Empty.")
            # Still track that this table is "done" (empty)
            valid_ids[target_table.name] = set()
            continue

        # --- DATA SANITIZATION ---
        for row in rows:
            for fk in target_table.foreign_keys:
                col_name = fk.parent.name
                val = row.get(col_name)
                if val is not None:
                    parent_table_name = fk.column.table.name
                    # If we have the parent table's keys, validate
                    if parent_table_name in valid_ids:
                        if val not in valid_ids[parent_table_name]:
                            # Orphan found! Nullify it.
                            row[col_name] = None
                    elif val == 0:
                        # Fallback for tables not in the loop yet or 0 values
                        row[col_name] = None

        try:
            # Bulk insert
            session.execute(target_table.insert(), rows)
            session.commit()
            
            # Store primary keys for future FK validation
            pk_cols = [c.name for c in target_table.primary_key.columns]
            if pk_cols:
                pk = pk_cols[0] 
                valid_ids[target_table.name] = set(row[pk] for row in rows)
            
            print(f"Done ({len(rows)} rows)")
        except Exception as e:
            session.rollback()
            print(f"Failed: {e}")

    print("\nMigration Complete!")

if __name__ == "__main__":
    migrate()
