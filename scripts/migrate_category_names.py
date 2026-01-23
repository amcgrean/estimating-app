
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from project import create_app, db
from project.models import BidField

app = create_app()
with app.app_context():
    # Find fields with 'Shingle' category
    fields = BidField.query.filter_by(category='Shingle').all()
    count = 0
    for f in fields:
        print(f"Updating field ID {f.id}: {f.name} (Shingle -> Shingles)")
        f.category = 'Shingles'
        count += 1
    
    if count > 0:
        db.session.commit()
        print(f"Successfully updated {count} fields.")
    else:
        print("No fields found with category 'Shingle'. All good!")
