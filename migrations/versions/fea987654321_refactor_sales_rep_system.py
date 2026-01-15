"""refactor_sales_rep_system

Revision ID: fea987654321
Revises: f1a2b3c4d5e6
Create Date: 2026-01-14 11:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fea987654321'
down_revision = 'f1a2b3c4d5e6'
branch_labels = None
depends_on = None


def upgrade():
    # Use raw SQL for robustness to avoid transaction aborts if constraints don't exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    table_names = inspector.get_table_names()
    
    # 1. Update Bid table
    op.execute("ALTER TABLE bid DROP CONSTRAINT IF EXISTS bid_sales_rep_id_fkey")
    op.create_foreign_key('fk_bid_sales_rep_user_id', 'bid', 'user', ['sales_rep_id'], ['id'])

    # 2. Update Project table
    if 'project' in table_names:
        op.execute("ALTER TABLE project DROP CONSTRAINT IF EXISTS project_sales_rep_id_fkey")
        op.create_foreign_key('fk_project_sales_rep_user_id', 'project', 'user', ['sales_rep_id'], ['id'])

    # 3. Clean up User table
    # Flask-SQLAlchemy default is camelCase -> snake_case. User -> user.
    op.execute("ALTER TABLE \"user\" DROP CONSTRAINT IF EXISTS user_sales_rep_id_fkey") 
    
    # Drop column safely
    op.execute("ALTER TABLE \"user\" DROP COLUMN IF EXISTS sales_rep_id")

    # 4. Drop SalesRep table
    op.execute("DROP TABLE IF EXISTS sales_rep CASCADE")


def downgrade():
    # 1. Re-create SalesRep table
    op.create_table('sales_rep',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # 2. Restore User table column
    op.add_column('user', sa.Column('sales_rep_id', sa.Integer(), nullable=True))
    op.create_foreign_key('user_sales_rep_id_fkey', 'user', 'sales_rep', ['sales_rep_id'], ['id'])

    # 3. Restore Bid table FK
    op.drop_constraint('fk_bid_sales_rep_user_id', 'bid', type_='foreignkey')
    op.create_foreign_key('bid_sales_rep_id_fkey', 'bid', 'sales_rep', ['sales_rep_id'], ['id'])

    # 4. Restore Project table FK
    try:
        op.drop_constraint('fk_project_sales_rep_user_id', 'project', type_='foreignkey')
        op.create_foreign_key('project_sales_rep_id_fkey', 'project', 'sales_rep', ['sales_rep_id'], ['id'])
    except Exception:
        pass
