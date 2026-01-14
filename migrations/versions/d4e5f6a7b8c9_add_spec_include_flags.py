"""Add spec include flags

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-01-13 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4e5f6a7b8c9'
down_revision = '2a08068b669f'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('bid')]

    # Add new boolean columns to bid table if they don't exist
    new_bool_cols = [
        'include_specs', 'include_framing', 'include_siding', 
        'include_shingle', 'include_deck', 'include_trim', 
        'include_window', 'include_door', 'flexible_bid_date'
    ]

    for col in new_bool_cols:
        if col not in columns:
            op.add_column('bid', sa.Column(col, sa.Boolean(), server_default='false', nullable=True))

    # Add date field
    if 'bid_date' not in columns:
        op.add_column('bid', sa.Column('bid_date', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('bid', 'include_specs')
    op.drop_column('bid', 'include_framing')
    op.drop_column('bid', 'include_siding')
    op.drop_column('bid', 'include_shingle')
    op.drop_column('bid', 'include_deck')
    op.drop_column('bid', 'include_trim')
    op.drop_column('bid', 'include_window')
    op.drop_column('bid', 'include_door')
    op.drop_column('bid', 'bid_date')
    op.drop_column('bid', 'flexible_bid_date')
