"""Add customer_id to Project table

Revision ID: f0c6376ba5fb
Revises: 67a0a2ddbbaa
Create Date: 2024-12-01 02:15:51.901932

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0c6376ba5fb'
down_revision = '67a0a2ddbbaa'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.add_column(sa.Column('customer_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_projects_customer', 'customer', ['customer_id'], ['id'])

def downgrade():
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.drop_constraint('fk_projects_customer', type_='foreignkey')
        batch_op.drop_column('customer_id')
