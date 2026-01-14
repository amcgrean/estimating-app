from flask import Blueprint, jsonify
from project.models import User, UserType, SalesRep, Branch

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
            'branch_id': u.user_branch_id,
            'sales_rep_id': u.sales_rep_id,
            'sales_rep_name': u.sales_rep.name if u.sales_rep else 'None'
        })
    return jsonify(data)
