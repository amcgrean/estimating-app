"""created usertype

Revision ID: d9191b399b50
Revises: c7317a8949d5
"""
from alembic import op
import sqlalchemy as sa

revision = "d9191b399b50"
down_revision = "c7317a8949d5"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_type",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=50), nullable=False, unique=True),
    )


def downgrade():
    op.drop_table("user_type")
