"""Add missing columns to bid table

Revision ID: 4f90106c22bb
Revises: 3c1bcb97367e
Create Date: 2026-01-13 10:00:09.356262

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4f90106c22bb'
down_revision = '3c1bcb97367e'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('bid') as batch_op:
        batch_op.add_column(sa.Column('bid_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('flexible_bid_date', sa.Boolean(), server_default='0', nullable=True))
        batch_op.add_column(sa.Column('include_specs', sa.Boolean(), server_default='0', nullable=True))
        batch_op.add_column(sa.Column('framing_notes', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('siding_notes', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('deck_notes', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('trim_notes', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('window_notes', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('door_notes', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('shingle_notes', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('plan_filename', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('email_filename', sa.String(length=255), nullable=True))


def downgrade():
    with op.batch_alter_table('bid') as batch_op:
        batch_op.drop_column('email_filename')
        batch_op.drop_column('plan_filename')
        batch_op.drop_column('shingle_notes')
        batch_op.drop_column('door_notes')
        batch_op.drop_column('window_notes')
        batch_op.drop_column('trim_notes')
        batch_op.drop_column('deck_notes')
        batch_op.drop_column('siding_notes')
        batch_op.drop_column('framing_notes')
        batch_op.drop_column('include_specs')
        batch_op.drop_column('flexible_bid_date')
        batch_op.drop_column('bid_date')
