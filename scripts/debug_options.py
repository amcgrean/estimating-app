
from project import create_app, db
from project.models import Bid, BidValue, BidField
import json

app = create_app()

def check_options_mismatch(bid_id):
    with app.app_context():
        bid = Bid.query.get(bid_id)
        print(f"Checking Bid {bid_id}: {bid.project_name}")
        
        # Get values using explicit query
        current_values = BidValue.query.filter_by(bid_id=bid.id).all()
        val_map = {v.field_id: v.value for v in current_values}
        
        fields = BidField.query.filter_by(is_active=True).all()
        
        for field in fields:
            if field.id in val_map:
                val = val_map[field.id]
                if not val: continue 

                print(f"\nField: {field.name} (ID: {field.id}) Type: {field.field_type}")
                print(f"  Stored Value: '{val}'")
                
                if field.field_type == 'select':
                    # Get options
                    try:
                        options = json.loads(field.options) if field.options else []
                    except:
                        options = [o.strip() for o in field.options.split(',')] if field.options else []
                    
                    print(f"  Available Options: {options}")
                    
                    if val in options:
                        print("  STATUS: MATCH (Should show in UI)")
                    else:
                        print("  STATUS: MISMATCH (Will NOT show in UI)")
                        # Suggest potential fuzzy match
                        for opt in options:
                            if val.lower() == opt.lower():
                                print(f"    -> Case mismatch with '{opt}'")
                            elif val in opt or opt in val:
                                print(f"    -> Partial mismatch with '{opt}'")

if __name__ == "__main__":
    with app.app_context():
        # Find a bid with values
        val = BidValue.query.filter(BidValue.value != '', BidValue.value != None).first()
        if val:
            check_options_mismatch(val.bid_id)
        else:
            print("No bids with values found.")
