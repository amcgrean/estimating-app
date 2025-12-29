"""add branch table

Revision ID: 38c9830b0e51
Revises: 154ff894bf82
"""
from alembic import op
import sqlalchemy as sa

revision = "38c9830b0e51"
down_revision = "154ff894bf82"
branch_labels = None
depends_on = None


def upgrade():
    # 1) Create the table (name MUST be "branch" to match your FK usage: branch.branch_id)
    op.create_table(
        "branch",
        sa.Column("branch_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("branch_name", sa.String(length=255), nullable=False),
        sa.Column("branch_code", sa.String(length=255), nullable=False, unique=True),
        sa.Column("branch_type", sa.Integer(), nullable=False),
    )

    # 2) Seed initial branches
    branch_table = sa.table(
        "branch",
        sa.column("branch_id", sa.Integer()),
        sa.column("branch_name", sa.String()),
        sa.column("branch_code", sa.String()),
        sa.column("branch_type", sa.Integer()),
    )

    op.bulk_insert(
        branch_table,
        [
            {"branch_id": 1, "branch_name": "Grimes",     "branch_code": "20GR", "branch_type": 1},
            {"branch_id": 2, "branch_name": "Fort Dodge", "branch_code": "10FD", "branch_type": 1},
            {"branch_id": 3, "branch_name": "Coralville", "branch_code": "40CV", "branch_type": 1},
            {"branch_id": 4, "branch_name": "Birchwood",  "branch_code": "25BW", "branch_type": 1},
        ],
    )


def downgrade():
    op.drop_table("branch")
