from project import create_app, db
from project.models import Bid

app = create_app()

def check_bids():
    with app.app_context():
        count = Bid.query.count()
        max_id = db.session.query(db.func.max(Bid.id)).scalar()
        print(f"Total Bids in DB: {count}")
        print(f"Max Bid ID in DB: {max_id}")

if __name__ == "__main__":
    check_bids()
