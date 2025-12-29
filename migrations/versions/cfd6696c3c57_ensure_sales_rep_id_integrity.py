"""Ensure sales_rep_id integrity

Revision ID: cfd6696c3c57
Revises: b1cbbe757bcb
Create Date: 2024-07-22 19:34:11.038837

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cfd6696c3c57'
down_revision = 'b1cbbe757bcb'
branch_labels = None
depends_on = None


# migration script

def upgrade():
    # Ensure sales_rep_id column exists and is correctly referenced
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_foreign_key('fk_sales_rep_id', 'sales_rep', ['sales_rep_id'], ['id'])

def downgrade():
    # Optionally remove the foreign key constraint
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('fk_sales_rep_id', type_='foreignkey')
