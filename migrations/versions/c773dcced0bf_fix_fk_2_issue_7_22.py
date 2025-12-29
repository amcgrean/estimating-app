"""fix fk issue 7.22

Revision ID: 7b8c9ff662b9
Revises: cfd6696c3c57
Create Date: (leave as-is)

"""
from alembic import op
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = "c773dcced0bf"
down_revision = "cfd6696c3c57"
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

    # If no column, nothing to do
    if not _has_column(inspector, "user", "sales_rep_id"):
        return

    # Drop any existing FK(s) on user.sales_rep_id (names vary)
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

    # Ensure correct self-referential FK exists: user.sales_rep_id -> user.id
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

    # Drop the FK if it exists (best effort)
    fks = _foreign_keys(inspector, "user")
    with op.batch_alter_table("user", schema=None) as batch_op:
        for fk in fks:
            if fk.get("name") == "fk_user_sales_rep_id":
                batch_op.drop_constraint("fk_user_sales_rep_id", type_="foreignkey")
