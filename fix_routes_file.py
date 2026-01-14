import os

path = r"c:\Users\amcgrean\python\pa-bid-request\project\blueprints\main\routes.py"
with open(path, 'rb') as f:
    content = f.read()

# Decode with utf-8, ignoring errors is risky but we know the top is good.
# Better to decode as utf-8 up to the known good point.
try:
    text_content = content.decode('utf-8')
except UnicodeDecodeError:
    # If it fails, likely the end is garbage.
    # formatting was:
    # 1923:         trim_form=trim_form
    # 1924:     )
    pass

# We can search for the byte sequence of the closing parenthesis and indentation
# "    )" -> b'    )' or b'\t)' depending on indentation.
# Based on view_file: "    )"
target = b"        trim_form=trim_form\r\n    )"
idx = content.find(target)
if idx == -1:
    target = b"        trim_form=trim_form\n    )"
    idx = content.find(target)

if idx != -1:
    end_idx = idx + len(target)
    clean_bytes = content[:end_idx]
    
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
    with open(path, 'wb') as f:
        f.write(clean_bytes)
        f.write(new_code.encode('utf-8'))
    print("File repaired successfully.")
else:
    print("Could not find target marker bytes.")
