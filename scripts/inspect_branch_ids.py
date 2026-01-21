
import sys
import os
from sqlalchemy import create_engine, inspect

# Add project root to path
sys.path.append(os.getcwd())

from project import create_app, db
from project.models import BidField

app = create_app()
with app.app_context():
    fields = BidField.query.all()
    print(f"{'ID':<5} | {'Name':<30} | {'Branch IDs RAW':<50}")
    print("-" * 90)
    for f in fields:
        raw_val = f.branch_ids
        # repr() to see if it's bytes or weird chars
        print(f"{f.id:<5} | {f.name[:30]:<30} | {repr(raw_val):<50}")
