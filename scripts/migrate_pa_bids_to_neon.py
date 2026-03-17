#!/usr/bin/env python3
"""
Migrate missing bids (and any new customers) from the PythonAnywhere SQLite DB
to the Neon PostgreSQL database.

Usage:
    python scripts/migrate_pa_bids_to_neon.py --source "path/to/bids (79).db" --dry-run
    python scripts/migrate_pa_bids_to_neon.py --source "path/to/bids (79).db"

The script:
  1. Connects to Neon via DATABASE_URL environment variable (or --db-url flag)
  2. Finds the highest bid ID already in Neon
  3. Copies any customers referenced by new bids that don't yet exist in Neon
  4. Inserts all bids with ID > max Neon bid ID from the source SQLite file
  5. Reports a summary of what was migrated

Requirements:
    pip install psycopg2-binary
"""

import argparse
import os
import sqlite3
import sys
from datetime import datetime

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    sys.exit("psycopg2 is required: pip install psycopg2-binary")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_sqlite_conn(path: str) -> sqlite3.Connection:
    if not os.path.exists(path):
        sys.exit(f"Source SQLite file not found: {path}")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def get_pg_conn(db_url: str):
    url = db_url.strip()
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    try:
        return psycopg2.connect(url)
    except psycopg2.OperationalError as e:
        sys.exit(f"Cannot connect to Neon DB: {e}")


def sqlite_tables(conn: sqlite3.Connection) -> list[str]:
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    return [r[0] for r in cur.fetchall()]


# ---------------------------------------------------------------------------
# Inspection
# ---------------------------------------------------------------------------

def inspect_source(src: sqlite3.Connection):
    cur = src.cursor()

    cur.execute("SELECT COUNT(*) FROM bid")
    total_bids = cur.fetchone()[0]

    cur.execute("SELECT MAX(id) FROM bid")
    max_id = cur.fetchone()[0]

    cur.execute("SELECT MIN(log_date), MAX(log_date) FROM bid WHERE log_date IS NOT NULL")
    min_date, max_date = cur.fetchone()

    print(f"\n[Source SQLite]")
    print(f"  Total bids : {total_bids}")
    print(f"  Max bid ID : {max_id}")
    print(f"  Date range : {min_date}  →  {max_date}")

    return max_id


def inspect_neon(pg) -> int:
    cur = pg.cursor()

    # Check if bid table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'bid'
        )
    """)
    if not cur.fetchone()[0]:
        sys.exit("ERROR: 'bid' table does not exist in Neon DB. Run Flask-Migrate first.")

    cur.execute("SELECT COUNT(*) FROM bid")
    total_bids = cur.fetchone()[0]

    cur.execute("SELECT MAX(id) FROM bid")
    max_id = cur.fetchone()[0] or 0

    cur.execute("SELECT MIN(log_date), MAX(log_date) FROM bid WHERE log_date IS NOT NULL")
    min_date, max_date = cur.fetchone()

    print(f"\n[Neon DB]")
    print(f"  Total bids : {total_bids}")
    print(f"  Max bid ID : {max_id}")
    print(f"  Date range : {min_date}  →  {max_date}")

    return max_id


# ---------------------------------------------------------------------------
# Neon schema introspection — get actual columns so we never assume
# ---------------------------------------------------------------------------

def neon_bid_columns(pg) -> list[str]:
    cur = pg.cursor()
    cur.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'bid'
        ORDER BY ordinal_position
    """)
    return [r[0] for r in cur.fetchall()]


