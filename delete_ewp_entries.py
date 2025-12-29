from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/amcgrean/mysite/instance/bids.db?timeout=30'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class EWP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_number = db.Column(db.String(255), nullable=False)
    sales_rep_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)
    address = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    login_date = db.Column(db.Date, nullable=False)
    tji_depth = db.Column(db.String(255), nullable=False)
    assigned_designer = db.Column(db.String(255), nullable=True)
    layout_finalized = db.Column(db.Date, nullable=True)
    agility_quote = db.Column(db.Date, nullable=True)
    imported_stellar = db.Column(db.Date, nullable=True)
    last_updated_by = db.Column(db.String(150), nullable=True)
    last_updated_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)

with app.app_context():
    try:
        rows_deleted = db.session.query(EWP).filter(EWP.id.between(1, 100)).delete(synchronize_session='fetch')
        db.session.commit()
        print(f"Deleted {rows_deleted} rows from the EWP table.")
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting rows: {e}")
