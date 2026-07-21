"""
DB-side cutover dry-run: instantiate the Flask app + models against the
Supabase `bids` schema (exactly what the production cutover will do) and prove
a real READ and WRITE land there. Cleans up the test row.

Run:  .venv\Scripts\python.exe _cutover_dryrun.py
"""
import os, re, sys

# --- build the Supabase DATABASE_URL with search_path=bids from LiveEdge .env.local ---
ENV = r"C:\Users\amcgrean\python\beisser-takeoff\.env.local"
vals = {}
with open(ENV, "r", encoding="utf-8") as f:
    for line in f:
        m = re.match(r"^([^#=]+)=(.+)$", line.strip())
        if m:
            vals[m.group(1).strip()] = m.group(2).strip().strip('"').strip("'")

supa = vals["POSTGRES_URL_NON_POOLING"]
if supa.startswith("postgres://"):
    supa = supa.replace("postgres://", "postgresql://", 1)

os.environ["DATABASE_URL"] = supa
# env-driven schema flip — exactly what production will set at cutover
os.environ["DB_SCHEMA"] = "bids"
# also point storage at R2 (already verified working)
for k in ("R2_ACCOUNT_ID", "R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY", "R2_BUCKET_NAME"):
    if vals.get(k):
        os.environ[k] = vals[k]
os.environ.setdefault("SECRET_KEY", "dryrun")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from project import create_app, db
from project.models import Bid, Customer

app = create_app()
result = {}
with app.app_context():
    # 1. READ — resolve against bids schema
    total = db.session.query(Bid).count()
    recent = db.session.query(Bid).order_by(Bid.id.desc()).first()
    result["read"] = f"PASS — {total} bids visible; newest #{recent.id} '{recent.project_name}'"

    # a real customer for the FK
    cust = db.session.query(Customer).first()

    # 2. WRITE — insert a test bid, confirm it lands, then delete
    test = Bid(
        plan_type="Residential",
        customer_id=cust.id,
        project_name="__CUTOVER_DRYRUN__ (delete me)",
        status="Incomplete",
    )
    db.session.add(test)
    db.session.commit()
    new_id = test.id

    back = db.session.query(Bid).get(new_id)
    wrote_ok = back is not None and back.project_name == "__CUTOVER_DRYRUN__ (delete me)"

    # clean up
    db.session.delete(test)
    db.session.commit()
    gone = db.session.query(Bid).get(new_id) is None

    result["write"] = ("PASS" if (wrote_ok and gone) else "FAIL") + \
        f" — inserted #{new_id} into bids.bid, read back={wrote_ok}, cleaned up={gone}"

print("\nCUTOVER DB DRY-RUN  (Flask -> Supabase bids)")
print("=" * 60)
print(f"  DATABASE_URL -> ...{supa[-55:]}")
for k, v in result.items():
    print(f"  {'OK  ' if v.startswith('PASS') else 'XX  '}{k:<6} {v}")
sys.exit(0 if all(v.startswith("PASS") for v in result.values()) else 1)
