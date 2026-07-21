from project import create_app, db
from project.models import Customer
app = create_app()
with app.app_context():
    codes = ['QUOT2025', 'QUOT2026']
    customers = Customer.query.filter(Customer.customerCode.in_(codes)).all()
    if not customers:
        print("No customers found for QUOT2025/2026")
    for c in customers:
        print(f"Found Customer: {c.customerCode} - {c.name}")
