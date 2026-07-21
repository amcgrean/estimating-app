"""
Check for specific project names in Neon to see if they exist under different names or branches.
"""
from sqlalchemy import create_engine, text

NEON = 'postgresql://neondb_owner:npg_1E4CvgZbaVBW@ep-fragrant-waterfall-ad8fjcey-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'

def check_projects():
    engine = create_engine(NEON)
    projects_to_check = ['Jamie Hatch', 'Good Oak Builders', 'Truview-Shed', 'Renda Building']
    with engine.connect() as c:
        for p in projects_to_check:
            print(f"\nSearching for '{p}'...")
            res = c.execute(text(f"SELECT id, project_name, branch_id, customer_id FROM bid WHERE project_name ILIKE :p"), {'p': f'%{p}%'})
            rows = res.fetchall()
            if rows:
                for r in rows:
                    print(f"  ID: {r[0]}, Name: {r[1]}, Branch: {r[2]}, CustomerID: {r[3]}")
            else:
                print("  No matches found.")

if __name__ == "__main__":
    check_projects()
