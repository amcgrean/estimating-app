from project import create_app, db
from project.models import Bid

def update_bid_status():
    app = create_app()
    with app.app_context():
        try:
            bids = Bid.query.all()
            for bid in bids:
                bid.status = 'Complete'
            db.session.commit()
            print("All bids have been updated to 'Complete' status.")
        except Exception as e:
            db.session.rollback()
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    update_bid_status()
