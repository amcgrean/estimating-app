"""Add last_updated_by and last_updated_at to Bid and Design

Revision ID: 154ff894bf82
Revises: 92ced36fbfb2
Create Date: 2024-07-18 21:13:24.056845

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, DateTime
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '154ff894bf82'
down_revision = '92ced36fbfb2'
branch_labels = None
depends_on = None


def upgrade():
    # Add last_updated_by and last_updated_at columns to Bid
    op.add_column('bid', sa.Column('last_updated_by', sa.String(length=150), nullable=True))
    op.add_column('bid', sa.Column('last_updated_at', sa.DateTime, nullable=True, default=datetime.utcnow))

    # Add last_updated_by and last_updated_at columns to Design
    op.add_column('design', sa.Column('last_updated_by', sa.String(length=150), nullable=True))
    op.add_column('design', sa.Column('last_updated_at', sa.DateTime, nullable=True, default=datetime.utcnow))

    # Add last_updated_by and last_updated_at columns to EWP
    op.add_column('ewp', sa.Column('last_updated_by', sa.String(length=150), nullable=True))
    op.add_column('ewp', sa.Column('last_updated_at', sa.DateTime, nullable=True, default=datetime.utcnow))

    # Populate the existing rows with default values
    conn = op.get_bind()
    conn.execute(
        sa.text(
            "UPDATE bid SET last_updated_by = 'admin', last_updated_at = '2024-07-13 00:00:00' WHERE last_updated_by IS NULL"
        )
    )
    conn.execute(
        sa.text(
            "UPDATE design SET last_updated_by = 'admin', last_updated_at = '2024-07-13 00:00:00' WHERE last_updated_by IS NULL"
        )
    )
    conn.execute(
        sa.text(
            "UPDATE ewp SET last_updated_by = 'admin', last_updated_at = '2024-07-13 00:00:00' WHERE last_updated_by IS NULL"
        )
    )


def downgrade():
    # Remove last_updated_by and last_updated_at columns from Bid
    op.drop_column('bid', 'last_updated_by')
    op.drop_column('bid', 'last_updated_at')

    # Remove last_updated_by and last_updated_at columns from Design
    op.drop_column('design', 'last_updated_by')
    op.drop_column('design', 'last_updated_at')

    # Remove last_updated_by and last_updated_at columns from EWP
    op.drop_column('ewp', 'last_updated_by')
    op.drop_column('ewp', 'last_updated_at')
