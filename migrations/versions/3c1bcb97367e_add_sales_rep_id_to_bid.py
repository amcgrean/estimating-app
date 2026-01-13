"""Add sales_rep_id to Bid

Revision ID: 3c1bcb97367e
Revises: 5e5635f727fe
Create Date: 2026-01-12 16:52:48.020987

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3c1bcb97367e'
down_revision = '5e5635f727fe'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('bid')]
    if 'sales_rep_id' not in columns:
        with op.batch_alter_table('bid') as batch_op:
            batch_op.add_column(sa.Column('sales_rep_id', sa.Integer(), nullable=True))
            batch_op.create_foreign_key('fk_bid_sales_rep_id', 'sales_rep', ['sales_rep_id'], ['id'])


def downgrade():
    with op.batch_alter_table('bid') as batch_op:
        batch_op.drop_constraint('fk_bid_sales_rep_id', type_='foreignkey')
        batch_op.drop_column('sales_rep_id')
