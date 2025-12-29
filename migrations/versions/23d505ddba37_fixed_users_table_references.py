"""fixed users table references

Revision ID: 23d505ddba37
Revises: cc0d1f788bac
Create Date: (leave as-is / not important)

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = "23d505ddba37"
down_revision = "cc0d1f788bac"
branch_labels = None
depends_on = None


def _fk_names(inspector: Inspector, table_name: str) -> set[str]:
    """Return a set of FK constraint names for a given table."""
    fks = inspector.get_foreign_keys(table_name) or []
    return {fk.get("name") for fk in fks if fk.get("name")}


def _has_column(inspector: Inspector, table_name: str, column_name: str) -> bool:
    cols = inspector.get_columns(table_name) or []
    return any(c.get("name") == column_name for c in cols)


def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Current FK names on the user table
    existing_fks = _fk_names(inspector, "user")

    # Drop old/incorrect FK(s) if they exist
    with op.batch_alter_table("user", schema=None) as batch_op:
        if "fk_user_usertype_id" in existing_fks:
            batch_op.drop_constraint("fk_user_usertype_id", type_="foreignkey")

        # If you previously had a FK pointing to a non-existent sales_rep table, remove it too
        if "fk_user_sales_rep_id" in existing_fks:
            batch_op.drop_constraint("fk_user_sales_rep_id", type_="foreignkey")

    # Recreate the "sales_rep_id -> user.id" FK if the column exists (self-referential)
    # Re-inspect after dropping constraints
    inspector = Inspector.from_engine(conn)
    existing_fks = _fk_names(inspector, "user")

    with op.batch_alter_table("user", schema=None) as batch_op:
        if (
            _has_column(inspector, "user", "sales_rep_id")
            and "fk_user_sales_rep_id" not in existing_fks
        ):
            batch_op.create_foreign_key(
                "fk_user_sales_rep_id",
                "user",
                ["sales_rep_id"],
                ["id"],
            )

    # Note: if your model no longer has usertype_id, we do NOT recreate it here.


def downgrade():
    # Downgrade is best-effort; only revert what we safely can.
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    existing_fks = _fk_names(inspector, "user")

    with op.batch_alter_table("user", schema=None) as batch_op:
        if "fk_user_sales_rep_id" in existing_fks:
            batch_op.drop_constraint("fk_user_sales_rep_id", type_="foreignkey")
