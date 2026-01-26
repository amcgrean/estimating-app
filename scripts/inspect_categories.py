
import os
import sys
from sqlalchemy import create_engine, text

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from project import create_app, db
from project.models import BidField

def inspect_categories():
    app = create_app()
    with app.app_context():
        print(f"Connecting to: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Get all unique categories
        fields = BidField.query.all()
        categories = {}
        for f in fields:
            cat = f.category
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1
            
        print("\n--- Unique Categories ---")
        for cat in sorted(categories.keys()):
            print(f"'{cat}': {categories[cat]} fields")
            
        # Check for whitespace issues
        print("\n--- Whitespace / Case Check ---")
        seen_lower = {}
        for cat in categories:
            normalized = cat.strip().lower()
            if normalized in seen_lower:
                print(f"[WARN] Potential duplicate: '{cat}' vs '{seen_lower[normalized]}'")
            else:
                seen_lower[normalized] = cat

if __name__ == "__main__":
    inspect_categories()
