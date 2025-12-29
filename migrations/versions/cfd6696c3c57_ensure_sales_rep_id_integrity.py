"""Ensure sales_rep_id integrity

Revision ID: cfd6696c3c57
Revises: b1cbbe757bcb
Create Date: (leave as-is)

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = "cfd6696c3c57"
down_revision = "b1cbbe757bcb"
branch_labels = None
depends_on = None


def _has_column(inspector: Inspector, table_name: str, column_name: str) -> bool:
    cols = inspector.get_columns(table_name) or []
    return any(c.get("name") == column_name for c in cols)


def _foreign_keys(inspector: Inspector, table_name: str):
    return inspector.get_foreign_keys(table_name) or []


def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # If the column doesn't exist, nothing to enforce
    if not _has_column(inspector, "user", "sales_rep_id"):
        return

    # Drop any FK(s) that use sales_rep_id (names can vary across DBs/migrations)
    fks = _foreign_keys(inspector, "user")
    to_drop = []
    for fk in fks:
        cols = fk.get("constrained_columns") or []
        if "sales_rep_id" in cols and fk.get("name"):
            to_drop.append(fk["name"])

    if to_drop:
        with op.batch_alter_table("user", schema=None) as batch_op:
            for fk_name in to_drop:
                batch_op.drop_constraint(fk_name, type_="foreignkey")

    # Re-inspect and ensure the correct FK exists: user.sales_rep_id -> user.id
    inspector = Inspector.from_engine(conn)
    fks = _foreign_keys(inspector, "user")

    has_self_fk = any(
        ("sales_rep_id" in (fk.get("constrained_columns") or []))
        and fk.get("referred_table") == "user"
        for fk in fks
    )

    if not has_self_fk:
        with op.batch_alter_table("user", schema=None) as batch_op:
            batch_op.create_foreign_key(
                "fk_user_sales_rep_id",
                "user",
                ["sales_rep_id"],
                ["id"],
            )


def downgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    if not _has_column(inspector, "user", "sales_rep_id"):
        return

    # Best effort: drop the FK we created if it exists
    fks = _foreign_keys(inspector, "user")
    with op.batch_alter_table("user", schema=None) as batch_op:
        for fk in fks:
            if fk.get("name") == "fk_user_sales_rep_id":
                batch_op.drop_constraint("fk_user_sales_rep_id", type_="foreignkey")
