
from flask_migrate import upgrade as flask_migrate_upgrade
from sqlalchemy import text

@main.route('/debug/fix_and_upgrade')
@login_required
def fix_and_upgrade():
    if current_user.usertype.name not in ['Administrator', 'Admin']:
        return "Unauthorized", 403

    try:
        # 1. Fix Head
        dead_end_rev = 'b2c3d4e5f6a7'
        new_parent_rev = 'd9319f6e738f'
        
        result = db.session.execute(text("SELECT version_num FROM alembic_version"))
        current_rev = result.scalar()
        
        messages = []
        messages.append(f"Initial Revision: {current_rev}")
        
        if current_rev == dead_end_rev:
            db.session.execute(text(f"UPDATE alembic_version SET version_num = '{new_parent_rev}' WHERE version_num = '{dead_end_rev}'"))
            db.session.commit()
            messages.append(f"FIX APPLIED: Updated alembic_version from {dead_end_rev} to {new_parent_rev}")
        else:
            messages.append(f"No version fix needed (Not at {dead_end_rev})")
            
        # 2. Run Upgrade
        flask_migrate_upgrade()
        messages.append("SUCCESS: flask db upgrade executed.")
        
        return "<br>".join(messages)
    except Exception as e:
        return f"ERROR: {str(e)}"
