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

@debug_bp.route('/debug/seed_fields')
@login_required
def seed_fields():
    if current_user.usertype.name not in ['Administrator', 'Admin']:
        return "Unauthorized", 403

    from project.models import BidField
    
    fields_data = [
        # Framing
        {'name': 'Plate', 'category': 'Framing', 'field_type': 'select', 'options': 'Treated, Standard', 'sort_order': 10},
        {'name': 'Stud', 'category': 'Framing', 'field_type': 'select', 'options': '2x4, 2x6', 'sort_order': 20},
        {'name': 'Wall Sheathing', 'category': 'Framing', 'field_type': 'select', 'options': 'OSB, Zip System, Plywood', 'sort_order': 30},
        {'name': 'Wall Sheathing Thickness', 'category': 'Framing', 'field_type': 'select', 'options': '7/16, 1/2, 5/8', 'sort_order': 40},
        {'name': 'House Wrap', 'category': 'Framing', 'field_type': 'select', 'options': 'None, Tyvek, Rex Wrap', 'sort_order': 50},
        {'name': 'Floor System', 'category': 'Framing', 'field_type': 'select', 'options': 'I-Joist, Open Web Truss, Dimensional Lumber', 'sort_order': 60},
        {'name': 'Subfloor', 'category': 'Framing', 'field_type': 'select', 'options': 'Advantech, OSB', 'sort_order': 70},
        {'name': 'Ceiling Joist', 'category': 'Framing', 'field_type': 'text', 'sort_order': 80},
        {'name': 'Rafter', 'category': 'Framing', 'field_type': 'text', 'sort_order': 90},
        {'name': 'Roof Decking', 'category': 'Framing', 'field_type': 'select', 'options': 'OSB, Zip System, Plywood', 'sort_order': 100},
        {'name': 'Roof Decking Thickness', 'category': 'Framing', 'field_type': 'select', 'options': '7/16, 1/2, 5/8', 'sort_order': 110},
        {'name': 'Felt Paper', 'category': 'Framing', 'field_type': 'select', 'options': '15#, 30#, Synthetic', 'sort_order': 120},
        {'name': 'Cornice', 'category': 'Framing', 'field_type': 'textarea', 'sort_order': 130},
        
        # Siding
        {'name': 'Siding Type', 'category': 'Siding', 'field_type': 'select', 'options': 'Vinyl, LP SmartSide, Hardie, Cedar', 'sort_order': 200},
        {'name': 'Lap Type', 'category': 'Siding', 'field_type': 'text', 'sort_order': 210},
        {'name': 'B and B', 'category': 'Siding', 'field_type': 'text', 'sort_order': 220},
        {'name': 'Shake', 'category': 'Siding', 'field_type': 'text', 'sort_order': 230},
        {'name': 'Soffit', 'category': 'Siding', 'field_type': 'text', 'sort_order': 240},
        {'name': 'Fascia', 'category': 'Siding', 'field_type': 'text', 'sort_order': 250},
        {'name': 'Porch Ceiling', 'category': 'Siding', 'field_type': 'text', 'sort_order': 260},
        {'name': 'Shutter', 'category': 'Siding', 'field_type': 'text', 'sort_order': 270},
        {'name': 'Vent', 'category': 'Siding', 'field_type': 'text', 'sort_order': 280},
        {'name': 'Column', 'category': 'Siding', 'field_type': 'text', 'sort_order': 290},
        {'name': 'Rail', 'category': 'Siding', 'field_type': 'text', 'sort_order': 300},
        
        # Shingle
        {'name': 'Shingle Mfg', 'category': 'Shingle', 'field_type': 'select', 'options': 'Owens Corning, GAF, Tamko', 'sort_order': 400},
        {'name': 'Shingle Type', 'category': 'Shingle', 'field_type': 'select', 'options': 'Architectural, 3-Tab', 'sort_order': 410},
        {'name': 'Shingle Color', 'category': 'Shingle', 'field_type': 'text', 'sort_order': 420},
        
        # Deck
        {'name': 'Decking Type', 'category': 'Deck', 'field_type': 'select', 'options': 'Treated, Composite, PVC', 'sort_order': 500},
        {'name': 'Railing', 'category': 'Deck', 'field_type': 'select', 'options': 'Wood, Aluminum, Vinyl, Cable', 'sort_order': 510},
        
        # Trim
        {'name': 'Base', 'category': 'Trim', 'field_type': 'text', 'sort_order': 600},
        {'name': 'Casing', 'category': 'Trim', 'field_type': 'text', 'sort_order': 610},
        {'name': 'Crown', 'category': 'Trim', 'field_type': 'text', 'sort_order': 620},
        {'name': 'Interior Door Type', 'category': 'Trim', 'field_type': 'select', 'options': 'Molded, Wood, MDF', 'sort_order': 630},
        {'name': 'Interior Door Style', 'category': 'Trim', 'field_type': 'text', 'sort_order': 640},
        {'name': 'Hardware Finish', 'category': 'Trim', 'field_type': 'text', 'sort_order': 650},
        {'name': 'Stair Part', 'category': 'Trim', 'field_type': 'text', 'sort_order': 660},
        
        # Window/Door (Exterior)
        {'name': 'Window Brand', 'category': 'Window', 'field_type': 'select', 'options': 'Andersen, Marvin, Pella, Vinyl', 'sort_order': 700},
        {'name': 'Window Series', 'category': 'Window', 'field_type': 'text', 'sort_order': 710},
        {'name': 'Window Color', 'category': 'Window', 'field_type': 'text', 'sort_order': 720},
        {'name': 'Grid Pattern', 'category': 'Window', 'field_type': 'text', 'sort_order': 730},
        
        {'name': 'Ext Door Brand', 'category': 'Door', 'field_type': 'select', 'options': 'Therma-Tru, Masonite', 'sort_order': 800},
        {'name': 'Ext Door Material', 'category': 'Door', 'field_type': 'select', 'options': 'Fiberglass, Steel, Wood', 'sort_order': 810},
    ]
    
    count = 0
    added = []
    skipped = []
    
    for data in fields_data:
        exists = BidField.query.filter_by(name=data['name'], category=data['category']).first()
        if not exists:
            new_field = BidField(
                name=data['name'],
                category=data['category'],
                field_type=data['field_type'],
                options=data.get('options'),
                sort_order=data['sort_order'],
                branch_ids='[]' # Default to all
            )
            db.session.add(new_field)
            count += 1
            added.append(f"{data['category']} - {data['name']}")
        else:
            skipped.append(f"{data['category']} - {data['name']}")
    
    db.session.commit()
    return f"Seeded {count} fields.<br><br><b>Added:</b><br>{'<br>'.join(added)}<br><br><b>Skipped (Already Existed):</b><br>{'<br>'.join(skipped)}"
