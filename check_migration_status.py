from project import create_app, db
from flask_migrate import Migrate, upgrade, current, history, heads
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from flask import Flask

app = create_app()

def check_status():
    with app.app_context():
        # Get DB revision
        conn = db.engine.connect()
        context = MigrationContext.configure(conn)
        current_rev = context.get_current_revision()
        print(f"Current DB Revision: {current_rev}")
        
        # Get Script Directory heads
        # This requires setting up Alembic config which Flask-Migrate does, 
        # but accessing internal API might be tricky without full config.
        # simpler: use flask db commands via subprocess if possible, or just trust the DB revision print.
        
        # If we can import the script directory
        try:
            config = app.extensions['migrate'].migrate.get_config()
            script = ScriptDirectory.from_config(config)
            print(f"Codebase Heads: {script.get_heads()}")
        except Exception as e:
            print(f"Could not get codebase heads: {e}")

if __name__ == '__main__':
    check_status()
