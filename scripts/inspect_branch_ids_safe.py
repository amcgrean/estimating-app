
import sys
import os
import json

# Add project root to path
sys.path.append(os.getcwd())

from project import create_app, db
from project.models import BidField

app = create_app()
with app.app_context():
    fields = BidField.query.all()
    print("--- START DUMP ---")
    for f in fields:
        raw_val = f.branch_ids
        # Explicitly check for non-None, non-standard values
        if raw_val is None:
            val_str = "None"
        else:
            val_str = f"'{raw_val}'"
        
        print(f"ID: {f.id}, Name: {f.name}, BranchIDs: {val_str}")
    print("--- END DUMP ---")
