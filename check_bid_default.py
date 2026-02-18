from project import create_app, db
from sqlalchemy import text

app = create_app()

def inspect_default():
    with app.app_context():
        sql = text("SELECT column_name, column_default FROM information_schema.columns WHERE table_name = 'bid' AND column_name = 'id'")
        result = db.session.execute(sql).fetchone()
        print(f"Bid ID Default: {result}")

if __name__ == "__main__":
    inspect_default()
