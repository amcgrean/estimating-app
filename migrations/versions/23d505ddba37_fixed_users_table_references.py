from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

revision = '23d505ddba37'
down_revision = 'cc0d1f788bac'
branch_labels = None
depends_on = None

def upgrade():
    # Start batch operation for SQLite
    with op.batch_alter_table('user', schema=None) as batch_op:
        # Manually handle foreign key constraints
        batch_op.drop_constraint('fk_user_usertype_id', type_='foreignkey', if_exists=True)
        batch_op.drop_constraint('fk_user_estimatorID', type_='foreignkey', if_exists=True)
        batch_op.drop_constraint('fk_user_sales_rep_id', type_='foreignkey', if_exists=True)
        batch_op.drop_constraint('fk_user_branch_id', type_='foreignkey', if_exists=True)

        # Recreate foreign keys
        batch_op.create_foreign_key('fk_user_usertype_id', 'user_type', ['usertype_id'], ['id'])
        batch_op.create_foreign_key('fk_user_estimatorID', 'estimator', ['estimatorID'], ['estimatorID'])
        batch_op.create_foreign_key('fk_user_sales_rep_id', 'sales_rep', ['sales_rep_id'], ['id'])
        batch_op.create_foreign_key('fk_user_branch_id', 'branch', ['user_branch_id'], ['branch_id'])

def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('fk_user_usertype_id', type_='foreignkey', if_exists=True)
        batch_op.drop_constraint('fk_user_estimatorID', type_='foreignkey', if_exists=True)
        batch_op.drop_constraint('fk_user_sales_rep_id', type_='foreignkey', if_exists=True)
        batch_op.drop_constraint('fk_user_branch_id', type_='foreignkey', if_exists=True)
