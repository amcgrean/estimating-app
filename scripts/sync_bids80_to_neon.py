"""
Sync bids (80).db -> Neon DB:
  - INSERT 4 missing bids
  - UPDATE status, estimator_id, completion_date, due_date, notes, last_updated_by, last_updated_at
    for ALL bids where local differs from Neon

Usage:
    $env:DATABASE_URL = "postgresql://..."
    python scripts/sync_bids80_to_neon.py          # dry run
    python scripts/sync_bids80_to_neon.py --commit  # apply changes
"""
import sqlite3
import argparse
import sys
import os
from datetime import datetime
from sqlalchemy import create_engine, text

LOCAL_DB = r"C:\Users\amcgrean\python\pa-bid-request\bids (80).db"

NEON_DB_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_1E4CvgZbaVBW@ep-fragrant-waterfall-ad8fjcey-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"
)

# Fields to compare/update for existing bids
# NOTE: branch_id is intentionally excluded — Neon has authoritative values (set by migration)
#       that local bids (80).db has as NULL for older records.
SYNC_FIELDS = [
    "status",
    "estimator_id",
    "completion_date",
    "due_date",
    "notes",
    "last_updated_by",
    "last_updated_at",
    "plan_type",
    "project_name",
]

def parse_dt(val):
    if not val:
        return None
    if isinstance(val, datetime):
        return val
    for fmt in ('%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
        try:
            return datetime.strptime(val, fmt)
        except ValueError:
            continue
    return None

def load_local_bids(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM bid ORDER BY id")
    rows = {r['id']: dict(r) for r in cur.fetchall()}
    conn.close()
    return rows

def load_neon_bids(engine):
    with engine.connect() as conn:
        res = conn.execute(text("SELECT * FROM bid"))
        cols = res.keys()
        return {r[0]: dict(zip(cols, r)) for r in res.fetchall()}

def run_sync(commit=False):
    print(f"Loading local DB:  {LOCAL_DB}")
    local_bids = load_local_bids(LOCAL_DB)
    print(f"  -> {len(local_bids)} bids")

    engine = create_engine(NEON_DB_URL)
    print("Loading Neon DB...")
    neon_bids = load_neon_bids(engine)
    print(f"  -> {len(neon_bids)} bids")

    inserts = []
    updates = []

    for bid_id, local in local_bids.items():
        if bid_id not in neon_bids:
            inserts.append(local)
        else:
            neon = neon_bids[bid_id]

            # Guard: only update if local record is newer than Neon
            local_updated = parse_dt(local.get('last_updated_at'))
            neon_updated  = neon.get('last_updated_at')
            if isinstance(neon_updated, datetime):
                neon_updated = neon_updated.replace(tzinfo=None)
            else:
                neon_updated = parse_dt(neon_updated)

            if local_updated and neon_updated and neon_updated > local_updated:
                # Neon is newer — skip this record
                continue

            diff = {}
            for field in SYNC_FIELDS:
                local_val = local.get(field)
                neon_val  = neon.get(field)

                # Normalise datetimes
                if field in ('completion_date', 'due_date', 'log_date', 'last_updated_at'):
                    local_val = parse_dt(local_val)
                    if isinstance(neon_val, datetime):
                        neon_val = neon_val.replace(tzinfo=None)
                    else:
                        neon_val = parse_dt(neon_val)

                # Normalise ints
                if field == 'estimator_id':
                    local_val = int(local_val) if local_val else None
                    neon_val  = int(neon_val)  if neon_val  else None

                if local_val != neon_val:
                    diff[field] = (neon_val, local_val)

            if diff:
                updates.append((bid_id, diff))

    print(f"\n[DRY RUN] Summary:")
    print(f"  Bids to INSERT: {len(inserts)}")
    print(f"  Bids to UPDATE: {len(updates)}")

    if inserts:
        print("\nINSERTS:")
        for b in inserts:
            print(f"  Bid {b['id']}  customer_id={b['customer_id']}  status={b['status']}  project={b['project_name']}")

    if updates:
        print("\nUPDATES (first 30 shown):")
        for bid_id, diff in updates[:30]:
            print(f"  Bid {bid_id}:")
            for field, (old, new) in diff.items():
                print(f"    {field}: {old!r} -> {new!r}")

    if not commit:
        print("\nDRY RUN complete. Use --commit to apply changes.")
        return

    print("\nApplying changes to Neon...")
    with engine.connect() as conn:
        # INSERTs
        for b in inserts:
            try:
                conn.execute(text("""
                    INSERT INTO bid (id, plan_type, customer_id, project_name, estimator_id,
                                    status, log_date, due_date, completion_date, notes,
                                    last_updated_by, last_updated_at, branch_id)
                    VALUES (:id, :plan_type, :customer_id, :project_name, :estimator_id,
                            :status, :log_date, :due_date, :completion_date, :notes,
                            :last_updated_by, :last_updated_at, :branch_id)
                """), {
                    'id':              b['id'],
                    'plan_type':       b.get('plan_type'),
                    'customer_id':     b['customer_id'],
                    'project_name':    b.get('project_name') or 'Unknown Project',
                    'estimator_id':    int(b['estimator_id']) if b.get('estimator_id') else None,
                    'status':          b.get('status'),
                    'log_date':        parse_dt(b.get('log_date')),
                    'due_date':        parse_dt(b.get('due_date')),
                    'completion_date': parse_dt(b.get('completion_date')),
                    'notes':           b.get('notes'),
                    'last_updated_by': b.get('last_updated_by'),
                    'last_updated_at': parse_dt(b.get('last_updated_at')),
                    'branch_id':       int(b['branch_id']) if b.get('branch_id') else None,
                })
                print(f"  [INSERTED] Bid {b['id']}")
            except Exception as e:
                print(f"  [ERROR] INSERT Bid {b['id']}: {e}")

        # UPDATEs
        updated_count = 0
        for bid_id, diff in updates:
            set_clauses = ", ".join(f"{f} = :{f}" for f in diff)
            params = {f: val[1] for f, val in diff.items()}
            params['bid_id'] = bid_id
            try:
                conn.execute(text(f"UPDATE bid SET {set_clauses} WHERE id = :bid_id"), params)
                updated_count += 1
            except Exception as e:
                print(f"  [ERROR] UPDATE Bid {bid_id}: {e}")

        conn.commit()

        # Reset sequence
        try:
            conn.execute(text("SELECT setval('bid_id_seq', (SELECT MAX(id) FROM bid))"))
            conn.commit()
            print("  Sequence reset OK.")
        except Exception as e:
            print(f"  Warning: Could not reset sequence: {e}")

    print(f"\nDone. Inserted: {len(inserts)}, Updated: {updated_count}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--commit', action='store_true', help='Apply changes (default: dry run)')
    args = parser.parse_args()
    run_sync(commit=args.commit)
