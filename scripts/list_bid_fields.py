import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from project import create_app, db
from project.models import BidField

app = create_app()
with app.app_context():
    fields = BidField.query.limit(5).all()
    print("--- Available Bid Fields ---")
    for f in fields:
        print(f"ID: {f.id}, Name: '{f.name}', Category: '{f.category}'")
