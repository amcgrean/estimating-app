# migrations/versions/xxx_add_usertype_table_and_update_user_table.py

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = 'd9191b399b50'
down_revision = 'c7317a8949d5'
branch_labels = None
depends_on = None


def upgrade():
    # Create user_type table if it does not exist
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)

    if 'user_type' not in inspector.get_table_names():
        op.create_table(
            'user_type',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('name', sa.String(50), nullable=False, unique=True)
        )

        # Add some default user types
        op.bulk_insert(
            op.get_bind().table('user_type'),
            [
                {'id': 1, 'name': 'Admin'},
                {'id': 2, 'name': 'Sales Rep'},
                {'id': 3, 'name': 'Estimator'},
                {'id': 4, 'name': 'Designer'},
                {'id': 5, 'name': 'Service Tech'}
            ]
        )

    # Add usertype_id column to user table (initially nullable)
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('usertype_id', sa.Integer, nullable=True))
        batch_op.create_foreign_key('fk_usertype_id', 'user_type', ['usertype_id'], ['id'])

    # Update existing users to have a default usertype_id
    op.execute('UPDATE user SET usertype_id = 1')  # Setting default to 'Admin'

    # Alter the column to be non-nullable
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('usertype_id', existing_type=sa.Integer, nullable=False)


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('fk_usertype_id', type_='foreignkey')
        batch_op.drop_column('usertype_id')
    op.drop_table('user_type')
