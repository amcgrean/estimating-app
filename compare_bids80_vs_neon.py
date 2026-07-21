"""
Compare bids (80).db against Neon DB on:
  1. Bid IDs - which bids are in local but not Neon, and vice versa
  2. Customer codes - which customers are in local but not Neon, and vice versa
  3. For bids missing from Neon, show their customer code
"""
import sqlite3
from sqlalchemy import create_engine, text

NEON_DB_URL = "postgresql://neondb_owner:npg_1E4CvgZbaVBW@ep-fragrant-waterfall-ad8fjcey-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"
LOCAL_DB = r"C:\Users\amcgrean\python\pa-bid-request\bids (80).db"

def get_local_bids(db_path):
    """Returns dict of bid_id -> customer_id from local SQLite"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, customer_id FROM bid ORDER BY id")
    rows = {r[0]: r[1] for r in cur.fetchall()}
    conn.close()
    return rows

def get_local_customers(db_path):
    """Returns dict of customer_id -> customerCode from local SQLite"""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT id, customerCode FROM customer ORDER BY id")
    rows = {r[0]: r[1] for r in cur.fetchall()}
    conn.close()
    return rows

def get_neon_bids(url):
    """Returns dict of bid_id -> customer_id from Neon"""
    engine = create_engine(url)
    with engine.connect() as conn:
        res = conn.execute(text("SELECT id, customer_id FROM bid ORDER BY id"))
        return {r[0]: r[1] for r in res.fetchall()}

def get_neon_customers(url):
    """Returns dict of customer_id -> customerCode from Neon"""
    engine = create_engine(url)
    with engine.connect() as conn:
        res = conn.execute(text('SELECT id, "customerCode" FROM customer ORDER BY id'))
        return {r[0]: r[1] for r in res.fetchall()}

if __name__ == "__main__":
    print("=" * 60)
    print("STEP 1: Loading data...")
    print("=" * 60)
    local_bids    = get_local_bids(LOCAL_DB)
    local_custs   = get_local_customers(LOCAL_DB)
    neon_bids     = get_neon_bids(NEON_DB_URL)
    neon_custs    = get_neon_customers(NEON_DB_URL)

    print(f"Local DB bids:      {len(local_bids)}")
    print(f"Neon DB bids:       {len(neon_bids)}")
    print(f"Local DB customers: {len(local_custs)}")
    print(f"Neon DB customers:  {len(neon_custs)}")

    # --- BID COMPARISON ---
    print("\n" + "=" * 60)
    print("STEP 2: BID ID COMPARISON")
    print("=" * 60)

    local_bid_ids = set(local_bids.keys())
    neon_bid_ids  = set(neon_bids.keys())

    in_local_not_neon = sorted(local_bid_ids - neon_bid_ids)
    in_neon_not_local = sorted(neon_bid_ids - local_bid_ids)

    if in_local_not_neon:
        print(f"\n[MISSING FROM NEON] {len(in_local_not_neon)} bids in local (80).db but NOT in Neon:")
        for bid_id in in_local_not_neon:
            cust_id = local_bids[bid_id]
            cust_code = local_custs.get(cust_id, "UNKNOWN")
            print(f"  Bid {bid_id}  customer_id={cust_id}  customerCode={cust_code}")
    else:
        print("\n[OK] All local bids are present in Neon.")

    if in_neon_not_local:
        print(f"\n[EXTRA IN NEON] {len(in_neon_not_local)} bids in Neon but NOT in local (80).db:")
        for bid_id in in_neon_not_local:
            neon_cust_id = neon_bids[bid_id]
            neon_cust_code = neon_custs.get(neon_cust_id, "UNKNOWN")
            print(f"  Bid {bid_id}  customer_id={neon_cust_id}  customerCode={neon_cust_code}")
    else:
        print("[OK] No extra bids in Neon that aren't in local.")

    # --- CUSTOMER COMPARISON ---
    print("\n" + "=" * 60)
    print("STEP 3: CUSTOMER CODE COMPARISON")
    print("=" * 60)

    local_codes = set(local_custs.values())
    neon_codes  = set(neon_custs.values())

    in_local_not_neon_codes = sorted(local_codes - neon_codes)
    in_neon_not_local_codes = sorted(neon_codes - local_codes)

    if in_local_not_neon_codes:
        print(f"\n[MISSING FROM NEON] {len(in_local_not_neon_codes)} customer codes in local but NOT in Neon:")
        for code in in_local_not_neon_codes:
            print(f"  {code}")
    else:
        print("\n[OK] All local customer codes are present in Neon.")

    if in_neon_not_local_codes:
        print(f"\n[EXTRA IN NEON] {len(in_neon_not_local_codes)} customer codes in Neon but NOT in local (80).db:")
        for code in in_neon_not_local_codes:
            print(f"  {code}")
    else:
        print("[OK] No extra customer codes in Neon that aren't in local.")

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)
