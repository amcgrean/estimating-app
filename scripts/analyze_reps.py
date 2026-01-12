from project import create_app, db
from project.models import Customer, SalesRep

app = create_app()

def analyze_matching():
    with app.app_context():
        customers = Customer.query.all()
        sales_reps = SalesRep.query.all()
        
        rep_map = {r.name.lower(): r.id for r in sales_reps}
        
        matches = 0
        mismatches = 0
        missing_agent = 0
        
        for c in customers:
            if not c.sales_agent:
                missing_agent += 1
                continue
                
            agent_name = c.sales_agent.strip().lower()
            if agent_name in rep_map:
                matches += 1
            else:
                mismatches += 1
                if mismatches < 5:
                    print(f"Mismatch: Customer '{c.name}' has agent '{c.sales_agent}' - Not found in SalesRep table.")
        
        print(f"\nStats:")
        print(f"Total Customers: {len(customers)}")
        print(f"Total Sales Reps: {len(sales_reps)}")
        print(f"Matches: {matches}")
        print(f"Mismatches: {mismatches}")
        print(f"Missing Agent: {missing_agent}")

if __name__ == "__main__":
    analyze_matching()
