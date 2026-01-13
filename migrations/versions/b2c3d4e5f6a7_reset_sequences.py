"""Reset sequences for spec tables

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-01-13 15:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # List of tables to reset sequences for
    tables = ['framing', 'siding', 'shingle', 'deck', 'trim', 'window', 'door']
    
    conn = op.get_bind()
    
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_tables_names()

    for table in tables:
        if table in existing_tables:
            columns = [c['name'] for c in inspector.get_columns(table)]
            if 'id' in columns:
                # Reset sequence safely
                op.execute(sa.text(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE((SELECT MAX(id) FROM {table}), 0) + 1, false);"))
            else:
                print(f"Skipping {table}: 'id' column not found.")
        else:
            print(f"Skipping {table}: Table not found.")


def downgrade():
    pass
