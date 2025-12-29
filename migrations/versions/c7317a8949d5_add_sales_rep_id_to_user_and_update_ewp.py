"""Add sales_rep_id to User and update EWP

Revision ID: c7317a8949d5
Revises: 27ec8156bda3
Create Date: 2024-07-10 14:11:04.344181

"""
from alembic import op
import sqlalchemy as sa


revision = "c7317a8949d5"
down_revision = "27ec8156bda3"
branch_labels = None
depends_on = None


def _colmap(insp, table):
    # name -> dict(col info)
    return {c["name"]: c for c in insp.get_columns(table)}


def _fk_names(insp, table):
    return {fk.get("name") for fk in insp.get_foreign_keys(table)}


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # ---- USER: add sales_rep_id (int) if missing ----
    user_cols = _colmap(insp, "user")
    if "sales_rep_id" not in user_cols:
        op.add_column("user", sa.Column("sales_rep_id", sa.Integer(), nullable=True))

    # ---- EWP: ensure sales_rep_id/customer_id exist AND are integers ----
    ewp_cols = _colmap(insp, "ewp")

    # Add columns if missing
    with op.batch_alter_table("ewp", schema=None) as batch_op:
        if "sales_rep_id" not in ewp_cols:
            batch_op.add_column(sa.Column("sales_rep_id", sa.Integer(), nullable=True))
        if "customer_id" not in ewp_cols:
            batch_op.add_column(sa.Column("customer_id", sa.Integer(), nullable=True))

    # Refresh inspector view after DDL
    ewp_cols = _colmap(insp, "ewp")

    # If sales_rep_id exists but is NOT integer, convert it (Postgres only).
    # This protects you if an earlier migration created it as VARCHAR.
    sales_rep_id_col = ewp_cols.get("sales_rep_id")
    if sales_rep_id_col is not None:
        col_type = sales_rep_id_col["type"]
        # On Postgres, VARCHAR shows up like sa.VARCHAR()/sa.String()
        is_integer = isinstance(col_type, (sa.INTEGER, sa.Integer))
        if not is_integer:
            # Try to cast existing values (if any) to int; invalid casts become NULL
            # This is safe for an empty/new DB.
            op.execute("""
                ALTER TABLE ewp
                ALTER COLUMN sales_rep_id TYPE INTEGER
                USING NULLIF(trim(sales_rep_id::text), '')::integer
            """)

    # Same protection for customer_id (rare, but safe)
    ewp_cols = _colmap(insp, "ewp")
    customer_id_col = ewp_cols.get("customer_id")
    if customer_id_col is not None:
        col_type = customer_id_col["type"]
        is_integer = isinstance(col_type, (sa.INTEGER, sa.Integer))
        if not is_integer:
            op.execute("""
                ALTER TABLE ewp
                ALTER COLUMN customer_id TYPE INTEGER
                USING NULLIF(trim(customer_id::text), '')::integer
            """)

    # ---- Legacy data migration (only if old string cols exist) ----
    ewp_cols = _colmap(insp, "ewp")
    has_legacy_sales_rep = "sales_rep" in ewp_cols
    has_legacy_customer = "customer" in ewp_cols

    if has_legacy_sales_rep or has_legacy_customer:
        with op.batch_alter_table("ewp", schema=None) as batch_op:
            if "temp_sales_rep" not in ewp_cols:
                batch_op.add_column(sa.Column("temp_sales_rep", sa.String(255), nullable=True))
            if "temp_customer" not in ewp_cols:
                batch_op.add_column(sa.Column("temp_customer", sa.String(255), nullable=True))

        if has_legacy_sales_rep:
            op.execute("UPDATE ewp SET temp_sales_rep = sales_rep")
        if has_legacy_customer:
            op.execute("UPDATE ewp SET temp_customer = customer")

        op.execute("""
            UPDATE ewp
            SET sales_rep_id = u.id
            FROM "user" u
            WHERE ewp.temp_sales_rep IS NOT NULL
              AND u.username = ewp.temp_sales_rep
        """)

        op.execute("""
            UPDATE ewp
            SET customer_id = c.id
            FROM customer c
            WHERE ewp.temp_customer IS NOT NULL
              AND c.name = ewp.temp_customer
        """)

        # Drop legacy columns
        with op.batch_alter_table("ewp", schema=None) as batch_op:
            if has_legacy_sales_rep:
                batch_op.drop_column("sales_rep")
            if has_legacy_customer:
                batch_op.drop_column("customer")

        # Drop temps if present
        ewp_cols = _colmap(insp, "ewp")
        with op.batch_alter_table("ewp", schema=None) as batch_op:
            if "temp_sales_rep" in ewp_cols:
                batch_op.drop_column("temp_sales_rep")
            if "temp_customer" in ewp_cols:
                batch_op.drop_column("temp_customer")

    # ---- Foreign keys (only after types are correct) ----
    fk_names = _fk_names(insp, "ewp")
    with op.batch_alter_table("ewp", schema=None) as batch_op:
        if "fk_sales_rep_id" not in fk_names:
            batch_op.create_foreign_key("fk_sales_rep_id", "user", ["sales_rep_id"], ["id"])
        if "fk_customer_id" not in fk_names:
            batch_op.create_foreign_key("fk_customer_id", "customer", ["customer_id"], ["id"])


def downgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)

    fk_names = _fk_names(insp, "ewp")
    ewp_cols = _colmap(insp, "ewp")
    user_cols = _colmap(insp, "user")

    with op.batch_alter_table("ewp", schema=None) as batch_op:
        if "fk_customer_id" in fk_names:
            batch_op.drop_constraint("fk_customer_id", type_="foreignkey")
        if "fk_sales_rep_id" in fk_names:
            batch_op.drop_constraint("fk_sales_rep_id", type_="foreignkey")

        if "sales_rep" not in ewp_cols:
            batch_op.add_column(sa.Column("sales_rep", sa.String(255), nullable=True))
        if "customer" not in ewp_cols:
            batch_op.add_column(sa.Column("customer", sa.String(255), nullable=True))

        if "customer_id" in ewp_cols:
            batch_op.drop_column("customer_id")
        if "sales_rep_id" in ewp_cols:
            batch_op.drop_column("sales_rep_id")

    if "sales_rep_id" in user_cols:
        op.drop_column("user", "sales_rep_id")
