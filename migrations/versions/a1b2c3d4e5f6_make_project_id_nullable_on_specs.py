"""Make project_id nullable on specs

Revision ID: a1b2c3d4e5f6
Revises: 5210bd32aa77
Create Date: 2026-01-13 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '5210bd32aa77'
branch_labels = None
depends_on = None


def upgrade():
    tables = ['framing', 'siding', 'shingle', 'deck', 'trim', 'window', 'door']
    
    for table_name in tables:
        with op.batch_alter_table(table_name) as batch_op:
            batch_op.alter_column('project_id',
               existing_type=sa.Integer(),
               nullable=True)


def downgrade():
    tables = ['framing', 'siding', 'shingle', 'deck', 'trim', 'window', 'door']
    
    for table_name in tables:
        with op.batch_alter_table(table_name) as batch_op:
            batch_op.alter_column('project_id',
               existing_type=sa.Integer(),
               nullable=False)
