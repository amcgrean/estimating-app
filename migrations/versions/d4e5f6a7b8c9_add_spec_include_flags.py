"""Add spec include flags

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-01-13 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd4e5f6a7b8c9'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade():
    # Add new boolean columns to bid table
    # Using server_default ensures existing rows get False
    op.add_column('bid', sa.Column('include_specs', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('bid', sa.Column('include_framing', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('bid', sa.Column('include_siding', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('bid', sa.Column('include_shingle', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('bid', sa.Column('include_deck', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('bid', sa.Column('include_trim', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('bid', sa.Column('include_window', sa.Boolean(), server_default='false', nullable=True))
    op.add_column('bid', sa.Column('include_door', sa.Boolean(), server_default='false', nullable=True))
    
    # Add date fields
    op.add_column('bid', sa.Column('bid_date', sa.DateTime(), nullable=True))
    op.add_column('bid', sa.Column('flexible_bid_date', sa.Boolean(), server_default='false', nullable=True))


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
