"""
Seed script for 40CV (Coralville) branch-specific bid form fields.

All fields here are restricted to branch_ids=[3] (Coralville/40CV).
They will NOT appear for 20GR (Grimes) users.

If records already exist in the DB with branch_ids='[]' (all-branches),
this script updates them to branch_ids='[3]' so they are 40CV-only.

Run with:  python seed_dynamic_fields.py
"""

from project import create_app, db
from project.models import BidField, Branch
import json

app = create_app()

CORALVILLE_CODE = '40CV'


def seed_fields():
    with app.app_context():
        coralville = Branch.query.filter_by(branch_code=CORALVILLE_CODE).first()
        if not coralville:
            print(f"ERROR: Branch '{CORALVILLE_CODE}' not found. Aborting.")
            return

        branch_ids = json.dumps([coralville.branch_id])
        print(f"Seeding fields for branch: {coralville.branch_name} (ID={coralville.branch_id}, code={coralville.branch_code})")

        fields_data = [
            # ------------------------------------------------------------------
            # FRAMING
            # ------------------------------------------------------------------
            {'name': 'Plate',                 'category': 'Framing', 'field_type': 'select',   'options': 'Treated, Standard',                          'sort_order': 10},
            {'name': 'Stud',                  'category': 'Framing', 'field_type': 'select',   'options': '2x4, 2x6',                                   'sort_order': 20},
            {'name': 'Wall Sheathing',        'category': 'Framing', 'field_type': 'select',   'options': 'OSB, Zip System, Plywood',                   'sort_order': 30},
            {'name': 'Wall Sheathing Thickness', 'category': 'Framing', 'field_type': 'select','options': '7/16, 1/2, 5/8',                             'sort_order': 40},
            {'name': 'House Wrap',            'category': 'Framing', 'field_type': 'select',   'options': 'None, Tyvek, Rex Wrap',                      'sort_order': 50},
            {'name': 'Floor System',          'category': 'Framing', 'field_type': 'select',   'options': 'I-Joist, Open Web Truss, Dimensional Lumber', 'sort_order': 60},
            {'name': 'Subfloor',              'category': 'Framing', 'field_type': 'select',   'options': 'Advantech, OSB',                             'sort_order': 70},
            {'name': 'Ceiling Joist',         'category': 'Framing', 'field_type': 'text',     'options': None,                                         'sort_order': 80},
            {'name': 'Rafter',                'category': 'Framing', 'field_type': 'text',     'options': None,                                         'sort_order': 90},
            {'name': 'Roof Decking',          'category': 'Framing', 'field_type': 'select',   'options': 'OSB, Zip System, Plywood',                   'sort_order': 100},
            {'name': 'Roof Decking Thickness','category': 'Framing', 'field_type': 'select',   'options': '7/16, 1/2, 5/8',                             'sort_order': 110},
            {'name': 'Felt Paper',            'category': 'Framing', 'field_type': 'select',   'options': '15#, 30#, Synthetic',                        'sort_order': 120},
            {'name': 'Cornice',               'category': 'Framing', 'field_type': 'textarea', 'options': None,                                         'sort_order': 130},

            # ------------------------------------------------------------------
            # SIDING
            # ------------------------------------------------------------------
            {'name': 'Siding Type',    'category': 'Siding', 'field_type': 'select', 'options': 'Vinyl, LP SmartSide, Hardie, Cedar', 'sort_order': 200},
            {'name': 'Lap Type',       'category': 'Siding', 'field_type': 'text',   'options': None,                                 'sort_order': 210},
            {'name': 'B and B',        'category': 'Siding', 'field_type': 'text',   'options': None,                                 'sort_order': 220},
            {'name': 'Shake',          'category': 'Siding', 'field_type': 'text',   'options': None,                                 'sort_order': 230},
            {'name': 'Soffit',         'category': 'Siding', 'field_type': 'text',   'options': None,                                 'sort_order': 240},
            {'name': 'Fascia',         'category': 'Siding', 'field_type': 'text',   'options': None,                                 'sort_order': 250},
            {'name': 'Porch Ceiling',  'category': 'Siding', 'field_type': 'text',   'options': None,                                 'sort_order': 260},
            {'name': 'Shutter',        'category': 'Siding', 'field_type': 'text',   'options': None,                                 'sort_order': 270},
            {'name': 'Vent',           'category': 'Siding', 'field_type': 'text',   'options': None,                                 'sort_order': 280},
            {'name': 'Column',         'category': 'Siding', 'field_type': 'text',   'options': None,                                 'sort_order': 290},
            {'name': 'Rail',           'category': 'Siding', 'field_type': 'text',   'options': None,                                 'sort_order': 300},

            # ------------------------------------------------------------------
            # SHINGLES  (category='Shingles' to match template check)
            # ------------------------------------------------------------------
            {'name': 'Shingle Mfg',   'category': 'Shingles', 'field_type': 'select', 'options': 'Owens Corning, GAF, Tamko', 'sort_order': 400},
            {'name': 'Shingle Type',  'category': 'Shingles', 'field_type': 'select', 'options': 'Architectural, 3-Tab',      'sort_order': 410},
            {'name': 'Shingle Color', 'category': 'Shingles', 'field_type': 'text',   'options': None,                        'sort_order': 420},

            # ------------------------------------------------------------------
            # DECK
            # ------------------------------------------------------------------
            {'name': 'Decking Type', 'category': 'Deck', 'field_type': 'select', 'options': 'Treated, Composite, PVC',        'sort_order': 500},
            {'name': 'Railing',      'category': 'Deck', 'field_type': 'select', 'options': 'Wood, Aluminum, Vinyl, Cable',   'sort_order': 510},

            # ------------------------------------------------------------------
            # TRIM
            # ------------------------------------------------------------------
            {'name': 'Base',               'category': 'Trim', 'field_type': 'text',   'options': None,                      'sort_order': 600},
            {'name': 'Casing',             'category': 'Trim', 'field_type': 'text',   'options': None,                      'sort_order': 610},
            {'name': 'Crown',              'category': 'Trim', 'field_type': 'text',   'options': None,                      'sort_order': 620},
            {'name': 'Interior Door Type', 'category': 'Trim', 'field_type': 'select', 'options': 'Molded, Wood, MDF',       'sort_order': 630},
            {'name': 'Interior Door Style','category': 'Trim', 'field_type': 'text',   'options': None,                      'sort_order': 640},
            {'name': 'Hardware Finish',    'category': 'Trim', 'field_type': 'text',   'options': None,                      'sort_order': 650},
            {'name': 'Stair Part',         'category': 'Trim', 'field_type': 'text',   'options': None,                      'sort_order': 660},

            # ------------------------------------------------------------------
            # WINDOW
            # ------------------------------------------------------------------
            {'name': 'Window Brand',  'category': 'Window', 'field_type': 'select', 'options': 'Andersen, Marvin, Pella, Vinyl', 'sort_order': 700},
            {'name': 'Window Series', 'category': 'Window', 'field_type': 'text',   'options': None,                             'sort_order': 710},
            {'name': 'Window Color',  'category': 'Window', 'field_type': 'text',   'options': None,                             'sort_order': 720},
            {'name': 'Grid Pattern',  'category': 'Window', 'field_type': 'text',   'options': None,                             'sort_order': 730},

            # ------------------------------------------------------------------
            # DOOR
            # ------------------------------------------------------------------
            {'name': 'Ext Door Brand',    'category': 'Door', 'field_type': 'select', 'options': 'Therma-Tru, Masonite',    'sort_order': 800},
            {'name': 'Ext Door Material', 'category': 'Door', 'field_type': 'select', 'options': 'Fiberglass, Steel, Wood', 'sort_order': 810},
        ]

        added = 0
        updated = 0

        for data in fields_data:
            # Look for an existing record regardless of its current branch_ids
            # (handles old 'Shingle' category records too by also checking with 's')
            existing = BidField.query.filter_by(
                name=data['name'],
                category=data['category'],
            ).first()

            # Also catch old Shingle records stored without the 's'
            if not existing and data['category'] == 'Shingles':
                existing = BidField.query.filter_by(
                    name=data['name'],
                    category='Shingle',
                ).first()

            if existing:
                # Only update if currently un-restricted (all-branches)
                if existing.branch_ids in (None, '[]', ''):
                    existing.branch_ids = branch_ids
                    existing.category = data['category']   # fix 'Shingle' -> 'Shingles' if needed
                    print(f"  UPDATE -> 40CV only: [{data['category']}] {data['name']}")
                    updated += 1
                else:
                    print(f"  SKIP (already branch-restricted): [{data['category']}] {data['name']} branch_ids={existing.branch_ids}")
            else:
                new_field = BidField(
                    name=data['name'],
                    category=data['category'],
                    field_type=data['field_type'],
                    options=data.get('options'),
                    sort_order=data['sort_order'],
                    branch_ids=branch_ids,
                    is_active=True,
                )
                db.session.add(new_field)
                print(f"  ADD (40CV): [{data['category']}] {data['name']}")
                added += 1

        db.session.commit()
        print(f"\nDone. Added {added} new fields, updated {updated} existing fields to 40CV-only.")


if __name__ == '__main__':
    seed_fields()
