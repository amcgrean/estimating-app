"""Add createdDate to ITService

Revision ID: 03adb408fbb3
Revises: 3ca35f57f7f4
Create Date: 2024-10-24 16:27:06.298459

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03adb408fbb3'
down_revision = '3ca35f57f7f4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('it_service', sa.Column('createdDate', sa.DateTime(), nullable=True))



def downgrade():
    op.drop_column('it_service', 'createdDate')
