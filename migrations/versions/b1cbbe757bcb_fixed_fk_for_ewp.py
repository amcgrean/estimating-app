"""fixed fk for ewp

Revision ID: b1cbbe757bcb
Revises: 23d505ddba37
Create Date: (leave as-is)

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = "b1cbbe757bcb"
down_revision = "23d505ddba37"
branch_labels = None
depends_on = None


def _fk_info(inspector: Inspector, table_name: str):
    return inspector.get_foreign_keys(table_name) or []


def _has_column(inspector: Inspector, table_name: str, column_name: str) -> bool:
    cols = inspector.get_columns(table_name) or []
    return any(c.get("name") == column_name for c in cols)


def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # ---- Fix user.sales_rep_id FK (sales_rep table does NOT exist) ----
    if _has_column(inspector, "user", "sales_rep_id"):
        fks = _fk_info(inspector, "user")

        # Drop ANY FK that uses local column sales_rep_id (name may vary)
        to_drop = []
        for fk in fks:
            constrained_cols = fk.get("constrained_columns") or []
            if "sales_rep_id" in constrained_cols and fk.get("name"):
                to_drop.append(fk["name"])

        with op.batch_alter_table("user", schema=None) as batch_op:
            for fk_name in to_drop:
                batch_op.drop_constraint(fk_name, type_="foreignkey")

        # Re-inspect, then ensure correct self-referential FK exists
        inspector = Inspector.from_engine(conn)
        fks = _fk_info(inspector, "user")

        already_has_user_fk = any(
            ("sales_rep_id" in (fk.get("constrained_columns") or []))
            and (fk.get("referred_table") == "user")
            for fk in fks
        )

        if not already_has_user_fk:
            with op.batch_alter_table("user", schema=None) as batch_op:
                batch_op.create_foreign_key(
                    "fk_user_sales_rep_id",
                    "user",
                    ["sales_rep_id"],
                    ["id"],
                )

    # ---- Fix EWP foreign keys safely ----
    inspector = Inspector.from_engine(conn)

    if _has_column(inspector, "ewp", "sales_rep_id") or _has_column(inspector, "ewp", "customer_id"):
        fks = _fk_info(inspector, "ewp")

        # Drop incorrect FK(s) if present
        drop_names = []
        for fk in fks:
            name = fk.get("name")
            cols = fk.get("constrained_columns") or []
            referred_table = fk.get("referred_table")
            # If sales_rep_id points anywhere other than user, drop it
            if "sales_rep_id" in cols and name and referred_table != "user":
                drop_names.append(name)
            # If customer_id points anywhere other than customer, drop it
            if "customer_id" in cols and name and referred_table != "customer":
                drop_names.append(name)

        with op.batch_alter_table("ewp", schema=None) as batch_op:
            for fk_name in set(drop_names):
                batch_op.drop_constraint(fk_name, type_="foreignkey")

        # Re-inspect then create correct FK(s) if missing
        inspector = Inspector.from_engine(conn)
        fks = _fk_info(inspector, "ewp")

        has_salesrep_fk = any(
            ("sales_rep_id" in (fk.get("constrained_columns") or []))
            and fk.get("referred_table") == "user"
            for fk in fks
        )
        has_customer_fk = any(
            ("customer_id" in (fk.get("constrained_columns") or []))
            and fk.get("referred_table") == "customer"
            for fk in fks
        )

        with op.batch_alter_table("ewp", schema=None) as batch_op:
            if _has_column(inspector, "ewp", "sales_rep_id") and not has_salesrep_fk:
                batch_op.create_foreign_key(
                    "fk_ewp_sales_rep_id",
                    "user",
                    ["sales_rep_id"],
                    ["id"],
                )
            if _has_column(inspector, "ewp", "customer_id") and not has_customer_fk:
                batch_op.create_foreign_key(
                    "fk_ewp_customer_id",
                    "customer",
                    ["customer_id"],
                    ["id"],
                )


def downgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Best-effort: remove the FKs we might have created
    with op.batch_alter_table("ewp", schema=None) as batch_op:
        for fk in _fk_info(inspector, "ewp"):
            if fk.get("name") in {"fk_ewp_sales_rep_id", "fk_ewp_customer_id"}:
                batch_op.drop_constraint(fk["name"], type_="foreignkey")

    inspector = Inspector.from_engine(conn)
    with op.batch_alter_table("user", schema=None) as batch_op:
        for fk in _fk_info(inspector, "user"):
            if fk.get("name") == "fk_user_sales_rep_id":
                batch_op.drop_constraint(fk["name"], type_="foreignkey")
