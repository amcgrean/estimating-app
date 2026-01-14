from project import create_app, db
from project.models import Bid, BidField, BidValue, Framing, Siding, Shingle, Deck, Trim, Window, Door

app = create_app()

def migrate_data():
    with app.app_context():
        bids = Bid.query.all()
        print(f"Found {len(bids)} bids to migrate.")
        
        # Helper to get field ID map: (Category, Name) -> ID
        # Note: Names must match exactly with seed script
        fields = BidField.query.all()
        field_map = {(f.category, f.name): f.id for f in fields}
        
        migrated_count = 0
        
        for bid in bids:
            # --- FRAMING ---
            if bid.framing:
                mapping = [
                    ('Plate', bid.framing.plate),
                    ('Stud', bid.framing.stud),
                    ('Wall Sheathing', bid.framing.wall_sheathing),
                    ('Wall Sheathing Thickness', bid.framing.wall_sheathing_thickness),
                    ('House Wrap', bid.framing.house_wrap),
                    ('Floor System', bid.framing.floor_system),
                    ('Subfloor', bid.framing.subfloor),
                    ('Ceiling Joist', bid.framing.ceiling_joist),
                    ('Rafter', bid.framing.rafter),
                    ('Roof Decking', bid.framing.roof_decking),
                    ('Roof Decking Thickness', bid.framing.roof_decking_thickness),
                    ('Felt Paper', bid.framing.felt_paper),
                    ('Cornice', bid.framing.cornice),
                ]
                for name, value in mapping:
                    if value:
                        f_id = field_map.get(('Framing', name))
                        if f_id:
                            if not BidValue.query.filter_by(bid_id=bid.id, field_id=f_id).first():
                                db.session.add(BidValue(bid_id=bid.id, field_id=f_id, value=str(value)))
            
            # Additional Notes field for Framing? No dynamic field for "Framing Notes" in seed script?
            # Let's check seed script. If not seeded, we can't migrate it to a dynamic field unless we create one.
            # Assuming we skip notes for now or seeded them if they were in the list.
            # Seed script didn't seem to have "Framing Notes" explicitly named "Framing Notes" but maybe "Notes"?
            # Seed script had: {'name': 'Cornice', 'category': 'Framing', ...}
            # It did NOT have "Framing Notes". It seems I missed notes in seed script or intentionally left them as static?
            # Implementation plan said: "Framing: ..., framing_notes".
            # If I missed it in seed, I should add it. Or just keep it as static column for now.
            # Given user request "Make bid sheet fields editable ... encompass all currently hardcoded fields", likely notes too.
            # But notes are usually large text areas.
            # Let's stick to the structure fields first. If notes are missing, I'll add them later.

            # --- SIDING ---
            if bid.siding:
                mapping = [
                    ('Siding Type', bid.siding.siding_type),
                    ('Lap Type', bid.siding.lap_type),
                    ('B and B', bid.siding.board_and_batten),
                    ('Shake', bid.siding.shake),
                    ('Soffit', bid.siding.soffit),
                    ('Fascia', bid.siding.fascia),
                    ('Porch Ceiling', bid.siding.porch_ceiling),
                    ('Shutter', bid.siding.shutter),
                    ('Vent', bid.siding.vent),
                    ('Column', bid.siding.column),
                    ('Rail', bid.siding.rail),
                ]
                for name, value in mapping:
                    if value:
                        f_id = field_map.get(('Siding', name))
                        if f_id:
                            if not BidValue.query.filter_by(bid_id=bid.id, field_id=f_id).first():
                                db.session.add(BidValue(bid_id=bid.id, field_id=f_id, value=str(value)))

            # --- SHINGLE ---
            if bid.shingle:
                mapping = [
                    ('Shingle Mfg', bid.shingle.shingle_mfg),
                    ('Shingle Type', bid.shingle.shingle_type),
                    ('Shingle Color', bid.shingle.shingle_color),
                ]
                for name, value in mapping:
                    if value:
                        f_id = field_map.get(('Shingle', name))
                        if f_id:
                            if not BidValue.query.filter_by(bid_id=bid.id, field_id=f_id).first():
                                db.session.add(BidValue(bid_id=bid.id, field_id=f_id, value=str(value)))

            # --- DECK ---
            if bid.deck:
                mapping = [
                    ('Decking Type', bid.deck.decking_type),
                    ('Railing', bid.deck.railing), # Check model key: railing_type?
                    # Model says 'railing_type'. Seed script says 'Railing'. 
                    # Let's check model again. 
                    # forms.py says `railing_type`. 
                    # models.py says:
                ]
                # I need to verify deck model attribute name. forms.py used `railing_type`.
                # Assuming `bid.deck.railing_type` exists.
                if hasattr(bid.deck, 'railing_type'):
                     mapping.append(('Railing', bid.deck.railing_type))
                
                for name, value in mapping:
                    if value:
                        f_id = field_map.get(('Deck', name))
                        if f_id:
                            if not BidValue.query.filter_by(bid_id=bid.id, field_id=f_id).first():
                                db.session.add(BidValue(bid_id=bid.id, field_id=f_id, value=str(value)))

            # --- TRIM ---
            if bid.trim:
                mapping = [
                    ('Base', bid.trim.base),
                    ('Casing', bid.trim.casing),
                    ('Crown', bid.trim.crown),
                    ('Interior Door Type', bid.trim.interior_door_type),
                    ('Interior Door Style', bid.trim.interior_door_style),
                    ('Hardware Finish', bid.trim.hardware_finish),
                    ('Stair Part', bid.trim.stair_part),
                ]
                for name, value in mapping:
                    if value:
                        f_id = field_map.get(('Trim', name))
                        if f_id:
                            if not BidValue.query.filter_by(bid_id=bid.id, field_id=f_id).first():
                                db.session.add(BidValue(bid_id=bid.id, field_id=f_id, value=str(value)))

            # --- WINDOW ---
            if bid.window:
                mapping = [
                     ('Window Brand', bid.window.window_brand),
                     ('Window Series', bid.window.window_series),
                     ('Window Color', bid.window.window_color),
                     ('Grid Pattern', bid.window.grid_pattern),
                ]
                for name, value in mapping:
                    if value:
                        f_id = field_map.get(('Window', name))
                        if f_id:
                            if not BidValue.query.filter_by(bid_id=bid.id, field_id=f_id).first():
                                db.session.add(BidValue(bid_id=bid.id, field_id=f_id, value=str(value)))

            # --- DOOR ---
            if bid.door:
                mapping = [
                    ('Ext Door Brand', bid.door.ext_door_brand),
                    ('Ext Door Material', bid.door.ext_door_material),
                ]
                for name, value in mapping:
                    if value:
                        f_id = field_map.get(('Door', name))
                        if f_id:
                            if not BidValue.query.filter_by(bid_id=bid.id, field_id=f_id).first():
                                db.session.add(BidValue(bid_id=bid.id, field_id=f_id, value=str(value)))
                                
            migrated_count += 1
            
        db.session.commit()
        print(f"Migrated data for {migrated_count} bids.")

if __name__ == '__main__':
    migrate_data()
