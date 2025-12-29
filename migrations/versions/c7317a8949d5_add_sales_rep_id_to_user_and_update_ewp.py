"""Add sales_rep_id to User and update EWP

Revision ID: c7317a8949d5
Revises: 27ec8156bda3
Create Date: 2024-07-10 14:11:04.344181

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision = 'c7317a8949d5'
down_revision = '27ec8156bda3'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Check if the sales_rep_id column already exists in the user table
    user_columns = inspector.get_columns('user')
    if 'sales_rep_id' not in [col['name'] for col in user_columns]:
        # Create the sales_rep_id column in the user table
        op.add_column('user', sa.Column('sales_rep_id', sa.Integer(), unique=True, nullable=True))

    # Modify the ewp table to use sales_rep_id and customer_id as integer fields
    with op.batch_alter_table('ewp', schema=None) as batch_op:
        ewp_columns = inspector.get_columns('ewp')
        if 'sales_rep_id' not in [col['name'] for col in ewp_columns]:
            batch_op.add_column(sa.Column('sales_rep_id', sa.Integer(), nullable=True))
        if 'customer_id' not in [col['name'] for col in ewp_columns]:
            batch_op.add_column(sa.Column('customer_id', sa.Integer(), nullable=True))
        if 'temp_sales_rep' not in [col['name'] for col in ewp_columns]:
            batch_op.add_column(sa.Column('temp_sales_rep', sa.String(255), nullable=True))
        if 'temp_customer' not in [col['name'] for col in ewp_columns]:
            batch_op.add_column(sa.Column('temp_customer', sa.String(255), nullable=True))

    # Copy existing data into temporary columns
    op.execute('UPDATE ewp SET temp_sales_rep = sales_rep, temp_customer = customer')

    # Drop old columns
    with op.batch_alter_table('ewp', schema=None) as batch_op:
        batch_op.drop_column('sales_rep')
        batch_op.drop_column('customer')

    # Populate new columns using the temporary columns and lookup from User and Customer tables
    op.execute('UPDATE ewp SET sales_rep_id = (SELECT id FROM user WHERE user.username = ewp.temp_sales_rep)')
    op.execute('UPDATE ewp SET customer_id = (SELECT id FROM customer WHERE customer.name = ewp.temp_customer)')

    # Drop temporary columns
    with op.batch_alter_table('ewp', schema=None) as batch_op:
        batch_op.drop_column('temp_sales_rep')
        batch_op.drop_column('temp_customer')

    # Add foreign keys
    with op.batch_alter_table('ewp', schema=None) as batch_op:
        batch_op.create_foreign_key('fk_sales_rep_id', 'user', ['sales_rep_id'], ['id'])
        batch_op.create_foreign_key('fk_customer_id', 'customer', ['customer_id'], ['id'])


def downgrade():
    # Revert the changes in the ewp table
    with op.batch_alter_table('ewp', schema=None) as batch_op:
        batch_op.add_column(sa.Column('sales_rep', sa.String(length=255), nullable=False))
        batch_op.add_column(sa.Column('customer', sa.String(length=255), nullable=False))
        batch_op.drop_constraint('fk_customer_id', type_='foreignkey')
        batch_op.drop_constraint('fk_sales_rep_id', type_='foreignkey')
        batch_op.drop_column('customer_id')
        batch_op.drop_column('sales_rep_id')

    # Revert the sales_rep_id column in the user table
    op.drop_column('user', 'sales_rep_id')
