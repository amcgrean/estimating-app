from project import create_app, db
from project.models import BidField
import json

app = create_app()

def seed_fields():
    with app.app_context():
        # Clear existing? Maybe check if exists first to avoid duplicates.
        # For now, let's assume empty or id-based check.
        
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
        for data in fields_data:
            exists = BidField.query.filter_by(name=data['name'], category=data['category']).first()
            if not exists:
                new_field = BidField(
                    name=data['name'],
                    category=data['category'],
                    field_type=data['field_type'],
                    options=data.get('options'),
                    sort_order=data['sort_order'],
                    branch_ids='[]' # Default to all? Empty means all in our logic
                )
                db.session.add(new_field)
                count += 1
        
        db.session.commit()
        print(f"Seeded {count} dynamic fields.")

if __name__ == '__main__':
    seed_fields()
