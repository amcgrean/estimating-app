import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from project import create_app, db
from project.models import UserSecurity

app = create_app()
app.app_context().push()

def insert_initial_user_security_data():
    initial_data = [
        {'user_type_id': 3, 'admin': False, 'estimating': False, 'bid_request': False, 'design': True, 'ewp': False, 'service': False, 'install': False, 'picking': False, 'work_orders': False, 'dashboards': True, 'security_10': False, 'security_11': False, 'security_12': False, 'security_13': False, 'security_14': False, 'security_15': False, 'security_16': False, 'security_17': False, 'security_18': False, 'security_19': False, 'security_20': False},
        {'user_type_id': 4, 'admin': False, 'estimating': False, 'bid_request': False, 'design': False, 'ewp': False, 'service': False, 'install': False, 'picking': True, 'work_orders': False, 'dashboards': False, 'security_10': False, 'security_11': False, 'security_12': False, 'security_13': False, 'security_14': False, 'security_15': False, 'security_16': False, 'security_17': False, 'security_18': False, 'security_19': False, 'security_20': False},
        {'user_type_id': 5, 'admin': False, 'estimating': True, 'bid_request': True, 'design': True, 'ewp': True, 'service': True, 'install': True, 'picking': True, 'work_orders': True, 'dashboards': True, 'security_10': True, 'security_11': True, 'security_12': True, 'security_13': True, 'security_14': True, 'security_15': True, 'security_16': True, 'security_17': True, 'security_18': True, 'security_19': True, 'security_20': True},
        {'user_type_id': 6, 'admin': False, 'estimating': True, 'bid_request': True, 'design': False, 'ewp': True, 'service': False, 'install': False, 'picking': False, 'work_orders': False, 'dashboards': True, 'security_10': False, 'security_11': False, 'security_12': False, 'security_13': False, 'security_14': False, 'security_15': False, 'security_16': False, 'security_17': False, 'security_18': False, 'security_19': False, 'security_20': False},
        {'user_type_id': 7, 'admin': False, 'estimating': False, 'bid_request': False, 'design': False, 'ewp': False, 'service': True, 'install': False, 'picking': False, 'work_orders': False, 'dashboards': True, 'security_10': False, 'security_11': False, 'security_12': False, 'security_13': False, 'security_14': False, 'security_15': False, 'security_16': False, 'security_17': False, 'security_18': False, 'security_19': False, 'security_20': False},
        {'user_type_id': 8, 'admin': False, 'estimating': False, 'bid_request': False, 'design': False, 'ewp': False, 'service': False, 'install': True, 'picking': False, 'work_orders': False, 'dashboards': True, 'security_10': False, 'security_11': False, 'security_12': False, 'security_13': False, 'security_14': False, 'security_15': False, 'security_16': False, 'security_17': False, 'security_18': False, 'security_19': False, 'security_20': False},
        {'user_type_id': 9, 'admin': False, 'estimating': False, 'bid_request': False, 'design': False, 'ewp': False, 'service': False, 'install': False, 'picking': False, 'work_orders': True, 'dashboards': False, 'security_10': False, 'security_11': False, 'security_12': False, 'security_13': False, 'security_14': False, 'security_15': False, 'security_16': False, 'security_17': False, 'security_18': False, 'security_19': False, 'security_20': False},
        {'user_type_id': 10, 'admin': False, 'estimating': False, 'bid_request': True, 'design': False, 'ewp': False, 'service': True, 'install': False, 'picking': True, 'work_orders': True, 'dashboards': True, 'security_10': False, 'security_11': False, 'security_12': False, 'security_13': False, 'security_14': False, 'security_15': False, 'security_16': False, 'security_17': False, 'security_18': False, 'security_19': False, 'security_20': False},
        {'user_type_id': 11, 'admin': False, 'estimating': False, 'bid_request': True, 'design': False, 'ewp': False, 'service': True, 'install': False, 'picking': False, 'work_orders': False, 'dashboards': False, 'security_10': False, 'security_11': False, 'security_12': False, 'security_13': False, 'security_14': False, 'security_15': False, 'security_16': False, 'security_17': False, 'security_18': False, 'security_19': False, 'security_20': False},
    ]
    
    for data in initial_data:
        user_security = UserSecurity(**data)
        db.session.add(user_security)
    db.session.commit()

if __name__ == '__main__':
    insert_initial_user_security_data()
    print("Initial user security data inserted successfully.")
