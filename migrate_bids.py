#!/usr/bin/env python3
"""
Migrate missing bids (and any missing customers) from the PythonAnywhere SQLite DB
to the Neon PostgreSQL database.

Usage:
    python scripts/migrate_pa_bids_to_neon.py --source "bids (79).db" --dry-run
    python scripts/migrate_pa_bids_to_neon.py --source "bids (79).db"

The script:
  1. Fetches ALL bid IDs currently in Neon
  2. Fetches ALL bid IDs from the source SQLite file
  3. Finds IDs present in source but MISSING from Neon (handles gaps, not just max)
  4. Syncs any customers referenced by missing bids that don't yet exist in Neon
  5. Inserts all missing bids in a single transaction

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
    sys.exit("psycopg2 is required:  pip install psycopg2-binary")


# ---------------------------------------------------------------------------
# Connections
# ---------------------------------------------------------------------------

def get_sqlite_conn(path: str) -> sqlite3.Connection:
    if not os.path.exists(path):
        sys.exit(f"Source SQLite file not found: {path}")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def get_pg_conn(db_url: str):
    url = db_url.strip().replace("postgres://", "postgresql://", 1)
    try:
        return psycopg2.connect(url)
    except psycopg2.OperationalError as e:
        sys.exit(f"Cannot connect to Neon DB:\n  {e}")


# ---------------------------------------------------------------------------
# Schema helpers
# ---------------------------------------------------------------------------

def neon_columns(pg, table: str) -> list[str]:
    cur = pg.cursor()
    cur.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = %s
        ORDER BY ordinal_position
    """, (table,))
    return [r[0] for r in cur.fetchall()]


def sqlite_columns(src: sqlite3.Connection, table: str) -> list[str]:
    cur = src.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    return [r[1] for r in cur.fetchall()]


# ---------------------------------------------------------------------------
# Inspection
# ---------------------------------------------------------------------------

def inspect_source(src: sqlite3.Connection) -> tuple[int, set[int]]:
    cur = src.cursor()
    cur.execute("SELECT id FROM bid ORDER BY id")
    ids = {r[0] for r in cur.fetchall()}

    cur.execute("SELECT MIN(log_date), MAX(log_date) FROM bid WHERE log_date IS NOT NULL")
    min_d, max_d = cur.fetchone()

    print(f"\n[Source SQLite  ({os.path.basename(src.row_factory.__module__ if hasattr(src.row_factory,'__module__') else 'bids.db')})]")
    print(f"  Total bids : {len(ids)}")
    print(f"  ID range   : {min(ids)} → {max(ids)}")
    print(f"  Date range : {min_d}  →  {max_d}")
    return max(ids), ids


def inspect_neon(pg) -> tuple[int, set[int]]:
    cur = pg.cursor()

    # Verify table exists
    cur.execute("""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = 'bid'
        )
    """)
    if not cur.fetchone()[0]:
        sys.exit("ERROR: 'bid' table not found in Neon. Run Flask-Migrate first.")

    cur.execute("SELECT id FROM bid ORDER BY id")
    ids = {r[0] for r in cur.fetchall()}

    if not ids:
        print(f"\n[Neon DB]  (empty)")
        return 0, ids

    cur.execute("SELECT MIN(log_date), MAX(log_date) FROM bid WHERE log_date IS NOT NULL")
    min_d, max_d = cur.fetchone()

    print(f"\n[Neon DB]")
    print(f"  Total bids : {len(ids)}")
    print(f"  ID range   : {min(ids)} → {max(ids)}")
    print(f"  Date range : {min_d}  →  {max_d}")
    return max(ids), ids


# ---------------------------------------------------------------------------
# Estimator sync
# ---------------------------------------------------------------------------

