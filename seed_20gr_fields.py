"""
Seed script for 20GR (Grimes) branch-specific bid form fields.

These fields are derived from the legacy Gravity Forms "Estimating Spec Sheet" (form ID 4)
exported from beisserlumber.com and are restricted to branch_id matching code '20GR'.

Run with:  python seed_20gr_fields.py
"""

from project import create_app, db
from project.models import BidField, Branch
import json

app = create_app()


def seed_20gr_fields():
    with app.app_context():
        grimes = Branch.query.filter_by(branch_code='20GR').first()
        if not grimes:
            print("ERROR: Grimes branch (20GR) not found in Branch table. Aborting.")
            return

        branch_ids = json.dumps([grimes.branch_id])
        print(f"Seeding fields for branch: {grimes.branch_name} (ID={grimes.branch_id}, code={grimes.branch_code})")

        fields_data = [

            # ----------------------------------------------------------------
            # FRAMING
            # ----------------------------------------------------------------
            # Plate: replaces generic seed's "Treated, Standard" with legacy options
            {
                'name': 'Plate',
                'category': 'Framing',
                'field_type': 'select',
                'options': 'Treated, TimberStrand, Treated w/Triple, TimberStrand w/Triple',
                'is_required': True,
                'sort_order': 10,
            },
            # Lot Type: new field — not in generic seed
            {
                'name': 'Lot Type',
                'category': 'Framing',
                'field_type': 'select',
                'options': 'Walkout, Daylight, Flat Lot, Slab on Grade',
                'is_required': True,
                'sort_order': 15,
            },
            # Basement Wall Height: new field
            {
                'name': 'Basement Wall Height',
                'category': 'Framing',
                'field_type': 'select',
                'options': "8', 9', 10'",
                'is_required': False,
                'sort_order': 20,
            },
            # Basement Exterior Walls: new field
            {
                'name': 'Basement Exterior Walls',
                'category': 'Framing',
                'field_type': 'select',
                'options': '2x4, 2x6, Other(specify in notes)',
                'is_required': True,
                'sort_order': 25,
            },
            # Basement Interior Walls: new field
            {
                'name': 'Basement Interior Walls',
                'category': 'Framing',
                'field_type': 'select',
                'options': 'As Shown, Bearing Only',
                'is_required': True,
                'sort_order': 30,
            },
            # Floor Framing: replaces generic "Floor System" (I-Joist/Open Web/Dim Lumber)
            {
                'name': 'Floor Framing',
                'category': 'Framing',
                'field_type': 'select',
                'options': 'TJI I-Joist, Floor Trusses, 2x, N/a',
                'is_required': True,
                'sort_order': 35,
            },
            # Floor Sheeting: replaces generic "Subfloor" (Advantech/OSB)
            {
                'name': 'Floor Sheeting',
                'category': 'Framing',
                'field_type': 'select',
                'options': 'Edge, Gold, Advantech',
                'is_required': True,
                'sort_order': 40,
            },
            # Floor Adhesive: new field
            {
                'name': 'Floor Adhesive',
                'category': 'Framing',
                'field_type': 'select',
                'options': 'SF-450, Advantech',
                'is_required': True,
                'sort_order': 45,
            },
            # Exterior Walls: replaces generic "Stud" (2x4/2x6)
            {
                'name': 'Exterior Walls',
                'category': 'Framing',
                'field_type': 'select',
                'options': '2x4, 2x6, Other(specify in notes)',
                'is_required': True,
                'sort_order': 50,
            },
            # 1st Floor Wall Height: new field
            {
                'name': '1st Floor Wall Height',
                'category': 'Framing',
                'field_type': 'select',
                'options': "8', 9', 10', 12', Per Plan",
                'is_required': True,
                'sort_order': 55,
            },
            # 2nd Floor Wall Height: new field
            {
                'name': '2nd Floor Wall Height',
                'category': 'Framing',
                'field_type': 'select',
                'options': "8', 9', 10', 12', Per Plan",
                'is_required': False,
                'sort_order': 60,
            },
            # Wall Sheeting: replaces generic "Wall Sheathing" (OSB/Zip System/Plywood)
            {
                'name': 'Wall Sheeting',
                'category': 'Framing',
                'field_type': 'select',
                'options': '7/16" OSB, 1/2" OSB, Zip Panels',
                'is_required': True,
                'sort_order': 65,
            },
            # Roof Trusses: new field
            {
                'name': 'Roof Trusses',
                'category': 'Framing',
                'field_type': 'select',
                'options': 'Yes, By Others',
                'is_required': True,
                'sort_order': 70,
            },
            # Roof Sheeting: replaces generic "Roof Decking" (OSB/Zip System/Plywood)
            {
                'name': 'Roof Sheeting',
                'category': 'Framing',
                'field_type': 'select',
                'options': '1/2" OSB, 7/16" OSB, 5/8" OSB, Zip Panels',
                'is_required': True,
                'sort_order': 75,
            },

            # ----------------------------------------------------------------
            # SIDING
            # ----------------------------------------------------------------
            # Lap Type: replaces generic text field with legacy select options
            {
                'name': 'Lap Type',
                'category': 'Siding',
                'field_type': 'select',
                'options': 'LP, Hardie, 100% LP, 100% Hardie, N/a - other',
                'is_required': True,
                'sort_order': 200,
            },
            # Panel Type: new field (conditional on Lap Type in legacy — show always here)
            {
                'name': 'Panel Type',
                'category': 'Siding',
                'field_type': 'select',
                'options': 'LP, Hardie, N/a - other',
                'is_required': True,
                'sort_order': 210,
            },
            # Shake Type: replaces generic text "Shake" with legacy select
            {
                'name': 'Shake Type',
                'category': 'Siding',
                'field_type': 'select',
                'options': 'LP, Hardie, N/a - other',
                'is_required': True,
                'sort_order': 220,
            },
            # Soffit/Trim: replaces generic text "Soffit" with legacy select
            {
                'name': 'Soffit/Trim',
                'category': 'Siding',
                'field_type': 'select',
                'options': 'LP, Hardie, Rollex, N/a - other',
                'is_required': True,
                'sort_order': 230,
            },
            # Window Trim Detail: new field
            {
                'name': 'Window Trim Detail',
                'category': 'Siding',
                'field_type': 'select',
                'options': 'Per Plan, Front Only, All Sides, No Window Trim',
                'is_required': True,
                'sort_order': 240,
            },

            # ----------------------------------------------------------------
            # SHINGLES
            # Note: The Bid model has a static shingle_notes textarea. This
            # dynamic field captures the required shingle specification per the
            # legacy form ("Please specify any brand or style/color you would
            # like bid.").  Category must match template check: 'Shingles'.
            # ----------------------------------------------------------------
            {
                'name': 'Shingle Specs',
                'category': 'Shingles',
                'field_type': 'textarea',
                'options': None,
                'is_required': True,
                'sort_order': 400,
            },

            # ----------------------------------------------------------------
            # DECK
            # ----------------------------------------------------------------
            # Decking Type: replaces generic (Treated/Composite/PVC) with legacy options
            {
                'name': 'Decking Type',
                'category': 'Deck',
                'field_type': 'select',
                'options': 'Treated, Composite - Stock, Composite - Midgrade, Composite - High End, Cedar',
                'is_required': True,
                'sort_order': 500,
            },
            # Railing Type: replaces generic "Railing" (Wood/Aluminum/Vinyl/Cable)
            {
                'name': 'Railing Type',
                'category': 'Deck',
                'field_type': 'select',
                'options': 'Treated, Treated w/Facemount, Cedar, Cedar w/Facemount, Westbury - Black, Westbury - Dark Bronze, Westbury - Gloss White',
                'is_required': True,
                'sort_order': 510,
            },
            # Stairs: new field
            {
                'name': 'Stairs',
                'category': 'Deck',
                'field_type': 'select',
                'options': 'Yes, No',
                'is_required': True,
                'sort_order': 520,
            },
            # Landing: new field
            {
                'name': 'Landing',
                'category': 'Deck',
                'field_type': 'select',
                'options': 'Yes, No',
                'is_required': True,
                'sort_order': 530,
            },

            # ----------------------------------------------------------------
            # DOOR (Exterior Doors)
            # Legacy uses a free-text allowance/notes field rather than brand/material
            # ----------------------------------------------------------------
            {
                'name': 'Exterior Allowance/Notes',
                'category': 'Door',
                'field_type': 'textarea',
                'options': None,
                'is_required': True,
                'sort_order': 800,
            },
            # Installation Services: individual checkbox fields per legacy checkboxes
            {
                'name': 'Install Front Door',
                'category': 'Door',
                'field_type': 'checkbox',
                'options': None,
                'is_required': False,
                'sort_order': 810,
            },
            {
                'name': 'Install Large Patio Doors',
                'category': 'Door',
                'field_type': 'checkbox',
                'options': None,
                'is_required': False,
                'sort_order': 820,
            },
            {
                'name': 'Install All Doors',
                'category': 'Door',
                'field_type': 'checkbox',
                'options': None,
                'is_required': False,
                'sort_order': 830,
            },

            # ----------------------------------------------------------------
            # WINDOW
            # ----------------------------------------------------------------
            # Window Brand: replaces generic (Andersen/Marvin/Pella/Vinyl) with full legacy list
            {
                'name': 'Window Brand',
                'category': 'Window',
                'field_type': 'select',
                'options': (
                    'Gerkin Vinyl, Sierra Pacific Vinyl, Sierra Pacific H3, '
                    'Andersen 100 Series, Andersen 400 Series, '
                    'Marvin Essential - All Fiberglass, '
                    'Marvin Elevate - Wood Interior Fiberglass Exterior, '
                    'Marvin Signature - Aluminum Clad Wood, '
                    'Marvin Modern & Vivid - Fiberglass Large Scale Windows'
                ),
                'is_required': True,
                'sort_order': 700,
            },
            # Window Color: replaces generic text with legacy select
            {
                'name': 'Window Color',
                'category': 'Window',
                'field_type': 'select',
                'options': 'White, Black Ext / White Int, Black/Black',
                'is_required': False,
                'sort_order': 710,
            },
            # Window Type: new field
            {
                'name': 'Window Type',
                'category': 'Window',
                'field_type': 'select',
                'options': 'Single Hung, Double Hung, Sliders, Casement',
                'is_required': False,
                'sort_order': 720,
            },
            # Window Grills/Grids: replaces generic text "Grid Pattern" with legacy select
            {
                'name': 'Window Grills/Grids',
                'category': 'Window',
                'field_type': 'select',
                'options': 'Front Only, All Windows, Per Plan, No grids/grills',
                'is_required': False,
                'sort_order': 730,
            },
            # Jambs: new field
            {
                'name': 'Jambs',
                'category': 'Window',
                'field_type': 'select',
                'options': 'Bid in Trim Package, Applied to windows, N/A',
                'is_required': False,
                'sort_order': 740,
            },
            # Window Install: new field
            {
                'name': 'Window Install',
                'category': 'Window',
                'field_type': 'select',
                'options': 'N/a, Large Patio Door Install, Window Install (All)',
                'is_required': False,
                'sort_order': 750,
            },

            # ----------------------------------------------------------------
            # TRIM
            # ----------------------------------------------------------------
            # Base: replaces generic text field with full legacy select list
            {
                'name': 'Base',
                'category': 'Trim',
                'field_type': 'select',
                'options': (
                    'MDF 1x6, MDF 1x8, MDF 1x4, '
                    'MDF 421 (3-1/4"), MDF 430 (1/2x4.25"), MDF 432 (1/2x3.5"), '
                    'MDF 473 (2-1/4"), MDF 512 (1/2x5.5"), MDF 714 (1/2x7-1/4"), '
                    'Clay Coat Col 620J (4-1/4"), Clay Coat Col L634 (3"), '
                    'Poplar Miss F2380 4-1/4, Poplar BIG Mission F293 5-1/4", '
                    'Poplar Colonial F218 2-5/8", Poplar Colonial F225 4-1/4", '
                    'Poplar Colonial F2800 5-1/4", '
                    'Maple Mission F2380 4-1/4", Oak Mission F2380 4-1/4"'
                ),
                'is_required': True,
                'sort_order': 600,
            },
            # Case: new field (legacy "Case" — replaces generic "Casing" text field)
            {
                'name': 'Case',
                'category': 'Trim',
                'field_type': 'select',
                'options': (
                    'MDF 1x4, MDF 1x6, MDF 1x8, '
                    'MDF 421 (3-1/4"), MDF 430 (1/2x4.25"), MDF 432 (1/2x3.5"), '
                    'MDF 473 (2-1/4"), MDF 512 (1/2x5.5"), '
                    'MDF 683 w/Backband (11/16" x 3-1/4"), '
                    'Claycoat 356J (2-1/4"), Claycoat 444J (3-1/4"), '
                    'Poplar Miss 7/16 x 3-1/4", Poplar BIG Miss 9/16 x 3-1/4", '
                    'Poplar Colonial F115 2-1/4", Poplar Colonial F134 3-1/4", '
                    'Maple Mission 3-1/4", Oak Mission 3-1/4"'
                ),
                'is_required': True,
                'sort_order': 610,
            },
            # Stair Material: replaces generic text "Stair Part" with legacy select
            {
                'name': 'Stair Material',
                'category': 'Trim',
                'field_type': 'select',
                'options': 'Poplar, Primed, Maple, Oak',
                'is_required': True,
                'sort_order': 620,
            },
            # Door Material/Type: replaces generic "Interior Door Type" (Molded/Wood/MDF)
            {
                'name': 'Door Material/Type',
                'category': 'Trim',
                'field_type': 'select',
                'options': 'Molded - H/C, Molded - S/C, Poplar, Maple, Oak, N/A',
                'is_required': True,
                'sort_order': 630,
            },
            # # of Panels: new field
            {
                'name': '# of Panels',
                'category': 'Trim',
                'field_type': 'text',
                'options': None,
                'is_required': True,
                'sort_order': 640,
            },
            # Door Hardware: new field (replaces generic "Hardware Finish" text)
            {
                'name': 'Door Hardware',
                'category': 'Trim',
                'field_type': 'select',
                'options': 'Schlage, Dexter',
                'is_required': True,
                'sort_order': 650,
            },
            # Built-in Materials Type: new field
            {
                'name': 'Built-in Materials Type',
                'category': 'Trim',
                'field_type': 'select',
                'options': 'Poplar, Birch, Maple, Oak, N/A',
                'is_required': True,
                'sort_order': 660,
            },
            # Plywood/1x Count: new field
            {
                'name': 'Plywood/1x Count',
                'category': 'Trim',
                'field_type': 'select',
                'options': 'Small (3-5 pcs), Medium (5-8 pcs), Large (10-12 pcs), Other',
                'is_required': False,
                'sort_order': 670,
            },
            # Trim Allowance: new field
            {
                'name': 'Trim Allowance',
                'category': 'Trim',
                'field_type': 'text',
                'options': None,
                'is_required': False,
                'sort_order': 680,
            },
        ]

        added = 0
        skipped = 0
        for data in fields_data:
            # Check for duplicate: same name + category + branch already exists
            exists = BidField.query.filter_by(
                name=data['name'],
                category=data['category'],
                branch_ids=branch_ids,
            ).first()

            if exists:
                print(f"  SKIP (already exists): [{data['category']}] {data['name']}")
                skipped += 1
                continue

            new_field = BidField(
                name=data['name'],
                category=data['category'],
                field_type=data['field_type'],
                options=data.get('options'),
                is_required=data.get('is_required', False),
                sort_order=data['sort_order'],
                branch_ids=branch_ids,
                is_active=True,
            )
            db.session.add(new_field)
            print(f"  ADD: [{data['category']}] {data['name']}")
            added += 1

        db.session.commit()
        print(f"\nDone. Added {added} fields, skipped {skipped} existing fields for 20GR (Grimes).")


if __name__ == '__main__':
    seed_20gr_fields()
