from flask import Blueprint
from flask_login import login_required, current_user
from project import db
from sqlalchemy import text
import traceback

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/debug/fix_and_upgrade')
@login_required
def fix_and_upgrade():
    if current_user.usertype.name not in ['Administrator', 'Admin']:
        return "Unauthorized", 403

    try:
        # 1. Fix Head
        dead_end_rev = 'b2c3d4e5f6a7'
        # The new parent should be the one BEFORE the split.
        new_parent_rev = 'd9319f6e738f' 
        
        # Check current revision
        result = db.session.execute(text("SELECT version_num FROM alembic_version"))
        current_rev = result.scalar()
        
        messages = []
        messages.append(f"Initial Revision: {current_rev}")
        
        if current_rev == dead_end_rev or current_rev == 'manual_initial':
            db.session.execute(text(f"UPDATE alembic_version SET version_num = '{new_parent_rev}'"))
            db.session.commit()
            messages.append(f"FIX APPLIED: Forced alembic_version from {current_rev} to {new_parent_rev}")
            messages.append("IMPORTANT: Please REFRESH this page to run the upgrade now that the version is fixed.")
            return "<br>".join(messages)
        else:
            messages.append(f"No version fix needed (Not at {dead_end_rev} or manual_initial)")
            
        # 2. Run Upgrade
        from flask_migrate import upgrade as flask_migrate_upgrade
        
        # Explicitly configure alembic to ensure it sees the new state if possible, though new request is safer.
        flask_migrate_upgrade()
        messages.append("SUCCESS: flask db upgrade executed. Refresh page/check DB.")
        
        return "<br>".join(messages)
    except Exception as e:
        return f"ERROR: {str(e)} <br> <pre>{traceback.format_exc()}</pre>"