def sync_estimators(src: sqlite3.Connection, pg, missing_bid_rows, dry_run: bool) -> int:
    """Insert estimators from source that are referenced by new bids but absent in Neon.
    estimator_id=0 is treated as NULL (PA uses 0 for unassigned; Neon FK won't allow it).
    """
    if not missing_bid_rows:
        return 0

    # Collect non-zero estimator_ids referenced by new bids
    needed_ids = {row["estimator_id"] for row in missing_bid_rows
                  if row["estimator_id"] and row["estimator_id"] != 0}
    if not needed_ids:
        print(f"  Estimators : none referenced (or all unassigned) ✓")
        return 0

    pg_cur = pg.cursor()
    pg_cur.execute('SELECT "estimatorID" FROM estimator WHERE "estimatorID" = ANY(%s)', (list(needed_ids),))
    existing = {r[0] for r in pg_cur.fetchall()}

    missing = needed_ids - existing
    if not missing:
        print(f"  Estimators : all {len(needed_ids)} referenced estimators already in Neon ✓")
        return 0

    # PA uses 'estimatorID' as PK column name; Neon uses 'id'
    placeholders = ",".join("?" * len(missing))
    src_cur = src.cursor()
    src_cur.execute(f"SELECT * FROM estimator WHERE estimatorID IN ({placeholders})", list(missing))
    rows = src_cur.fetchall()

    src_cols = sqlite_columns(src, "estimator")
    pg_cols  = neon_columns(pg, "estimator")

    # Build column mapping: estimatorID→id, estimatorName→name, etc.
    col_map = {}
    for sc in src_cols:
        if sc in pg_cols:
            col_map[sc] = sc
        elif sc == "estimatorID" and "id" in pg_cols:
            col_map[sc] = "id"
        elif sc == "estimatorName" and "name" in pg_cols:
            col_map[sc] = "name"
        elif sc == "estimatorUsername" and "username" in pg_cols:
            col_map[sc] = "username"

    print(f"  Estimators : {len(rows)} new estimator(s) to insert:")
    for r in rows:
        print(f"    → id={r['estimatorID']}  {r['estimatorName']}  ({r['estimatorUsername']})")

    if dry_run:
        return len(rows)

    col_str = ", ".join(f'"{pg_col}"' for pg_col in col_map.values())
    ph      = ", ".join("%s" for _ in col_map)
    sql     = f'INSERT INTO estimator ({col_str}) VALUES ({ph}) ON CONFLICT (id) DO NOTHING'

    inserted = 0
    for row in rows:
        pg_cur.execute(sql, tuple(row[src_col] for src_col in col_map.keys()))
        inserted += 1

    print(f"  Estimators : inserted {inserted}")
    return inserted


# ---------------------------------------------------------------------------
# Customer sync
# ---------------------------------------------------------------------------

def sync_customers(src: sqlite3.Connection, pg, missing_bid_rows, dry_run: bool) -> int:
    if not missing_bid_rows:
        return 0

    needed_ids = {row["customer_id"] for row in missing_bid_rows if row["customer_id"]}
    if not needed_ids:
        return 0

    pg_cur = pg.cursor()
    pg_cur.execute("SELECT id FROM customer WHERE id = ANY(%s)", (list(needed_ids),))
    existing = {r[0] for r in pg_cur.fetchall()}

    missing = needed_ids - existing
    if not missing:
        print(f"  Customers  : all {len(needed_ids)} referenced customers already in Neon ✓")
        return 0

    placeholders = ",".join("?" * len(missing))
    src_cur = src.cursor()
    src_cur.execute(f"SELECT * FROM customer WHERE id IN ({placeholders})", list(missing))
    rows = src_cur.fetchall()

    src_cols = sqlite_columns(src, "customer")
    pg_cols  = neon_columns(pg, "customer")
    shared   = [c for c in src_cols if c in pg_cols]

    print(f"  Customers  : {len(rows)} new customer(s) to insert:")
    for r in rows:
        print(f"    → id={r['id']}  {r['customerCode']}  {r['name']}")

    if dry_run:
        return len(rows)

    col_str  = ", ".join(f'"{c}"' for c in shared)
    ph       = ", ".join("%s" for _ in shared)
    sql      = f'INSERT INTO customer ({col_str}) VALUES ({ph}) ON CONFLICT (id) DO NOTHING'

    inserted = 0
    for row in rows:
        pg_cur.execute(sql, tuple(row[c] for c in shared))
        inserted += 1

    print(f"  Customers  : inserted {inserted}")
    return inserted


# ---------------------------------------------------------------------------
# Bid migration
# ---------------------------------------------------------------------------

