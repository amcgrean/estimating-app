import sys
import os
import traceback
from sqlalchemy import text

# Add project root to path
sys.path.append(os.getcwd())

from project import create_app, db
from project.models import Estimator, Designer, User, Design

def debug_migrate():
    # Write to log file directly
    with open('migration_log.txt', 'w', encoding='utf-8') as log_file:
        def log(msg):
            print(msg)
            log_file.write(msg + '\n')
            log_file.flush()

        app = create_app()
        with app.app_context():
            try:
                log(f"Using Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
                
                # 1. Create Designer Table
                log("Creating Designer table...")
                db.create_all() 
                log("Designer table created (or exists).")
                
                # 2. Find Designers in Estimator table by Username
                target_usernames = ['amyl', 'mikeb', 'mikew']
                log(f"Querying Estimators: {target_usernames}")
                designers_to_move = Estimator.query.filter(Estimator.estimatorUsername.in_(target_usernames)).all()
                log(f"Found {len(designers_to_move)} designers to move.")
                
                estimator_to_designer_map = {}
                for est in designers_to_move:
                    log(f"Processing: {est.estimatorName} (ID: {est.estimatorID})")
                    existing = Designer.query.filter_by(username=est.estimatorUsername).first()
                    if not existing:
                        new_designer = Designer(
                            name=est.estimatorName,
                            username=est.estimatorUsername,
                            type='Designer'
                        )
                        db.session.add(new_designer)
                        db.session.flush()
                        estimator_to_designer_map[est.estimatorID] = new_designer.id
                        log(f"Created Designer ID: {new_designer.id}")
                    else:
                        estimator_to_designer_map[est.estimatorID] = existing.id
                        log(f"Existing Designer ID: {existing.id}")
                
                db.session.commit()
                log("Designers processed and committed.")
                
                log("Updating Users...")
                users_updated = 0
                for old_est_id, new_des_id in estimator_to_designer_map.items():
                    log(f"Checking for users with estimatorID={old_est_id}")
                    users = User.query.filter_by(estimatorID=old_est_id).all()
                    for user in users:
                        log(f"  Updating user: {user.username}")
                        user.is_designer = True
                        user.designer_id = new_des_id
                        users_updated += 1
                
                db.session.commit()
                log(f"Updated {users_updated} user records.")
                
                log("Updating Designs...")
                designs_updated = 0
                with db.engine.connect() as conn:
                    transaction = conn.begin()
                    try:
                        for old_est_id, new_des_id in estimator_to_designer_map.items():
                            log(f"Updating designs for old_est_id={old_est_id} -> new_des_id={new_des_id}")
                            sql = text("UPDATE design SET designer_id = :new_id WHERE designer_id = :old_id")
                            result = conn.execute(sql, {'new_id': new_des_id, 'old_id': old_est_id})
                            log(f"  Rows affected: {result.rowcount}")
                            designs_updated += result.rowcount
                        transaction.commit()
                    except Exception as e:
                        transaction.rollback()
                        log(f"Error updating designs: {e}")
                        raise e
                        
                log(f"Updated {designs_updated} design records.")
                log("Migration Done.")
                
            except Exception:
                log("EXCEPTION OCCURRED:")
                log(traceback.format_exc())

if __name__ == "__main__":
    debug_migrate()
