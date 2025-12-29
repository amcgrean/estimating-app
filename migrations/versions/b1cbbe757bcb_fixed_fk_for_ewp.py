"""fixed fk for ewp

Revision ID: b1cbbe757bcb
Revises: 23d505ddba37
Create Date: 2024-07-22 14:48:07.018322

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1cbbe757bcb'
down_revision = '23d505ddba37'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    constraints = [c['name'] for c in inspector.get_foreign_keys('user')]
    if 'user_ibfk_1' in constraints:
        op.drop_constraint('user_ibfk_1', 'user', type_='foreignkey')
    with op.batch_alter_table('user', schema=None) as batch_op:
       # batch_op.drop_constraint('user_ibfk_1', type_='foreignkey')
        batch_op.create_foreign_key('user_usertype_id_fkey', 'user_type', ['usertype_id'], ['id'])
        batch_op.create_foreign_key('user_estimator_id_fkey', 'estimator', ['estimatorID'], ['estimatorID'])
        batch_op.create_foreign_key('user_sales_rep_id_fkey', 'sales_rep', ['sales_rep_id'], ['id'])
        batch_op.create_foreign_key('user_branch_id_fkey', 'branch', ['user_branch_id'], ['branch_id'])

def downgrade():
    # Reverse the above commands if necessary
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('user_usertype_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('user_estimator_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('user_sales_rep_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('user_branch_id_fkey', type_='foreignkey')
        # Re-create any dropped constraints if necessary
