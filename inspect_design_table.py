from project import create_app, db
from sqlalchemy import inspect

app = create_app()

def inspect_table():
    with app.app_context():
        inspector = inspect(db.engine)
        columns = inspector.get_columns('design')
        print("Columns in 'design' table:")
        for column in columns:
            print(f"- {column['name']}")

if __name__ == '__main__':
    inspect_table()
