"""Remove usertype column from user table

Revision ID: 37fcabfb89e9
Revises: 8e62a2faaf6e
Create Date: 2024-07-16 20:04:26.480395

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '37fcabfb89e9'
down_revision = '8e62a2faaf6e'
branch_labels = None
depends_on = None

def upgrade():
    # Rename 'password_hash' column back to 'password'
    with op.batch_alter_table('user') as batch_op:
        batch_op.alter_column('password_hash', new_column_name='password')


def downgrade():
    # Rename 'password' column back to 'password_hash' if downgrading
    with op.batch_alter_table('user') as batch_op:
        batch_op.alter_column('password', new_column_name='password_hash')