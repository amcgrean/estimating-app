"""add_estimator_type_flags

Revision ID: a1b2c3d4e5f6
Revises: fea987654321
Create Date: 2026-03-18 10:00:00.000000

Adds is_commercial_estimator and is_residential_estimator boolean flags to the
user table. Removes Amy Larsen, Mike Blevins, and Mike Wagenknecht from the
estimator table (they are designers, not estimators). Seeds estimator type
data for existing estimators:
  - dons        -> commercial only
  - jc, matth, karlp, ryanb -> residential only
  - jasonr      -> both commercial and residential
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'fea987654321'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # 1. Add new columns using native PostgreSQL IF NOT EXISTS — safe on re-runs
    #    and does not require a pre-query that could itself fail.
    conn.execute(sa.text(
        'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS '
        'is_commercial_estimator BOOLEAN DEFAULT FALSE'
    ))
    conn.execute(sa.text(
        'ALTER TABLE "user" ADD COLUMN IF NOT EXISTS '
        'is_residential_estimator BOOLEAN DEFAULT FALSE'
    ))

    # 2. Default any NULLs to False
    conn.execute(sa.text(
        'UPDATE "user" SET is_commercial_estimator = FALSE '
        'WHERE is_commercial_estimator IS NULL'
    ))
    conn.execute(sa.text(
        'UPDATE "user" SET is_residential_estimator = FALSE '
        'WHERE is_residential_estimator IS NULL'
    ))

    # 3. Seed estimator type flags for known estimators

    # Commercial only: dons
    conn.execute(sa.text(
        "UPDATE \"user\" SET is_commercial_estimator = TRUE WHERE username = 'dons'"
    ))

    # Residential only: jc, matth, karlp, ryanb
    conn.execute(sa.text(
        "UPDATE \"user\" SET is_residential_estimator = TRUE "
        "WHERE username IN ('jc', 'matth', 'karlp', 'ryanb')"
    ))

    # Both: jasonr
    conn.execute(sa.text(
        "UPDATE \"user\" SET is_commercial_estimator = TRUE, is_residential_estimator = TRUE "
        "WHERE username = 'jasonr'"
    ))

    # 4. Null out bid.estimator_id for any bids pointing to Amy/Mike/Mike
    #    (estimator IDs 6=amyl, 7=mikeb, 8=mikew)
    conn.execute(sa.text(
        'UPDATE bid SET estimator_id = NULL WHERE estimator_id IN (6, 7, 8)'
    ))

    # 5. Clear "estimatorID" (camelCase FK on user table) and is_estimator flag
    conn.execute(sa.text(
        'UPDATE "user" SET "estimatorID" = NULL, is_estimator = FALSE '
        "WHERE username IN ('amyl', 'mikeb', 'mikew')"
    ))

    # 6. Delete stale Estimator rows — only those that still exist
    conn.execute(sa.text(
        'DELETE FROM estimator WHERE "estimatorID" IN (6, 7, 8)'
    ))


def downgrade():
    conn = op.get_bind()

    # Re-insert removed estimator rows
    conn.execute(sa.text(
        'INSERT INTO estimator ("estimatorID", "estimatorName", "estimatorUsername") '
        "VALUES (6, 'Amy Larsen', 'amyl'), "
        "(7, 'Mike Blevins', 'mikeb'), "
        "(8, 'Mike Wagenknecht', 'mikew') "
        'ON CONFLICT ("estimatorID") DO NOTHING'
    ))

    # Restore user links
    conn.execute(sa.text(
        "UPDATE \"user\" SET \"estimatorID\" = 6 WHERE username = 'amyl'"
    ))
    conn.execute(sa.text(
        "UPDATE \"user\" SET \"estimatorID\" = 7 WHERE username = 'mikeb'"
    ))
    conn.execute(sa.text(
        "UPDATE \"user\" SET \"estimatorID\" = 8 WHERE username = 'mikew'"
    ))

    # Drop the new columns
    op.drop_column('user', 'is_residential_estimator')
    op.drop_column('user', 'is_commercial_estimator')
