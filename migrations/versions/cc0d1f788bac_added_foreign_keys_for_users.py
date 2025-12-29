"""added foreign keys for users

Revision ID: cc0d1f788bac
Revises: 38c9830b0e51
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

revision = "cc0d1f788bac"
down_revision = "38c9830b0e51"
branch_labels = None
depends_on = None


def _has_column(inspector, table_name: str, col_name: str) -> bool:
    return col_name in [c["name"] for c in inspector.get_columns(table_name)]


def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # --- USER TABLE ---
    if not inspector.has_table("user"):
        # If your DB ever changed naming, better to fail loudly
        raise RuntimeError('Table "user" not found. Check earlier migrations / naming.')

    # Make sure required FK columns exist before adding constraints
    with op.batch_alter_table("user", schema=None) as batch_op:
        if not _has_column(inspector, "user", "usertype_id"):
            batch_op.add_column(sa.Column("usertype_id", sa.Integer(), nullable=True))

        if not _has_column(inspector, "user", "estimatorID"):
            batch_op.add_column(sa.Column("estimatorID", sa.Integer(), nullable=True))

        if not _has_column(inspector, "user", "sales_rep_id"):
            batch_op.add_column(sa.Column("sales_rep_id", sa.Integer(), nullable=True))

        if not _has_column(inspector, "user", "user_branch_id"):
            batch_op.add_column(sa.Column("user_branch_id", sa.Integer(), nullable=True))

    # Refresh inspector after potential column adds
    inspector = Inspector.from_engine(conn)

    # Add constraints (only if they don't already exist)
    existing_fks = {fk["name"] for fk in inspector.get_foreign_keys("user") if fk.get("name")}

    with op.batch_alter_table("user", schema=None) as batch_op:
        if "fk_user_usertype_id" not in existing_fks and _has_column(inspector, "user", "usertype_id"):
            batch_op.create_foreign_key(
                "fk_user_usertype_id",
                "user_type",
                ["usertype_id"],
                ["id"],
            )

        if "fk_user_estimatorID" not in existing_fks and _has_column(inspector, "user", "estimatorID"):
            batch_op.create_foreign_key(
                "fk_user_estimatorID",
                "estimator",
                ["estimatorID"],
                ["estimatorID"],
            )

        if "fk_user_sales_rep_id" not in existing_fks and _has_column(inspector, "user", "sales_rep_id"):
            # sales_rep is a User (self-referential FK)
            batch_op.create_foreign_key(
                "fk_user_sales_rep_id",
                "user",
                ["sales_rep_id"],
        ["id"],
    )

        if "fk_user_branch_id" not in existing_fks and _has_column(inspector, "user", "user_branch_id"):
            batch_op.create_foreign_key(
                "fk_user_branch_id",
                "branch",
                ["user_branch_id"],
                ["branch_id"],
            )

    # Optional: if you truly require usertype_id NOT NULL, enforce it AFTER you’ve populated data.
    # For now keep it nullable so migrations can succeed cleanly.


def downgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    existing_fks = {fk["name"] for fk in inspector.get_foreign_keys("user") if fk.get("name")}

    with op.batch_alter_table("user", schema=None) as batch_op:
        if "fk_user_branch_id" in existing_fks:
            batch_op.drop_constraint("fk_user_branch_id", type_="foreignkey")
        if "fk_user_sales_rep_id" in existing_fks:
            batch_op.drop_constraint("fk_user_sales_rep_id", type_="foreignkey")
        if "fk_user_estimatorID" in existing_fks:
            batch_op.drop_constraint("fk_user_estimatorID", type_="foreignkey")
        if "fk_user_usertype_id" in existing_fks:
            batch_op.drop_constraint("fk_user_usertype_id", type_="foreignkey")
        

    # Don't automatically drop columns in downgrade; too risky for your historical DB.
