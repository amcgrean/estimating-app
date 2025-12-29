"""new changes to user tracking

Revision ID: 31081991b1e3
Revises: d9319f6e738f
Create Date: 2024-07-27 12:23:21.679259

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer, DateTime, Boolean

# revision identifiers, used by Alembic.
revision = '31081991b1e3'
down_revision = 'd9319f6e738f'
branch_labels = None
depends_on = None


def upgrade():
    # Drop user_temp table if it exists
    op.execute('DROP TABLE IF EXISTS user_temp')

    # Create user_temp table
    op.create_table('user_temp',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=150), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('password', sa.String(length=150), nullable=False),
        sa.Column('usertype_id', sa.Integer(), nullable=False),
        sa.Column('estimatorID', sa.Integer(), nullable=True),
        sa.Column('sales_rep_id', sa.Integer(), nullable=True),
        sa.Column('user_branch_id', sa.Integer(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_admin', sa.Boolean(), nullable=True),
        sa.Column('login_count', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['usertype_id'], ['user_type.id'], ),
        sa.ForeignKeyConstraint(['estimatorID'], ['estimator.estimatorID'], ),
        sa.ForeignKeyConstraint(['sales_rep_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['user_branch_id'], ['branch.branch_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )

    # Copy data from user to user_temp
    op.execute('''
        INSERT INTO user_temp (id, username, email, password, usertype_id, "estimatorID", sales_rep_id, user_branch_id, last_login, created_at, updated_at, is_active, is_admin, login_count)
        SELECT id, username, email, password, usertype_id, "estimatorID", sales_rep_id, user_branch_id, last_login, created_at, updated_at, is_active, is_admin, login_count
        FROM user
    ''')

    # Drop the old user table
    op.drop_table('user')

    # Rename user_temp to user
    op.rename_table('user_temp', 'user')


def downgrade():
    # Rename user back to user_temp
    op.rename_table('user', 'user_temp')

    # Recreate the original user table
    op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=150), nullable=False),
        sa.Column('email', sa.String(length=150), nullable=False),
        sa.Column('password', sa.VARCHAR(length=128), nullable=False),
        sa.Column('usertype_id', sa.Integer(), nullable=False),
        sa.Column('estimatorID', sa.Integer(), nullable=True),
        sa.Column('sales_rep_id', sa.Integer(), nullable=True),
        sa.Column('user_branch_id', sa.Integer(), nullable=True),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_admin', sa.Boolean(), nullable=True),
        sa.Column('login_count', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['usertype_id'], ['user_type.id'], ),
        sa.ForeignKeyConstraint(['estimatorID'], ['estimator.estimatorID'], ),
        sa.ForeignKeyConstraint(['sales_rep_id'], ['user.id'], ),
        sa.ForeignKeyConstraint(['user_branch_id'], ['branch.branch_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.UniqueConstraint('email')
    )

    # Copy data back from user_temp to user
    op.execute('''
        INSERT INTO user (id, username, email, password, usertype_id, estimatorID, sales_rep_id, user_branch_id, last_login, created_at, updated_at, is_active, is_admin, login_count)
        SELECT id, username, email, password, usertype_id, estimatorID, sales_rep_id, user_branch_id, last_login, created_at, updated_at, is_active, is_admin, login_count
        FROM user_temp
    ''')

    # Drop the user_temp table
    op.drop_table('user_temp')
