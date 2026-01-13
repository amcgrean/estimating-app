"""Link detailed specs tables to Bid table

Revision ID: 5210bd32aa77
Revises: 4f90106c22bb
Create Date: 2026-01-13 11:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5210bd32aa77'
down_revision = '4f90106c22bb'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = ['framing', 'siding', 'shingle', 'deck', 'trim', 'window', 'door']
    
    for table_name in tables:
        columns = [c['name'] for c in inspector.get_columns(table_name)]
        if 'bid_id' not in columns:
            with op.batch_alter_table(table_name) as batch_op:
                batch_op.add_column(sa.Column('bid_id', sa.Integer(), nullable=True))
                batch_op.create_foreign_key(f'fk_{table_name}_bid_id', 'bid', ['bid_id'], ['id'])


def downgrade():
    tables = ['framing', 'siding', 'shingle', 'deck', 'trim', 'window', 'door']
    
    for table_name in tables:
        with op.batch_alter_table(table_name) as batch_op:
            batch_op.drop_constraint(f'fk_{table_name}_bid_id', type_='foreignkey')
            batch_op.drop_column('bid_id')
