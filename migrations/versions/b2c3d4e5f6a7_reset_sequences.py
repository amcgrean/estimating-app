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
    
    for table in tables:
        # Postgres specific command to reset sequence to max(id)
        # We use execute() to run raw SQL
        try:
             # This SQL resets the sequence associated with the 'id' column of the table
             # to the maximum value currently in the table.
             # pg_get_serial_sequence gets the sequence name automatically.
             conn.execute(sa.text(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE((SELECT MAX(id) FROM {table}), 0) + 1, false);"))
        except Exception as e:
            print(f"Warning: Could not reset sequence for {table}: {e}")
            # We don't raise here because some tables might not exist or have issues, 
            # and we want to try the others.


def downgrade():
    pass
