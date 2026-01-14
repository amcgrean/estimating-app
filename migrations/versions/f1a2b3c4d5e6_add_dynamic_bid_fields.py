"""add_dynamic_bid_fields

Revision ID: f1a2b3c4d5e6
Revises: e5f6a7b8c9d0
Create Date: 2026-01-14 10:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f1a2b3c4d5e6'
down_revision = 'e5f6a7b8c9d0'
branch_labels = None
depends_on = None


def upgrade():
    # Create BidField table
    op.create_table('bid_field',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('field_type', sa.String(length=50), nullable=False),
        sa.Column('is_required', sa.Boolean(), nullable=True),
        sa.Column('options', sa.Text(), nullable=True),
        sa.Column('default_value', sa.String(length=255), nullable=True),
        sa.Column('sort_order', sa.Integer(), nullable=True),
        sa.Column('branch_ids', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create BidValue table
    op.create_table('bid_value',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bid_id', sa.Integer(), nullable=False),
        sa.Column('field_id', sa.Integer(), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['bid_id'], ['bid.id'], ),
        sa.ForeignKeyConstraint(['field_id'], ['bid_field.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('bid_value')
    op.drop_table('bid_field')
