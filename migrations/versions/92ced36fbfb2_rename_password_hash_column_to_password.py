from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = '92ced36fbfb2'
down_revision = '37fcabfb89e9'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Get existing columns in the 'user' table
    user_columns = inspector.get_columns('user')
    
    with op.batch_alter_table('user') as batch_op:
        # Rename password_hash to password only if it still exists
        if 'password_hash' in [col['name'] for col in user_columns]:
            batch_op.alter_column('password_hash', new_column_name='password', existing_type=sa.String(150), nullable=False)
        
        # Rename usertype to usertype_id only if it still exists
        if 'usertype' in [col['name'] for col in user_columns]:
            batch_op.alter_column('usertype', new_column_name='usertype_id', existing_type=sa.Integer(), nullable=True)

def downgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Get existing columns in the 'user' table
    user_columns = inspector.get_columns('user')
    
    with op.batch_alter_table('user') as batch_op:
        # Revert password to password_hash only if it still exists
        if 'password' in [col['name'] for col in user_columns]:
            batch_op.alter_column('password', new_column_name='password_hash', existing_type=sa.String(150), nullable=False)
        
        # Revert usertype_id to usertype only if it still exists
        if 'usertype_id' in [col['name'] for col in user_columns]:
            batch_op.alter_column('usertype_id', new_column_name='usertype', existing_type=sa.Integer(), nullable=True)