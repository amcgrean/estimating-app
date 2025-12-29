"""populate user_type table

Revision ID: 4d2bd2b561f9
Revises: d9191b399b50
Create Date: 2024-07-15 19:14:51.549033

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4d2bd2b561f9'
down_revision = 'd9191b399b50'
branch_labels = None
depends_on = None


def upgrade():
    # Insert initial data into user_type table
    op.execute("""
        INSERT INTO user_type (id, name) VALUES
        (1, 'Administrator'),
        (2, 'Estimator'),
        (3, 'Designer'),
        (4, 'Picker'),
        (5, 'Manager'),
        (6, 'EWP'),
        (7, 'Service Tech'),
        (8, 'Installer'),
        (9, 'Door Builder'),
        (10, 'Sales Rep'),
        (11, 'Customer')
    """)


def downgrade():
    # Remove the inserted data from user_type table
    op.execute("""
        DELETE FROM user_type WHERE id IN (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
    """)
