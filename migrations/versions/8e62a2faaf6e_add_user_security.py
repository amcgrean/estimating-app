"""add user security

Revision ID: 8e62a2faaf6e
Revises: 4d2bd2b561f9
Create Date: 2024-07-15 19:29:39.561145

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8e62a2faaf6e'
down_revision = '4d2bd2b561f9'
branch_labels = None
depends_on = None


def upgrade():
    # Create user_security table
    op.create_table(
        'user_security',
        sa.Column('user_type_id', sa.Integer, sa.ForeignKey('user_type.id'), primary_key=True),
        sa.Column('admin', sa.Boolean, nullable=False),
        sa.Column('estimating', sa.Boolean, nullable=False),
        sa.Column('bid_request', sa.Boolean, nullable=False),
        sa.Column('design', sa.Boolean, nullable=False),
        sa.Column('ewp', sa.Boolean, nullable=False),
        sa.Column('service', sa.Boolean, nullable=False),
        sa.Column('install', sa.Boolean, nullable=False),
        sa.Column('picking', sa.Boolean, nullable=False),
        sa.Column('work_orders', sa.Boolean, nullable=False),
        sa.Column('dashboards', sa.Boolean, nullable=False),
        sa.Column('security_10', sa.Boolean, nullable=False),
        sa.Column('security_11', sa.Boolean, nullable=False),
        sa.Column('security_12', sa.Boolean, nullable=False),
        sa.Column('security_13', sa.Boolean, nullable=False),
        sa.Column('security_14', sa.Boolean, nullable=False),
        sa.Column('security_15', sa.Boolean, nullable=False),
        sa.Column('security_16', sa.Boolean, nullable=False),
        sa.Column('security_17', sa.Boolean, nullable=False),
        sa.Column('security_18', sa.Boolean, nullable=False),
        sa.Column('security_19', sa.Boolean, nullable=False),
        sa.Column('security_20', sa.Boolean, nullable=False)
    )

def downgrade():
    op.drop_table('user_security')