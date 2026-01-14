"""Add BidFile model

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-01-13 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c3d4e5f6a7b8'
down_revision = 'd9319f6e738f'
branch_labels = None
depends_on = None


def upgrade():
    # Create bid_file table
    op.create_table('bid_file',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bid_id', sa.Integer(), nullable=False),
        sa.Column('file_key', sa.String(length=255), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['bid_id'], ['bid.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('bid_file')
