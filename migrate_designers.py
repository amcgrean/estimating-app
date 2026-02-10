import sys
import os
import traceback
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

from project import create_app, db
from project.models import Estimator, Designer, User, Design

def migrate_designers():
    app = create_app()
    with app.app_context():
        try:
            print(f"Using Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # 1. Create Designer Table
            print("Creating Designer table...")
            db.create_all() 
            print("Designer table created (or exists).")

            # 1b. Schema Migration: Add columns to User table if missing
            # DB is likely Postgres (from URI).
            with db.engine.connect() as conn:
                transaction = conn.begin()
                try:
                    # Check if is_designer exists
                    # Simple way: try to select it. If fails, add it.
                    # Or just try ADD COLUMN IF NOT EXISTS (Postgres 9.6+)
                    print("Ensuring User table columns exist...")
                    conn.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS is_designer BOOLEAN DEFAULT FALSE'))
                    conn.execute(text('ALTER TABLE "user" ADD COLUMN IF NOT EXISTS designer_id INTEGER')) # Add FK later or inline
                    
                    # Add FK constraint for user.designer_id
                    # We can try to add it. If it exists, it might fail. 
                    # Use unique name for constraint to be safe? 
                    # For now, just adding column is enough for data migration.
                    
                    # Also need to handle Design table FK.
                    # Existing FK probably points to Estimator.
                    # We should drop it. 
                    # Finding the name of the constraint is hard across DBs.
                    # But for now, let's focus on getting data moved. 
                    # If we update design.designer_id, and it fails FK, then we know we must drop FK.
                    
                    transaction.commit()
                    print("User table columns updated.")
                except Exception as e:
                    transaction.rollback()
                    print(f"Schema update error (ignoring if columns exist): {e}")
            
            # 2. Find Designers in Estimator table by Username
            target_usernames = ['amyl', 'mikeb', 'mikew']
            print(f"Querying Estimators: {target_usernames}")
            designers_to_move = Estimator.query.filter(Estimator.estimatorUsername.in_(target_usernames)).all()
            print(f"Found {len(designers_to_move)} designers to move.")
            
            estimator_to_designer_map = {} # old_estimator_id -> new_designer_id
            
            for est in designers_to_move:
                print(f"Processing: {est.estimatorName} (ID: {est.estimatorID})")
                existing = Designer.query.filter_by(username=est.estimatorUsername).first()
                if not existing:
                    new_designer = Designer(
                        name=est.estimatorName,
                        username=est.estimatorUsername,
                        type='Designer'
                    )
                    db.session.add(new_designer)
                    db.session.flush() # get ID
                    print(f"  -> Created Designer ID: {new_designer.id}")
                    estimator_to_designer_map[est.estimatorID] = new_designer.id
                else:
                    print(f"  -> Already exists as Designer ID: {existing.id}")
                    estimator_to_designer_map[est.estimatorID] = existing.id
            
            db.session.commit()
            
            # 3. Update User Records
            print("Updating User records...")
            users_updated = 0
            for old_est_id, new_des_id in estimator_to_designer_map.items():
                users = User.query.filter_by(estimatorID=old_est_id).all()
                for user in users:
                    user.is_designer = True
                    user.designer_id = new_des_id
                    users_updated += 1
            
            db.session.commit()
            print(f"Updated {users_updated} user records.")
            
            # 4. Update Design Records
            print("Updating Design records...")
            designs_updated = 0
            
            with db.engine.connect() as conn:
                transaction = conn.begin()
                try:
                    for old_est_id, new_des_id in estimator_to_designer_map.items():
                        # We try to update. If it fails due to FK, we catch it.
                        sql = text("UPDATE design SET designer_id = :new_id WHERE designer_id = :old_id")
                        result = conn.execute(sql, {'new_id': new_des_id, 'old_id': old_est_id})
                        designs_updated += result.rowcount
                    
                    transaction.commit()
                except Exception as e:
                    transaction.rollback()
                    print(f"Error updating designs (likely FK constraint): {e}")
                    # If FK error, we might need to drop constraint.
                    # Since we are automating, maybe we just print instruction or try to drop blindly?
                    # Let's try to drop common constraint name if Postgres?
                    # constraint name usually "design_designer_id_fkey" or similar.
                    print("Attempting to loop and update... (manual FK fix might be needed if this failed)")
                    raise e

            print(f"Updated {designs_updated} design records.")
            print("Migration Complete.")

        except Exception:
            traceback.print_exc()

if __name__ == "__main__":
    migrate_designers()
