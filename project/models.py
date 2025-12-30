from datetime import datetime, timedelta
from . import db
from project.utils import safe_str_cmp
from flask_login import UserMixin,current_user
from . import bcrypt
from flask import current_app


class Branch(db.Model):
    branch_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    branch_name = db.Column(db.String(255), nullable=False)
    branch_code = db.Column(db.String(255), nullable=False)
    branch_type = db.Column(db.Integer, nullable=False)

class Estimator(db.Model):
    estimatorID = db.Column(db.Integer, primary_key=True)
    estimatorName = db.Column(db.String(100), nullable=False)
    estimatorUsername = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # New column

class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_type = db.Column(db.String(50), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    project_name = db.Column(db.String(100), nullable=False)
    estimator_id = db.Column(db.Integer, db.ForeignKey('estimator.estimatorID', name='fk_estimator_id'), nullable=True)
    status = db.Column(db.String(50), default='incomplete')
    log_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, default=datetime.utcnow() + timedelta(weeks=2))
    completion_date = db.Column(db.DateTime, nullable=True)  # New column
    notes = db.Column(db.Text, nullable=True)  # New column
    last_updated_by = db.Column(db.String(150), nullable=True)
    last_updated_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)

    branch_id = db.Column(db.Integer, db.ForeignKey('branch.branch_id'), nullable=True)
    
    customer = db.relationship('Customer', backref=db.backref('bid', lazy=True))
    estimator = db.relationship('Estimator', backref=db.backref('bid', lazy=True))
    branch = db.relationship('Branch', backref=db.backref('bids', lazy=True))

    @staticmethod
    def before_update(mapper, connection, target):
        if target.status == 'Complete':
            target.completion_date = datetime.utcnow()
        if current_user.is_authenticated:
            target.last_updated_by = current_user.username
        else:
            target.last_updated_by = 'Anonymous'
        target.last_updated_at = datetime.utcnow()

db.event.listen(Bid, 'before_update', Bid.before_update)


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customerCode = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False, unique=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.branch_id'), nullable=True)
    
    branch = db.relationship('Branch', backref=db.backref('customers', lazy=True))

class Design(db.Model):  # New table
    id = db.Column(db.Integer, primary_key=True)
    planNumber = db.Column(db.String(10), nullable=False, unique=True)  # number that will autogenerate later on
    plan_name = db.Column(db.String(100), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    project_address = db.Column(db.String(200), nullable=False)
    contractor = db.Column(db.String(100), nullable=True)
    log_date = db.Column(db.DateTime, default=datetime.utcnow)
    preliminary_set_date = db.Column(db.DateTime, nullable=True)
    designer_id = db.Column(db.Integer, db.ForeignKey('estimator.estimatorID'), nullable=True)  # Changed to nullable=True
    status = db.Column(db.String(50), default='Active')  # Default to 'Active'
    plan_description = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    last_updated_by = db.Column(db.String(150), nullable=True)
    last_updated_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)

    branch_id = db.Column(db.Integer, db.ForeignKey('branch.branch_id'), nullable=True)

    customer = db.relationship('Customer', backref=db.backref('designs', lazy=True))
    designer = db.relationship('Estimator', backref=db.backref('designs', lazy=True))
    branch = db.relationship('Branch', backref=db.backref('designs', lazy=True))

class UserType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    usertype_id = db.Column(db.Integer, db.ForeignKey('user_type.id'), nullable=False)
    estimatorID = db.Column(db.Integer, db.ForeignKey('estimator.estimatorID'), nullable=True)
    sales_rep_id = db.Column(db.Integer, db.ForeignKey('sales_rep.id'), nullable=True)
    user_branch_id = db.Column(db.Integer, db.ForeignKey('branch.branch_id'), nullable=True)

    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_estimator = db.Column(db.Boolean, default=False)
    login_count = db.Column(db.Integer, default=0)

    usertype = db.relationship('UserType', backref=db.backref('users', lazy=True))
    estimator = db.relationship('Estimator', backref=db.backref('estimators', lazy=True))  # Changed backref name
    branch = db.relationship('Branch', backref=db.backref('branches', lazy=True))  # Changed backref name
    sales_rep = db.relationship('SalesRep', backref='users', lazy=True)  # Reference the backref here only

    def set_password(self, password):
        self.password = password

    def check_password(self, password):
        return self.password == password

    def get_id(self):
        return self.id

class LoginActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    logged_in = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    logged_out = db.Column(db.DateTime, nullable=True)
    user = db.relationship('User', backref=db.backref('login_activities', lazy=True))

class BidActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    bid_id = db.Column(db.Integer, db.ForeignKey('bid.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # e.g., 'created', 'updated', 'deleted'
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('bid_activities', lazy=True))
    bid = db.relationship('Bid', backref=db.backref('activities', lazy=True))

class GeneralAudit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    model_name = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    changes = db.Column(db.Text, nullable=True)  # Stores changes in a JSON format
    user = db.relationship('User', backref=db.backref('audits', lazy=True))

class SalesRep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True)


class EWP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_number = db.Column(db.String(255), nullable=False)
    sales_rep_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Correct foreign key reference
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)  # Correct foreign key reference
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
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.branch_id'), nullable=True)

    customer = db.relationship('Customer', backref=db.backref('ewps', lazy=True))
    sales_rep = db.relationship('User', backref=db.backref('ewps', lazy=True))
    branch = db.relationship('Branch', backref=db.backref('ewps', lazy=True))

class UserSecurity(db.Model):
    __tablename__ = 'user_security'

    user_type_id = db.Column(db.Integer, db.ForeignKey('user_type.id'), primary_key=True)
    admin = db.Column(db.Boolean, nullable=False)
    estimating = db.Column(db.Boolean, nullable=False)
    bid_request = db.Column(db.Boolean, nullable=False)
    design = db.Column(db.Boolean, nullable=False)
    ewp = db.Column(db.Boolean, nullable=False)
    service = db.Column(db.Boolean, nullable=False)
    install = db.Column(db.Boolean, nullable=False)
    picking = db.Column(db.Boolean, nullable=False)
    work_orders = db.Column(db.Boolean, nullable=False)
    dashboards = db.Column(db.Boolean, nullable=False)
    security_10 = db.Column(db.Boolean, nullable=False)
    security_11 = db.Column(db.Boolean, nullable=False)
    security_12 = db.Column(db.Boolean, nullable=False)
    security_13 = db.Column(db.Boolean, nullable=False)
    security_14 = db.Column(db.Boolean, nullable=False)
    security_15 = db.Column(db.Boolean, nullable=False)
    security_16 = db.Column(db.Boolean, nullable=False)
    security_17 = db.Column(db.Boolean, nullable=False)
    security_18 = db.Column(db.Boolean, nullable=False)
    security_19 = db.Column(db.Boolean, nullable=False)
    security_20 = db.Column(db.Boolean, nullable=False)

class ITService(db.Model):
    __tablename__ = 'it_service'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    issue_type = db.Column(db.String(255), nullable=False)
    createdby = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='Open', nullable=False)
    updatedby = db.Column(db.String(255), nullable=True)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    createdDate = db.Column(db.DateTime, default=datetime.utcnow)  # Add this field if it doesn't exist

class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=True)  # FK to Customer table
    sales_rep_id = db.Column(db.Integer, db.ForeignKey('sales_rep.id'), nullable=False)  # Relates to SalesRep
    contractor = db.Column(db.String(255), nullable=False)
    project_address = db.Column(db.String(255), nullable=False)
    contractor_phone = db.Column(db.String(15), nullable=True)
    contractor_email = db.Column(db.String(255), nullable=True)
    include_framing = db.Column(db.Boolean, default=False, nullable=False)
    include_siding = db.Column(db.Boolean, default=False, nullable=False)
    include_shingles = db.Column(db.Boolean, default=False, nullable=False)
    include_deck = db.Column(db.Boolean, default=False, nullable=False)
    include_doors = db.Column(db.Boolean, default=False, nullable=False)
    include_windows = db.Column(db.Boolean, default=False, nullable=False)
    include_trim = db.Column(db.Boolean, default=False, nullable=False)
    notes = db.Column(db.Text, nullable=True)  # Placeholder for additional details or future notes
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_updated_by = db.Column(db.String(150), nullable=True)  # Tracks user who last updated
    last_updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.branch_id'), nullable=True)

    # Relationships
    sales_rep = db.relationship('SalesRep', backref=db.backref('projects', lazy=True))  # SalesRep relation
    customer = db.relationship('Customer', backref=db.backref('projects', lazy=True))
    branch = db.relationship('Branch', backref=db.backref('projects', lazy=True))

    def __repr__(self):
        return f"<Project id={self.id} contractor={self.contractor}>"