def neon_customer_columns(pg) -> list[str]:
    cur = pg.cursor()
    cur.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'customer'
        ORDER BY ordinal_position
    """)
    return [r[0] for r in cur.fetchall()]


def sqlite_bid_columns(src: sqlite3.Connection) -> list[str]:
    cur = src.cursor()
    cur.execute("PRAGMA table_info(bid)")
    return [r[1] for r in cur.fetchall()]


def sqlite_customer_columns(src: sqlite3.Connection) -> list[str]:
    cur = src.cursor()
    cur.execute("PRAGMA table_info(customer)")
    return [r[1] for r in cur.fetchall()]


# ---------------------------------------------------------------------------
# Customer sync (insert missing ones referenced by new bids)
# ---------------------------------------------------------------------------

def sync_customers(src: sqlite3.Connection, pg, new_bid_rows, dry_run: bool) -> int:
    """Insert customers from source that are referenced by new bids but absent in Neon."""

    if not new_bid_rows:
        return 0

    customer_ids = {row["customer_id"] for row in new_bid_rows if row["customer_id"]}
    if not customer_ids:
        return 0

    # Which ones already exist in Neon?
    pg_cur = pg.cursor()
    pg_cur.execute("SELECT id FROM customer WHERE id = ANY(%s)", (list(customer_ids),))
    existing_ids = {r[0] for r in pg_cur.fetchall()}

    missing_ids = customer_ids - existing_ids
    if not missing_ids:
        print(f"\n  Customers : all {len(customer_ids)} referenced customers already in Neon")
        return 0

    # Fetch missing customers from source
    placeholders = ",".join("?" * len(missing_ids))
    src_cur = src.cursor()
    src_cur.execute(f"SELECT * FROM customer WHERE id IN ({placeholders})", list(missing_ids))
    missing_rows = src_cur.fetchall()

    src_cols = sqlite_customer_columns(src)
    pg_cols = neon_customer_columns(pg)

    # Intersect columns that exist in both
    shared_cols = [c for c in src_cols if c in pg_cols]
    col_str = ", ".join(f'"{c}"' for c in shared_cols)
    placeholders_pg = ", ".join("%s" for _ in shared_cols)

    print(f"\n  Customers : {len(missing_rows)} new customer(s) need to be inserted first")
    for row in missing_rows:
        print(f"    → id={row['id']}  code={row['customerCode']}  name={row['name']}")

    if dry_run:
        return len(missing_rows)

    insert_sql = f'INSERT INTO customer ({col_str}) VALUES ({placeholders_pg}) ON CONFLICT (id) DO NOTHING'

    inserted = 0
    for row in missing_rows:
        values = tuple(row[c] for c in shared_cols)
        pg_cur.execute(insert_sql, values)
        inserted += 1

    print(f"  Customers : inserted {inserted}")
    return inserted


# ---------------------------------------------------------------------------
# Bid migration
# ---------------------------------------------------------------------------

def migrate_bids(src: sqlite3.Connection, pg, neon_max_id: int, dry_run: bool):
    src_cur = src.cursor()
    src_cur.execute("SELECT * FROM bid WHERE id > ? ORDER BY id ASC", (neon_max_id,))
    new_bids = src_cur.fetchall()

    if not new_bids:
        print(f"\n  Bids      : nothing to migrate (Neon already has up to id={neon_max_id})")
        return 0

    print(f"\n  Bids      : {len(new_bids)} bid(s) to migrate (id {new_bids[0]['id']} → {new_bids[-1]['id']})")

    # Show preview
    print("\n  Preview of bids to be migrated:")
    for row in new_bids[:10]:
        print(f"    id={row['id']}  {row['log_date']}  [{row['status']}]  {row['project_name'][:50]}")
    if len(new_bids) > 10:
        print(f"    ... and {len(new_bids) - 10} more")

    if dry_run:
        return len(new_bids)

    # Sync any missing customers first
    sync_customers(src, pg, new_bids, dry_run=False)

    src_cols = sqlite_bid_columns(src)
    pg_cols = neon_bid_columns(pg)

    # Use columns present in BOTH schemas to stay safe
    shared_cols = [c for c in src_cols if c in pg_cols]
    skipped_src = [c for c in src_cols if c not in pg_cols]
    skipped_pg  = [c for c in pg_cols  if c not in src_cols and c != "job_id"]  # job_id is nullable

    if skipped_src:
        print(f"\n  Note: source columns not in Neon (skipped): {skipped_src}")
    if skipped_pg:
        print(f"  Note: Neon columns not in source (will be NULL): {skipped_pg}")

    col_str = ", ".join(f'"{c}"' for c in shared_cols)
    placeholders = ", ".join("%s" for _ in shared_cols)
    insert_sql = f'INSERT INTO bid ({col_str}) VALUES ({placeholders}) ON CONFLICT (id) DO NOTHING'

    pg_cur = pg.cursor()
    inserted = 0
    errors = []

    for row in new_bids:
        values = tuple(row[c] for c in shared_cols)
        try:
            pg_cur.execute(insert_sql, values)
            inserted += 1
        except Exception as e:
            errors.append((row["id"], str(e)))
            pg.rollback()  # rollback just this statement's savepoint if needed

    if errors:
        print(f"\n  ERRORS ({len(errors)}):")
        for bid_id, err in errors[:5]:
            print(f"    bid id={bid_id}: {err}")

    return inserted


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Migrate bids from PythonAnywhere SQLite to Neon PostgreSQL")
    parser.add_argument("--source", required=True, help="Path to the source SQLite .db file (e.g. 'bids (79).db')")
    parser.add_argument("--db-url", default=os.environ.get("DATABASE_URL"), help="Neon PostgreSQL connection string (or set DATABASE_URL env var)")
    parser.add_argument("--dry-run", action="store_true", help="Preview what would be migrated without writing anything")
    args = parser.parse_args()

    if not args.db_url:
        sys.exit("No DATABASE_URL set. Use --db-url or export DATABASE_URL=...")

    print("=" * 60)
    print(f"  Bid Migration: SQLite  →  Neon PostgreSQL")
    print(f"  Mode: {'DRY RUN (no changes)' if args.dry_run else 'LIVE (will write to Neon)'}")
    print(f"  Source: {args.source}")
    print("=" * 60)

    src = get_sqlite_conn(args.source)
    pg  = get_pg_conn(args.db_url)

    src_max_id  = inspect_source(src)
    neon_max_id = inspect_neon(pg)

    if src_max_id <= neon_max_id:
        print(f"\n  Nothing to do: Neon max id ({neon_max_id}) >= source max id ({src_max_id})")
        return

    gap = src_max_id - neon_max_id
    print(f"\n  Gap: {gap} bid(s) to migrate (id {neon_max_id + 1} → {src_max_id})")

    if args.dry_run:
        # Still need to read the rows for preview
        src_cur = src.cursor()
        src_cur.execute("SELECT * FROM bid WHERE id > ? ORDER BY id ASC", (neon_max_id,))
        new_bids = src_cur.fetchall()

        sync_customers(src, pg, new_bids, dry_run=True)
        migrate_bids(src, pg, neon_max_id, dry_run=True)
        print("\n  [DRY RUN] No changes written.\n")
        return

    # Live run — wrap everything in a transaction
    try:
        migrate_bids(src, pg, neon_max_id, dry_run=False)
        pg.commit()
        print(f"\n  Migration committed successfully.")
    except Exception as e:
        pg.rollback()
        print(f"\n  ERROR — transaction rolled back: {e}")
        sys.exit(1)
    finally:
        pg.close()
        src.close()

    print("=" * 60)
    print(f"  Done: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
