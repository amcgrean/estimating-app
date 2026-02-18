from project import create_app, db
from project.models import NotificationLog

app = create_app()

def create_table():
    with app.app_context():
        try:
            # Check if table exists
            inspector = db.inspect(db.engine)
            if 'notification_log' not in inspector.get_table_names():
                print("Creating notification_log table...")
                NotificationLog.__table__.create(db.engine)
                print("Table created successfully.")
            else:
                print("Table 'notification_log' already exists.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    create_table()
