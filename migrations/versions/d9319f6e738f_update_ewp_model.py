from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import Date, String, Integer, ForeignKey, Text

# revision identifiers, used by Alembic.
revision = 'd9319f6e738f'
down_revision = 'c773dcced0bf'
branch_labels = None
depends_on = None

def upgrade():
    # Create a temporary table with the desired structure
    op.create_table(
        'ewp_tmp',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('plan_number', sa.String(255), nullable=False),
        sa.Column('sales_rep_id', sa.Integer, sa.ForeignKey('user.id'), nullable=True),
        sa.Column('customer_id', sa.Integer, sa.ForeignKey('customer.id'), nullable=False),
        sa.Column('address', sa.String(255), nullable=False),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('login_date', sa.Date, nullable=False),
        sa.Column('tji_depth', sa.String(255), nullable=False),
        sa.Column('assigned_designer', sa.String(255), nullable=True),
        sa.Column('layout_finalized', sa.Date, nullable=True),
        sa.Column('agility_quote', sa.Date, nullable=True),
        sa.Column('imported_stellar', sa.Date, nullable=True),
        sa.Column('last_updated_by', sa.String(150), nullable=True),
        sa.Column('last_updated_at', sa.DateTime, nullable=True, default=sa.func.now())
    )

    # Copy data from the old table to the new table
    op.execute('''
        INSERT INTO ewp_tmp (
            id, plan_number, sales_rep_id, customer_id, address, notes, login_date,
            tji_depth, assigned_designer, layout_finalized, agility_quote, imported_stellar,
            last_updated_by, last_updated_at
        )
        SELECT 
            id, plan_number, sales_rep_id, customer_id, address, notes, login_date,
            tji_depth, assigned_designer, layout_finalized, agility_quote, imported_stellar,
            last_updated_by, last_updated_at
        FROM ewp
    ''')

    # Drop the old table
    op.drop_table('ewp')

    # Rename the new table to the original name
    op.rename_table('ewp_tmp', 'ewp')

def downgrade():
    # Create the original table structure
    op.create_table(
        'ewp_tmp',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('plan_number', sa.String(255), nullable=False),
        sa.Column('sales_rep_id', sa.Integer, sa.ForeignKey('user.id'), nullable=True),
        sa.Column('customer_id', sa.Integer, sa.ForeignKey('customer.id'), nullable=True),
        sa.Column('address', sa.String(255), nullable=False),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('login_date', sa.Date, nullable=False),
        sa.Column('tji_depth', sa.String(255), nullable=False),
        sa.Column('assigned_designer', sa.String(255), nullable=True),
        sa.Column('layout_finalized', sa.Date, nullable=True),
        sa.Column('agility_quote', sa.Float, nullable=True),
        sa.Column('imported_stellar', sa.String(255), nullable=True),
        sa.Column('last_updated_by', sa.String(150), nullable=True),
        sa.Column('last_updated_at', sa.DateTime, nullable=True, default=sa.func.now())
    )

    # Copy data from the new table to the original table
    op.execute('''
        INSERT INTO ewp_tmp (
            id, plan_number, sales_rep_id, customer_id, address, notes, login_date,
            tji_depth, assigned_designer, layout_finalized, agility_quote, imported_stellar,
            last_updated_by, last_updated_at
        )
        SELECT 
            id, plan_number, sales_rep_id, customer_id, address, notes, login_date,
            tji_depth, assigned_designer, layout_finalized, agility_quote, imported_stellar,
            last_updated_by, last_updated_at
        FROM ewp
    ''')

    # Drop the new table
    op.drop_table('ewp')

    # Rename the original table to the original name
    op.rename_table('ewp_tmp', 'ewp')
