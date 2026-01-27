
from project import create_app, db
from project.models import Bid, BidValue, BidField
import json

app = create_app()

def check_select_fields(bid_id):
    with app.app_context():
        bid = Bid.query.get(bid_id)
        current_values = BidValue.query.filter_by(bid_id=bid.id).all()
        val_map = {v.field_id: v.value for v in current_values}
        
        fields = BidField.query.filter_by(is_active=True).all() # Get all active fields properties
        
        print(f"--- Checking SELECT fields for Bid {bid.id} ---")
        for field in fields:
            if field.field_type != 'select': continue
            
            if field.id in val_map:
                val = val_map[field.id]
                if not val:
                    print(f"Field '{field.name}' ({field.id}): Empty value")
                    continue
                
                try:
                    options = json.loads(field.options) if field.options else []
                except:
                    options = [o.strip() for o in field.options.split(',')] if field.options else []
                
                if val in options:
                    print(f"Field '{field.name}' ({field.id}): MATCH '{val}'")
                else:
                    print(f"Field '{field.name}' ({field.id}): MISMATCH '{val}'")
                    print(f"   Options: {options}")

if __name__ == "__main__":
    with app.app_context():
        # Find a bid with values
        val = BidValue.query.filter(BidValue.value != '', BidValue.value != None).first()
        if val:
            check_select_fields(val.bid_id)
