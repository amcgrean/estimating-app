"""add branch table

Revision ID: 38c9830b0e51
Revises: 154ff894bf82
Create Date: 2024-07-18 21:56:12.183421

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '38c9830b0e51'
down_revision = '154ff894bf82'
branch_labels = None
depends_on = None


def upgrade():
    # Create the branch table

    # Insert initial data into the branch table
    branch_table = sa.table(
        'branch',
        sa.Column('branch_id', sa.Integer()),
        sa.Column('branch_name', sa.String()),
        sa.Column('branch_code', sa.String()),
        sa.Column('branch_type', sa.Integer())
    )
    op.bulk_insert(
        branch_table,
        [
            {'branch_id': 1, 'branch_name': 'Grimes', 'branch_code': '20GR', 'branch_type': 1},
            {'branch_id': 2, 'branch_name': 'Fort Dodge', 'branch_code': '10FD', 'branch_type': 1},
            {'branch_id': 3, 'branch_name': 'Coralville', 'branch_code': '40CV', 'branch_type': 1},
            {'branch_id': 4, 'branch_name': 'Birchwood', 'branch_code': '25BW', 'branch_type': 1},
        ]
    )

    # Add user_branch_id to the user table using batch_alter_table for SQLite
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_branch_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_user_branch_id', 'branch', ['user_branch_id'], ['branch_id'])

    # Update existing users to have user_branch_id = 1 (Grimes)
    op.execute('UPDATE user SET user_branch_id = 1')

def downgrade():
    # Drop foreign key and column from user table using batch_alter_table for SQLite
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('fk_user_branch_id', type_='foreignkey')
        batch_op.drop_column('user_branch_id')

    # Drop branch table
    op.drop_table('branch')