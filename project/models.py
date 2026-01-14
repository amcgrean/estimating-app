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
    sales_rep_id = db.Column(db.Integer, db.ForeignKey('sales_rep.id'), nullable=True)
    project_name = db.Column(db.String(100), nullable=False)
    estimator_id = db.Column(db.Integer, db.ForeignKey('estimator.estimatorID', name='fk_estimator_id'), nullable=True)
    status = db.Column(db.String(50), default='Incomplete')
    log_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, default=datetime.utcnow() + timedelta(weeks=2))
    completion_date = db.Column(db.DateTime, nullable=True)
    
    # New Fields for Enhancements
    # New Fields for Enhancements
    bid_date = db.Column(db.DateTime, nullable=True)
    flexible_bid_date = db.Column(db.Boolean, default=False)
    
    # Spec Include Flags (Control visibility and validation)
    include_specs = db.Column(db.Boolean, default=False) # Master toggle
    include_framing = db.Column(db.Boolean, default=False)
    include_siding = db.Column(db.Boolean, default=False)
    include_shingle = db.Column(db.Boolean, default=False)
    include_deck = db.Column(db.Boolean, default=False)
    include_trim = db.Column(db.Boolean, default=False)
    include_window = db.Column(db.Boolean, default=False)
    include_door = db.Column(db.Boolean, default=False)

    framing_notes = db.Column(db.Text, nullable=True)
    siding_notes = db.Column(db.Text, nullable=True)
    deck_notes = db.Column(db.Text, nullable=True)
    trim_notes = db.Column(db.Text, nullable=True)
    window_notes = db.Column(db.Text, nullable=True)
    door_notes = db.Column(db.Text, nullable=True)
    shingle_notes = db.Column(db.Text, nullable=True)
    
    # Detailed Specs Relationships (One-to-One)
    framing = db.relationship('Framing', backref='bid', uselist=False, cascade="all, delete-orphan")
    siding = db.relationship('Siding', backref='bid', uselist=False, cascade="all, delete-orphan")
    shingle = db.relationship('Shingle', backref='bid', uselist=False, cascade="all, delete-orphan")
    deck = db.relationship('Deck', backref='bid', uselist=False, cascade="all, delete-orphan")
    trim = db.relationship('Trim', backref='bid', uselist=False, cascade="all, delete-orphan")
    window = db.relationship('Window', backref='bid', uselist=False, cascade="all, delete-orphan")
    door = db.relationship('Door', backref='bid', uselist=False, cascade="all, delete-orphan")
    
    # File Upload Paths (S3 Keys)
    plan_filename = db.Column(db.String(255), nullable=True)
    email_filename = db.Column(db.String(255), nullable=True)

    notes = db.Column(db.Text, nullable=True)
    last_updated_by = db.Column(db.String(150), nullable=True)
    last_updated_at = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)

    branch_id = db.Column(db.Integer, db.ForeignKey('branch.branch_id'), nullable=True)
    
    customer = db.relationship('Customer', backref=db.backref('bid', lazy=True))
    sales_rep = db.relationship('SalesRep', backref=db.backref('bids', lazy=True))
    estimator = db.relationship('Estimator', backref=db.backref('bid', lazy=True))
    branch = db.relationship('Branch', backref=db.backref('bids', lazy=True))
    files = db.relationship('BidFile', backref='bid', cascade="all, delete-orphan", lazy=True)

    @staticmethod
    def before_update(mapper, connection, target):
        if target.status == 'Complete':
            target.completion_date = datetime.utcnow()
        # Check if current_user is available (might be None in scripts)
        if current_user and current_user.is_authenticated:
            target.last_updated_by = current_user.username
        else:
            target.last_updated_by = 'System/Script'
        target.last_updated_at = datetime.utcnow()

db.event.listen(Bid, 'before_update', Bid.before_update)


class BidFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bid_id = db.Column(db.Integer, db.ForeignKey('bid.id'), nullable=False)
    file_key = db.Column(db.String(255), nullable=False) # S3 Key
    filename = db.Column(db.String(255), nullable=False) # Original filename
    file_type = db.Column(db.String(50), nullable=True) # e.g. 'plan', 'email', 'other'
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<BidFile {self.filename}>'


class NotificationRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False) # e.g., 'new_bid'
    
    # Recipient Configuration
    recipient_type = db.Column(db.String(50), nullable=False) 
    recipient_id = db.Column(db.Integer, nullable=True) 
    recipient_name = db.Column(db.String(100), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<NotificationRule {self.event_type} -> {self.recipient_type}:{self.recipient_id}>'


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customerCode = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False, unique=False)
    branch_id = db.Column(db.Integer, db.ForeignKey('branch.branch_id'), nullable=True)
    
    branch = db.relationship('Branch', backref=db.backref('customers', lazy=True))
    sales_agent = db.Column(db.String(150), nullable=True)

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
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        try:
            return bcrypt.check_password_hash(self.password, password)
        except ValueError:
            # Likely an "Invalid salt" error due to legacy/plain-text password in DB
            # Fallback: check plain text
            if self.password == password:
                # Optional: You could auto-migrate the password here if you had access to db.session
                return True
            return False

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
    bid = db.relationship('Bid', backref=db.backref('activities', lazy=True, cascade="all, delete-orphan"))

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
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True) # Deprecated
    bid_id = db.Column(db.Integer, db.ForeignKey('bid.id'), nullable=True) # New Link
    plate = db.Column(db.String(50), nullable=True)
    lot_type = db.Column(db.String(50), nullable=True)
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
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    bid_id = db.Column(db.Integer, db.ForeignKey('bid.id'), nullable=True)
    lap_type = db.Column(db.String(50), nullable=True)
    panel_type = db.Column(db.String(50), nullable=True)
    shake_type = db.Column(db.String(50), nullable=True)
    soffit_trim = db.Column(db.String(50), nullable=True)
    window_trim_detail = db.Column(db.String(50), nullable=True)
    siding_notes = db.Column(db.Text, nullable=True)

    project = db.relationship('Project', backref=db.backref('siding', uselist=False))


class Shingle(db.Model):
    __tablename__ = 'shingle'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    bid_id = db.Column(db.Integer, db.ForeignKey('bid.id'), nullable=True)
    shingle_notes = db.Column(db.Text, nullable=True)

    project = db.relationship('Project', backref=db.backref('shingle', uselist=False))


class Deck(db.Model):
    __tablename__ = 'deck'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    bid_id = db.Column(db.Integer, db.ForeignKey('bid.id'), nullable=True)
    decking_type = db.Column(db.String(50), nullable=True)
    railing_type = db.Column(db.String(50), nullable=True)
    stairs = db.Column(db.String(50), nullable=True)
    deck_notes = db.Column(db.Text, nullable=True)

    project = db.relationship('Project', backref=db.backref('deck', uselist=False))


class Door(db.Model):
    __tablename__ = 'door'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    bid_id = db.Column(db.Integer, db.ForeignKey('bid.id'), nullable=True)
    door_notes = db.Column(db.Text, nullable=True)

    project = db.relationship('Project', backref=db.backref('door', uselist=False))


class Window(db.Model):
    __tablename__ = 'window'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    bid_id = db.Column(db.Integer, db.ForeignKey('bid.id'), nullable=True)
    window_notes = db.Column(db.Text, nullable=True)

    project = db.relationship('Project', backref=db.backref('window', uselist=False))


class Trim(db.Model):
    __tablename__ = 'trim'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    bid_id = db.Column(db.Integer, db.ForeignKey('bid.id'), nullable=True)
    base = db.Column(db.String(50), nullable=True)
    case = db.Column(db.String(50), nullable=True)
    stair_material = db.Column(db.String(50), nullable=True)
    door_material_type = db.Column(db.String(50), nullable=True)
    number_of_panels = db.Column(db.String(50), nullable=True)
    door_hardware = db.Column(db.String(50), nullable=True)
    built_in_materials_type = db.Column(db.String(50), nullable=True)
    plywood_1x_count = db.Column(db.String(50), nullable=True)
    specify_count = db.Column(db.String(50), nullable=True)
    trim_allowance = db.Column(db.String(50), nullable=True)
    trim_notes = db.Column(db.Text, nullable=True)

    project = db.relationship('Project', backref=db.backref('trim', uselist=False))



