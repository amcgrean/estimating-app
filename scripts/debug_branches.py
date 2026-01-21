import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from project import create_app, db
from project.models import Branch

app = create_app()
with app.app_context():
    branches = Branch.query.all()
    for b in branches:
        print(f"ID: {b.branch_id}, Name: '{b.branch_name}'")
