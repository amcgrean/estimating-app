"""Add EWP table

Revision ID: 27ec8156bda3
Revises: 2a08068b669f
Create Date: 2024-07-02 19:46:28.670040

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27ec8156bda3'
down_revision = '2a08068b669f'
branch_labels = None
depends_on = None


def upgrade():
    # Create ewp table
    op.create_table(
        'ewp',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('plan_number', sa.String(length=255), nullable=False),
        sa.Column('sales_rep_id', sa.String(length=255), nullable=False),
        sa.Column('customer', sa.String(length=255), nullable=False),
        sa.Column('address', sa.String(length=255), nullable=False),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('login_date', sa.Date, nullable=False),
        sa.Column('tji_depth', sa.String(length=255), nullable=False),
        sa.Column('assigned_designer', sa.String(length=255), nullable=False),
        sa.Column('layout_finalized', sa.String(length=255), nullable=False),
        sa.Column('agility_quote', sa.Float, nullable=False),
        sa.Column('imported_stellar', sa.String(length=255), nullable=False)
    )


def downgrade():
    # Drop ewp table
    op.drop_table('ewp')