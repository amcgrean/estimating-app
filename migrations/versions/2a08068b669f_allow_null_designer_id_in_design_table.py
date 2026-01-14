"""Allow null designer_id in Design table

Revision ID: 2a08068b669f
Revises: manual_initial
Create Date: 2024-05-22 19:21:10.557607

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '2a08068b669f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Postgres-safe: just drop NOT NULL on designer_id.
    # Also safe on SQLite: Alembic will attempt the best it can, but for your new
    # Postgres deployment this is the correct operation.
    op.alter_column(
        "design",
        "designer_id",
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade():
    # Restore NOT NULL on designer_id
    op.alter_column(
        "design",
        "designer_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
