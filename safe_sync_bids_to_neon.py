"""
Safe sync from bids (80).db to Neon using fuzzy (customerCode, project_name) matching.
Forces estimator_id update for matching records to ensure alignment.
"""
import sqlite3
import sqlalchemy as sa
import argparse
from difflib import SequenceMatcher

LOCAL_DB = r'C:\Users\amcgrean\python\pa-bid-request\bids (80).db'
NEON = 'postgresql://neondb_owner:npg_1E4CvgZbaVBW@ep-fragrant-waterfall-ad8fjcey-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require'

def similar(a, b):
    if not a or not b: return 0
    return SequenceMatcher(None, a.upper(), b.upper()).ratio()

def get_local_bids():
    conn = sqlite3.connect(LOCAL_DB)
    cur = conn.cursor()
    query = """
    SELECT b.id, b.plan_type, b.project_name, b.status, b.log_date, b.due_date, 
           b.completion_date, b.notes, b.last_updated_by, b.last_updated_at,
           b.estimator_id, c.customerCode, e.estimatorName
    FROM bid b
    JOIN customer c ON b.customer_id = c.id
    LEFT JOIN estimator e ON b.estimator_id = e.estimatorID
    WHERE date(b.log_date) >= '2026-02-01'
    """
    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return rows

def sync(commit=False):
    local_rows = get_local_bids()
    print(f"Loaded {len(local_rows)} local bids from Feb 1st onward.")

    engine = sa.create_engine(NEON)
    with engine.connect() as conn:
        # Load Neon bids for mapping
        res = conn.execute(sa.text("""
            SELECT b.id, b.project_name, cu."customerCode", b.last_updated_at, b.branch_id, b.estimator_id, e."estimatorName"
            FROM bid b
            JOIN customer cu ON b.customer_id = cu.id
            LEFT JOIN estimator e ON e."estimatorID" = b.estimator_id
            WHERE b.log_date >= '2026-01-01'
        """))
        neon_bids = res.fetchall()
        
        neon_by_cc = {}
        for n_id, n_proj, n_cc, n_updated, n_branch, n_est_id, n_est_name in neon_bids:
            cc = n_cc.strip().upper()
            if cc not in neon_by_cc:
                neon_by_cc[cc] = []
            neon_by_cc[cc].append({
                'id': n_id, 
                'project': n_proj, 
                'updated_at': n_updated, 
                'branch': n_branch,
                'est_id': n_est_id,
                'est_name': n_est_name
            })

        updates = []
        inserts = []

        for l in local_rows:
            l_id, l_plan, l_proj, l_status, l_log, l_due, l_comp, l_notes, l_by, l_at, l_est_id, l_cc, l_est_name = l
            cc = l_cc.strip().upper()
            
            best_match = None
            best_score = 0
            
            if cc in neon_by_cc:
                for n_bid in neon_by_cc[cc]:
                    score = similar(l_proj, n_bid['project'])
                    if score > best_score:
                        best_score = score
                        best_match = n_bid
            
            if best_match and best_score > 0.85:
                # FORCE update estimator_id if it differs, and other fields if local is newer
                different_est = (l_est_id != best_match['est_id'])
                newer = (l_at and (not best_match['updated_at'] or str(l_at) > str(best_match['updated_at'])))
                
                if different_est or newer:
                    updates.append({
                        'id': best_match['id'],
                        'status': l_status,
                        'estimator_id': l_est_id,
                        'completion_date': l_comp,
                        'due_date': l_due,
                        'notes': l_notes,
                        'last_updated_by': l_by or 'System/SafeSync',
                        'last_updated_at': l_at,
                        'plan_type': l_plan
                    })
            else:
                # Insert missing
                res_cu = conn.execute(sa.text('SELECT id FROM customer WHERE "customerCode" = :cc'), {'cc': l_cc})
                neon_cu_id = res_cu.scalar()
                
                if neon_cu_id:
                    inserts.append({
                        'plan_type': l_plan,
                        'customer_id': neon_cu_id,
                        'project_name': l_proj,
                        'status': l_status,
                        'log_date': l_log,
                        'due_date': l_due,
                        'completion_date': l_comp,
                        'notes': l_notes,
                        'last_updated_by': l_by or 'System/SafeSync',
                        'last_updated_at': l_at,
                        'estimator_id': l_est_id,
                        'branch_id': 1
                    })

        print(f"Proposed: {len(updates)} updates, {len(inserts)} inserts.")

        if updates:
            print("\nSummary of Updates:")
            for u in updates[:10]:
                print(f"  Bid {u['id']} ({u['reason']}) -> EstID: {u['estimator_id']}")
            if len(updates) > 10: print(f"  ... and {len(updates)-10} more.")

        if inserts:
            print("\nSummary of Inserts:")
            for i in inserts[:10]:
                print(f"  {i['project_name']} (CC_ID: {i['customer_id']})")
            if len(inserts) > 10: print(f"  ... and {len(inserts)-10} more.")

        if not commit:
            print("\nDRY RUN. Use --commit to apply.")
            return

        # Apply updates
        for u in updates:
            conn.execute(sa.text("""
                UPDATE bid SET
                    status = :status, estimator_id = :estimator_id,
                    completion_date = :completion_date, due_date = :due_date,
                    notes = :notes, last_updated_by = :last_updated_by,
                    last_updated_at = :last_updated_at, plan_type = :plan_type
                WHERE id = :id
            """), u)
        
        # Apply inserts
        for i in inserts:
            conn.execute(sa.text("""
                INSERT INTO bid (
                    plan_type, customer_id, project_name, status, log_date,
                    due_date, completion_date, notes, last_updated_by,
                    last_updated_at, estimator_id, branch_id
                ) VALUES (
                    :plan_type, :customer_id, :project_name, :status, :log_date,
                    :due_date, :completion_date, :notes, :last_updated_by,
                    :last_updated_at, :estimator_id, :branch_id
                )
            """), i)
            
        conn.commit()
        print("\nSuccessfully applied all changes to Neon.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--commit', action='store_true')
    args = parser.parse_args()
    sync(commit=args.commit)
