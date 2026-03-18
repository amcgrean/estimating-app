from flask import Blueprint, jsonify
from project import db
from project.models import User, UserType, Branch, Bid, Customer

debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/users')
def debug_users():
    users = User.query.all()
    data = []
    for u in users:
        data.append({
            'id': u.id,
            'username': u.username,
            'usertype': u.usertype.name if u.usertype else 'None',
            'branch_id': u.user_branch_id
        })
    return jsonify(data)

@debug_bp.route('/bids')
def debug_bids():
    total = Bid.query.count()

    # Breakdown by status
    status_counts = db.session.query(Bid.status, db.func.count(Bid.id)).group_by(Bid.status).all()

    # Breakdown by branch_id
    branch_counts = db.session.query(Bid.branch_id, db.func.count(Bid.id)).group_by(Bid.branch_id).all()

    # Bids with NULL customer_id or customer_id not in customer table
    null_customer = Bid.query.filter(Bid.customer_id == None).count()
    orphan_customer = db.session.query(Bid).outerjoin(Customer, Bid.customer_id == Customer.id).filter(Customer.id == None, Bid.customer_id != None).count()

    # Most recent 5 bids
    recent = Bid.query.order_by(Bid.id.desc()).limit(5).all()
    recent_list = [{
        'id': b.id,
        'project_name': b.project_name,
        'status': b.status,
        'branch_id': b.branch_id,
        'customer_id': b.customer_id,
        'log_date': str(b.log_date)
    } for b in recent]

    return jsonify({
        'total_bids': total,
        'by_status': {s: c for s, c in status_counts},
        'by_branch_id': {str(b): c for b, c in branch_counts},
        'null_customer_id': null_customer,
        'orphan_customer_id': orphan_customer,
        'recent_5': recent_list
    })