def migrate_bids(src: sqlite3.Connection, pg, missing_ids: set[int], dry_run: bool) -> int:
    if not missing_ids:
        print("\n  Bids       : nothing to migrate — Neon is already up to date ✓")
        return 0

    sorted_ids = sorted(missing_ids)
    print(f"\n  Bids       : {len(sorted_ids)} bid(s) missing from Neon")
    print(f"  ID range   : {sorted_ids[0]} → {sorted_ids[-1]}")

    # Fetch the full rows from source
    placeholders = ",".join("?" * len(sorted_ids))
    src_cur = src.cursor()
    src_cur.execute(
        f"SELECT * FROM bid WHERE id IN ({placeholders}) ORDER BY id",
        sorted_ids
    )
    rows = src_cur.fetchall()

    print("\n  Preview (first 15):")
    for row in rows[:15]:
        print(f"    id={row['id']:5d}  {str(row['log_date'])[:19]}  [{row['status'] or '':12s}]  {str(row['project_name'])[:45]}")
    if len(rows) > 15:
        print(f"    ... and {len(rows) - 15} more")

    if dry_run:
        return len(rows)

    # Sync estimators and customers first
    sync_estimators(src, pg, rows, dry_run=False)
    sync_customers(src, pg, rows, dry_run=False)

    src_cols = sqlite_columns(src, "bid")
    pg_cols  = neon_columns(pg, "bid")
    shared   = [c for c in src_cols if c in pg_cols]
    skipped  = [c for c in src_cols if c not in pg_cols]
    if skipped:
        print(f"\n  Note: source columns not in Neon (skipped): {skipped}")

    col_str = ", ".join(f'"{c}"' for c in shared)
    ph      = ", ".join("%s" for _ in shared)
    sql     = f'INSERT INTO bid ({col_str}) VALUES ({ph}) ON CONFLICT (id) DO NOTHING'

    pg_cur   = pg.cursor()
    inserted = 0
    errors   = []

    for row in rows:
        # Coerce estimator_id=0 → NULL (PA uses 0 for unassigned; Neon FK disallows it)
        def val(col):
            v = row[col]
            if col == "estimator_id" and v == 0:
                return None
            return v

        pg_cur.execute("SAVEPOINT sp_bid")
        try:
            pg_cur.execute(sql, tuple(val(c) for c in shared))
            pg_cur.execute("RELEASE SAVEPOINT sp_bid")
            inserted += 1
        except Exception as e:
            pg_cur.execute("ROLLBACK TO SAVEPOINT sp_bid")
            errors.append((row["id"], str(e)))

    if errors:
        print(f"\n  ERRORS ({len(errors)}):")
        for bid_id, err in errors[:5]:
            print(f"    bid id={bid_id}: {err}")

    return inserted


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Migrate missing bids from PythonAnywhere SQLite → Neon PostgreSQL"
    )
    parser.add_argument("--source", required=True,
                        help="Path to source SQLite file, e.g. 'bids (79).db'")
    parser.add_argument("--db-url", default=os.environ.get("DATABASE_URL"),
                        help="Neon connection string (or set DATABASE_URL env var)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview only — no writes to Neon")
    args = parser.parse_args()

    if not args.db_url:
        sys.exit("No DATABASE_URL. Use --db-url or: export DATABASE_URL=postgresql://...")

    print("=" * 65)
    print("  Bid Migration: PythonAnywhere SQLite  →  Neon PostgreSQL")
    print(f"  Mode   : {'DRY RUN — no changes will be written' if args.dry_run else 'LIVE — will write to Neon'}")
    print(f"  Source : {args.source}")
    print("=" * 65)

    src = get_sqlite_conn(args.source)
    pg  = get_pg_conn(args.db_url)

    _src_max, src_ids  = inspect_source(src)
    _pg_max,  neon_ids = inspect_neon(pg)

    missing = src_ids - neon_ids
    in_neon_not_src = neon_ids - src_ids  # informational

    print(f"\n  Comparison:")
    print(f"    In PA source only (missing from Neon) : {len(missing)}")
    print(f"    In Neon only (added after PA export)  : {len(in_neon_not_src)}")
    print(f"    In both                               : {len(src_ids & neon_ids)}")

    if not missing:
        print("\n  Nothing to migrate.\n")
        return

    if args.dry_run:
        migrate_bids(src, pg, missing, dry_run=True)
        # Also show estimator/customer preview
        sorted_ids = sorted(missing)
        placeholders = ",".join("?" * len(sorted_ids))
        src_cur = src.cursor()
        src_cur.execute(f"SELECT * FROM bid WHERE id IN ({placeholders}) ORDER BY id", sorted_ids)
        rows = src_cur.fetchall()
        sync_estimators(src, pg, rows, dry_run=True)
        sync_customers(src, pg, rows, dry_run=True)
        print("\n  [DRY RUN] No changes written.\n")
        return

    # Live run
    try:
        inserted = migrate_bids(src, pg, missing, dry_run=False)
        pg.commit()
        print(f"\n  ✓ Committed {inserted} bid(s) to Neon successfully.")
    except Exception as e:
        pg.rollback()
        print(f"\n  ERROR — rolled back: {e}")
        sys.exit(1)
    finally:
        pg.close()
        src.close()

    print("=" * 65)
    print(f"  Done: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)


if __name__ == "__main__":
    main()
