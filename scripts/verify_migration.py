import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from project import create_app, db
from project.models import Bid

app = create_app()
with app.app_context():
    count = Bid.query.count()
    print(f"Total Bids in DB: {count}")
    
    last_bid = Bid.query.order_by(Bid.id.desc()).first()
    if last_bid:
        print(f"Last Bid ID: {last_bid.id}")
        print(f"Last Bid Customer: {last_bid.customer_id}")
