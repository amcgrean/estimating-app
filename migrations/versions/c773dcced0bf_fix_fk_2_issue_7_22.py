"""fix fk 2 issue 7.22

Revision ID: c773dcced0bf
Revises: 7b8c9ff662b9
Create Date: 2024-07-22 19:42:40.208238

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c773dcced0bf'
down_revision = '7b8c9ff662b9'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_foreign_key('fk_sales_rep_id', 'sales_rep', ['sales_rep_id'], ['id'])
        batch_op.create_foreign_key('fk_usertype_id', 'user_type', ['usertype_id'], ['id'])
        batch_op.create_foreign_key('fk_user_branch_id', 'branch', ['user_branch_id'], ['branch_id'])
        batch_op.create_foreign_key('fk_estimator_id', 'estimator', ['estimatorID'], ['estimatorID'])

def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('fk_sales_rep_id', type_='foreignkey')
        batch_op.drop_constraint('fk_usertype_id', type_='foreignkey')
        batch_op.drop_constraint('fk_user_branch_id', type_='foreignkey')
        batch_op.drop_constraint('fk_estimator_id', type_='foreignkey')