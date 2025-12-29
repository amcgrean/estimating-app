"""Allow null designer_id in Design table

Revision ID: 2a08068b669f
Revises: manual_initial
Create Date: 2024-05-22 19:21:10.557607

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '2a08068b669f'
down_revision = 'manual_initial'
branch_labels = None
depends_on = None


def upgrade():
    # Create a new table with the modified structure
    op.create_table(
        'design_new',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('planNumber', sa.String(10), nullable=False, unique=True),
        sa.Column('plan_name', sa.String(100), nullable=False),
        sa.Column('customer_id', sa.Integer, sa.ForeignKey('customer.id'), nullable=False),
        sa.Column('project_address', sa.String(200), nullable=False),
        sa.Column('contractor', sa.String(100), nullable=True),
        sa.Column('log_date', sa.DateTime, default=datetime.utcnow),
        sa.Column('preliminary_set_date', sa.DateTime, nullable=True),
        sa.Column('designer_id', sa.Integer, sa.ForeignKey('estimator.estimatorID'), nullable=True),  # Changed to nullable=True
        sa.Column('status', sa.String(50), default='Active'),
        sa.Column('plan_description', sa.String(50), nullable=True),
        sa.Column('notes', sa.Text, nullable=True)
    )

    # Copy data from the old table to the new table
    op.execute('''
        INSERT INTO design_new (id, planNumber, plan_name, customer_id, project_address, contractor, log_date, preliminary_set_date, designer_id, status, plan_description, notes)
        SELECT id, planNumber, plan_name, customer_id, project_address, contractor, log_date, preliminary_set_date, designer_id, status, plan_description, notes
        FROM design
    ''')

    # Drop the old table
    op.drop_table('design')

    # Rename the new table to the old table name
    op.rename_table('design_new', 'design')


def downgrade():
    # Create the old table structure
    op.create_table(
        'design_old',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('planNumber', sa.String(10), nullable=False, unique=True),
        sa.Column('plan_name', sa.String(100), nullable=False),
        sa.Column('customer_id', sa.Integer, sa.ForeignKey('customer.id'), nullable=False),
        sa.Column('project_address', sa.String(200), nullable=False),
        sa.Column('contractor', sa.String(100), nullable=True),
        sa.Column('log_date', sa.DateTime, default=datetime.utcnow),
        sa.Column('preliminary_set_date', sa.DateTime, nullable=True),
        sa.Column('designer_id', sa.Integer, sa.ForeignKey('estimator.estimatorID'), nullable=False),
        sa.Column('status', sa.String(50), default='Active'),
        sa.Column('plan_description', sa.String(50), nullable=True),
        sa.Column('notes', sa.Text, nullable=True)
    )

    # Copy data back to the old table
    op.execute('''
        INSERT INTO design_old (id, planNumber, plan_name, customer_id, project_address, contractor, log_date, preliminary_set_date, designer_id, status, plan_description, notes)
        SELECT id, planNumber, plan_name, customer_id, project_address, contractor, log_date, preliminary_set_date, designer_id, status, plan_description, notes
        FROM design
    ''')

    # Drop the current table
    op.drop_table('design')

    # Rename the old table back to the original name
    op.rename_table('design_old', 'design')