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
        # b2c3 is no longer a dead end; it is the valid parent of the new chain.
        # We only need to fix if we are at 'manual_initial' or unknown.
        new_valid_rev = 'b2c3d4e5f6a7'
        
        # Check current revision
        result = db.session.execute(text("SELECT version_num FROM alembic_version"))
        current_rev = result.scalar()
        
        messages = []
        messages.append(f"Initial Revision: {current_rev}")
        
        if current_rev == 'manual_initial':
            db.session.execute(text(f"UPDATE alembic_version SET version_num = '{new_valid_rev}'"))
            db.session.commit()
            messages.append(f"FIX APPLIED: Forced alembic_version from {current_rev} to {new_valid_rev}")
            messages.append("IMPORTANT: Please REFRESH this page to run the upgrade now that the version is fixed.")
            return "<br>".join(messages)
        elif current_rev == 'b2c3d4e5f6a7':
             messages.append(f"Version is {current_rev} (Valid). Proceeding to upgrade.")
        else:
            messages.append(f"Current version {current_rev}. Attempting upgrade...")
            
        # 2. Run Upgrade
        from flask_migrate import upgrade as flask_migrate_upgrade
        
        # Explicitly configure alembic to ensure it sees the new state if possible, though new request is safer.
        flask_migrate_upgrade()
        messages.append("SUCCESS: flask db upgrade executed. Refresh page/check DB.")
        
        return "<br>".join(messages)
    except Exception as e:
        return f"ERROR: {str(e)} <br> <pre>{traceback.format_exc()}</pre>"
