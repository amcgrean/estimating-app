import os

path = r"c:\Users\amcgrean\python\pa-bid-request\project\blueprints\main\routes.py"
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Verify end of file
last_lines = lines[-5:] # check last few lines
print("Last lines:", [l.strip() for l in last_lines])

expected_end = "trim_form=trim_form"
found = False
for l in last_lines:
    if expected_end in l:
        found = True
        break

if not found:
    print("WARNING: Expected end not found. Aborting append.")
    exit(1)

new_code = """

@main.route('/debug/fix_and_upgrade')
@login_required
def fix_and_upgrade():
    if current_user.usertype.name not in ['Administrator', 'Admin']:
        return "Unauthorized", 403

    try:
        # 1. Fix Head
        dead_end_rev = 'b2c3d4e5f6a7'
        new_parent_rev = 'd9319f6e738f'
        
        # Check current revision
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
        messages.append("SUCCESS: flask db upgrade executed. Refresh page/check DB.")
        
        return "<br>".join(messages)
    except Exception as e:
        return f"ERROR: {str(e)}"
"""

with open(path, 'a', encoding='utf-8') as f:
    f.write(new_code)
print("Successfully appended route.")