class Framing(db.Model):
    __tablename__ = 'framing'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    plate = db.Column(db.String(50), nullable=False)
    lot_type = db.Column(db.String(50), nullable=False)
    basement_wall_height = db.Column(db.String(50), nullable=True)
    basement_exterior_walls = db.Column(db.String(50), nullable=False)
    basement_interior_walls = db.Column(db.String(50), nullable=False)
    floor_framing = db.Column(db.String(50), nullable=False)
    floor_sheeting = db.Column(db.String(50), nullable=False)
    floor_adhesive = db.Column(db.String(50), nullable=False)
    exterior_walls = db.Column(db.String(50), nullable=False)
    first_floor_wall_height = db.Column(db.String(50), nullable=False)
    second_floor_wall_height = db.Column(db.String(50), nullable=True)
    wall_sheeting = db.Column(db.String(50), nullable=False)
    roof_trusses = db.Column(db.String(50), nullable=False)
    roof_sheeting = db.Column(db.String(50), nullable=False)
    framing_notes = db.Column(db.Text, nullable=True)

    project = db.relationship('Project', backref=db.backref('framing', uselist=False))


class Siding(db.Model):
    __tablename__ = 'siding'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    lap_type = db.Column(db.String(50), nullable=False)
    panel_type = db.Column(db.String(50), nullable=False)
    shake_type = db.Column(db.String(50), nullable=False)
    soffit_trim = db.Column(db.String(50), nullable=False)
    window_trim_detail = db.Column(db.String(50), nullable=False)
    siding_notes = db.Column(db.Text, nullable=True)

    project = db.relationship('Project', backref=db.backref('siding', uselist=False))


class Shingle(db.Model):
    __tablename__ = 'shingle'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    shingle_notes = db.Column(db.Text, nullable=False)

    project = db.relationship('Project', backref=db.backref('shingle', uselist=False))


class Deck(db.Model):
    __tablename__ = 'deck'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    decking_type = db.Column(db.String(50), nullable=False)
    railing_type = db.Column(db.String(50), nullable=False)
    stairs = db.Column(db.String(50), nullable=False)
    deck_notes = db.Column(db.Text, nullable=True)

    project = db.relationship('Project', backref=db.backref('deck', uselist=False))


class Door(db.Model):
    __tablename__ = 'door'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    door_notes = db.Column(db.Text, nullable=False)

    project = db.relationship('Project', backref=db.backref('door', uselist=False))


class Window(db.Model):
    __tablename__ = 'window'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    window_notes = db.Column(db.Text, nullable=False)

    project = db.relationship('Project', backref=db.backref('window', uselist=False))


class Trim(db.Model):
    __tablename__ = 'trim'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    base = db.Column(db.String(50), nullable=False)
    case = db.Column(db.String(50), nullable=False)
    stair_material = db.Column(db.String(50), nullable=False)
    door_material_type = db.Column(db.String(50), nullable=False)
    number_of_panels = db.Column(db.String(50), nullable=False)
    door_hardware = db.Column(db.String(50), nullable=False)
    built_in_materials_type = db.Column(db.String(50), nullable=False)
    plywood_1x_count = db.Column(db.String(50), nullable=True)
    specify_count = db.Column(db.String(50), nullable=False)
    trim_allowance = db.Column(db.String(50), nullable=True)
    trim_notes = db.Column(db.Text, nullable=True)

    project = db.relationship('Project', backref=db.backref('trim', uselist=False))



