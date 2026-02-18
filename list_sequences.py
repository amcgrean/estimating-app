from project import create_app, db
from sqlalchemy import text

app = create_app()

def list_sequences():
    with app.app_context():
        # Query for all sequences in the current search path
        sql = text("SELECT n.nspname as schema, c.relname as sequence FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace WHERE c.relkind = 'S'")
        result = db.session.execute(sql).fetchall()
        print("Available Sequences:")
        for r in result:
            print(f"- {r.schema}.{r.sequence}")

if __name__ == "__main__":
    list_sequences()
