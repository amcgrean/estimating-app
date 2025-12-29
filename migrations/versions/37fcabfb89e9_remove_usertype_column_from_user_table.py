"""Remove usertype column from user table

Revision ID: 37fcabfb89e9
Revises: 8e62a2faaf6e
"""
from alembic import op
import sqlalchemy as sa

revision = "37fcabfb89e9"
down_revision = "8e62a2faaf6e"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)

    user_cols = {c["name"] for c in insp.get_columns("user")}

    # 1) If older schema had password_hash, rename it to password (only if needed)
    if "password_hash" in user_cols and "password" not in user_cols:
        op.alter_column("user", "password_hash", new_column_name="password")

    # 2) Drop old "usertype" column if it exists (some older schemas had this string column)
    user_cols = {c["name"] for c in insp.get_columns("user")}
    if "usertype" in user_cols:
        with op.batch_alter_table("user") as batch_op:
            batch_op.drop_column("usertype")


def downgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)

    user_cols = {c["name"] for c in insp.get_columns("user")}

    # Re-add usertype if it used to exist (nullable to be safe)
    if "usertype" not in user_cols:
        with op.batch_alter_table("user") as batch_op:
            batch_op.add_column(sa.Column("usertype", sa.String(length=50), nullable=True))

    # Rename password back to password_hash only if password_hash doesn't exist
    user_cols = {c["name"] for c in insp.get_columns("user")}
    if "password" in user_cols and "password_hash" not in user_cols:
        op.alter_column("user", "password", new_column_name="password_hash")
