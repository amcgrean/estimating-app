from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, TextAreaField, SubmitField, FileField, PasswordField, HiddenField, DateField, FormField, SelectMultipleField
from wtforms.validators import DataRequired, Optional, Regexp, EqualTo, ValidationError
from flask_wtf.file import FileAllowed
from flask_login import current_user
from project import db
from datetime import datetime, timedelta
import re
from .models import UserType, UserSecurity, Estimator, Branch, GeneralAudit, SalesRep, Customer

# Custom email validator
def simple_email_check(form, field):
    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
    if not email_regex.match(field.data):
        raise ValidationError('Invalid email address')

class BaseForm(FlaskForm):
    def log_activity(self, instance, action):
        # logging logic suppressed for brevity if acceptable, but better to keep original
        if hasattr(instance, 'id'):
            model_name = instance.__class__.__name__
            audit_entry = GeneralAudit(
                user_id=current_user.id,
                model_name=model_name,
                action=action,
                timestamp=datetime.utcnow(),
                changes=str(instance)
            )
            db.session.add(audit_entry)
            db.session.commit()

    def save_instance(self, instance):
        is_new = instance.id is None
        db.session.add(instance)
        db.session.commit()
        # simplified audit logging to avoid circular deps or complex logic during migration if needed
        # self.log_activity(instance, 'created' if is_new else 'updated')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(BaseForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), simple_email_check])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    usertype_id = SelectField('User Type', validators=[DataRequired()])
    estimatorID = SelectField('Estimator', coerce=int, choices=[], validators=[Optional()])
    user_branch_id = SelectField('Branch', coerce=int, choices=[], validators=[DataRequired()])
    is_estimator = BooleanField('Is Estimator')
    submit = SubmitField('Register')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usertype_id.choices = [(ut.id, ut.name) for ut in UserType.query.all()]
        self.estimatorID.choices = [(e.estimatorID, e.estimatorName) for e in Estimator.query.all()]
        self.user_branch_id.choices = [(b.branch_id, b.branch_name) for b in Branch.query.all()]

class UserForm(BaseForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), simple_email_check])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    usertype_id = SelectField('User Type', validators=[DataRequired()], coerce=int)
    estimatorID = SelectField('Estimator', coerce=int, choices=[], validators=[Optional()])
    user_branch_id = SelectField('Branch', coerce=int, choices=[], validators=[DataRequired()])
    is_estimator = BooleanField('Is Estimator')
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usertype_id.choices = [(ut.id, ut.name) for ut in UserType.query.all()]
        self.estimatorID.choices = [(e.estimatorID, e.estimatorName) for e in Estimator.query.all()]
        self.user_branch_id.choices = [(b.branch_id, b.branch_name) for b in Branch.query.all()]

class UpdateUserForm(BaseForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    usertype_id = SelectField('User Type', coerce=int, choices=[], validators=[DataRequired()])
    estimatorID = SelectField('Estimator', coerce=int, choices=[], validators=[Optional()])
    user_branch_id = SelectField('Branch', coerce=int, choices=[], validators=[DataRequired()])
    is_estimator = BooleanField('Is Estimator')
    password = PasswordField('New Password (leave blank to keep current password)', validators=[Optional()])
    submit = SubmitField('Update')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.usertype_id.choices = [(ut.id, ut.name) for ut in UserType.query.all()]
        self.estimatorID.choices = [(e.estimatorID, e.estimatorName) for e in Estimator.query.all()]
        self.user_branch_id.choices = [(b.branch_id, b.branch_name) for b in Branch.query.all()]

class UserSettingsForm(BaseForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[Optional()])
    confirm_password = PasswordField('Confirm New Password', validators=[Optional(), EqualTo('password')])
    submit = SubmitField('Update Settings')

class UserTypeForm(BaseForm):
    name = StringField('User Type Name', validators=[DataRequired()])
    submit = SubmitField('Add User Type')

class UserSecurityForm(FlaskForm):
    submit = SubmitField('Update Security')

    def __init__(self, usertypes, *args, **kwargs):
        super(UserSecurityForm, self).__init__(*args, **kwargs)
        for usertype in usertypes:
            self._add_usertype_fields(usertype)

    def _add_usertype_fields(self, usertype):
        security = UserSecurity.query.filter_by(user_type_id=usertype.id).first()
        setattr(self, f'user_type_name_{usertype.id}', BooleanField(default=usertype.name))
        setattr(self, f'user_type_id_{usertype.id}', BooleanField(default=usertype.id, render_kw={'readonly': True}))
        setattr(self, f'admin_{usertype.id}', BooleanField(default=security.admin))
        setattr(self, f'estimating_{usertype.id}', BooleanField(default=security.estimating))
        setattr(self, f'bid_request_{usertype.id}', BooleanField(default=security.bid_request))
        setattr(self, f'design_{usertype.id}', BooleanField(default=security.design))
        setattr(self, f'ewp_{usertype.id}', BooleanField(default=security.ewp))
        setattr(self, f'service_{usertype.id}', BooleanField(default=security.service))
        setattr(self, f'install_{usertype.id}', BooleanField(default=security.install))
        setattr(self, f'picking_{usertype.id}', BooleanField(default=security.picking))
        setattr(self, f'work_orders_{usertype.id}', BooleanField(default=security.work_orders))
        setattr(self, f'dashboards_{usertype.id}', BooleanField(default=security.dashboards))
        setattr(self, f'security_10_{usertype.id}', BooleanField(default=security.security_10))
        setattr(self, f'security_11_{usertype.id}', BooleanField(default=security.security_11))
        setattr(self, f'security_12_{usertype.id}', BooleanField(default=security.security_12))
        setattr(self, f'security_13_{usertype.id}', BooleanField(default=security.security_13))
        setattr(self, f'security_14_{usertype.id}', BooleanField(default=security.security_14))
        setattr(self, f'security_15_{usertype.id}', BooleanField(default=security.security_15))
        setattr(self, f'security_16_{usertype.id}', BooleanField(default=security.security_16))
        setattr(self, f'security_17_{usertype.id}', BooleanField(default=security.security_17))
        setattr(self, f'security_18_{usertype.id}', BooleanField(default=security.security_18))
        setattr(self, f'security_19_{usertype.id}', BooleanField(default=security.security_19))
        setattr(self, f'security_20_{usertype.id}', BooleanField(default=security.security_20))

class DesignForm(BaseForm):
    plan_name = StringField('Plan Name', validators=[DataRequired()])
    project_address = StringField('Project Address', validators=[DataRequired()])
    contractor = StringField('Contractor')
    customer_id = SelectField('Customer', coerce=int, validators=[Optional()])
    designer_id = SelectField('Designer', coerce=int, validators=[Optional()])
    preliminary_set_date = DateField('Preliminary Set Date', format='%Y-%m-%d', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('Active', 'Active'),
        ('Bid Set', 'Bid Set'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold')
    ])
    plan_description = SelectField('Type', choices=[
        ('New Design', 'New Design'),
        ('Redesign', 'Redesign')
    ])
    notes = TextAreaField('Notes')
    branch_id = SelectField('Branch', coerce=int, choices=[])
    submit = SubmitField('Create Design')

class LayoutForm(BaseForm):
    plan_number = StringField('Plan Number', validators=[DataRequired()])
    sales_rep_id = SelectField('Sales Rep', coerce=int)
    customer_id = SelectField('Customer', coerce=int)
    address = StringField('Address', validators=[DataRequired()])
    notes = TextAreaField('Notes')
    login_date = DateField('Login Date', format='%Y-%m-%d', validators=[DataRequired()])
    tji_depth = StringField('TJI Depth', validators=[DataRequired()])
    assigned_designer = StringField('Assigned Designer')
    layout_finalized = DateField('Layout Finalized', format='%Y-%m-%d')
    agility_quote = DateField('Agility Quote', format='%Y-%m-%d')
    imported_stellar = DateField('Imported Stellar', format='%Y-%m-%d')
    branch_id = SelectField('Branch', coerce=int, choices=[])
    submit = SubmitField('Save Changes')

# --- DETAILED SPECS FORMS (NEW) ---

class FramingForm(BaseForm):
    pass


class SidingForm(BaseForm):
    pass

class ShingleForm(BaseForm):
    pass

class DoorForm(BaseForm):
    pass

class WindowForm(BaseForm):
    pass

class TrimForm(BaseForm):
    pass

class DeckForm(BaseForm):
    pass

# --- MAIN BID FORM ---

class BidForm(BaseForm):
    plan_type = SelectField('Plan Type', choices=[('Residential', 'Residential'), ('Commercial', 'Commercial')], validators=[DataRequired()])
    customer_id = SelectField('Customer', coerce=int, validators=[DataRequired()])
    sales_rep_id = SelectField('Sales Rep', coerce=int, validators=[Optional()])
    estimator_id = SelectField('Estimator', coerce=int)
    status = SelectField('Status', choices=[('Incomplete', 'Incomplete'), ('Complete', 'Complete'), ('Hold', 'Hold')])
    project_name = StringField('Project Name', validators=[DataRequired()])
    due_date = DateField('Due Date', format='%Y-%m-%d', default=lambda: (datetime.utcnow() + timedelta(days=14)).date(), validators=[DataRequired()])
    
    # New Enhancement Fields
    bid_date = DateField('Bid Date', format='%Y-%m-%d', validators=[Optional()])
    flexible_bid_date = BooleanField('Flexible Bid Date')
    
    # Spec Controls
    include_specs = BooleanField('Include Specs') # Master toggle
    include_framing = BooleanField('Include Framing')
    include_siding = BooleanField('Include Siding')
    include_shingle = BooleanField('Include Shingle')
    include_deck = BooleanField('Include Deck')
    include_trim = BooleanField('Include Trim')
    include_window = BooleanField('Include Window')
    include_door = BooleanField('Include Door')
    
    # Nested Detailed Specs Forms
    framing = FormField(FramingForm)
    siding = FormField(SidingForm)
    shingle = FormField(ShingleForm)
    deck = FormField(DeckForm)
    trim = FormField(TrimForm)
    window = FormField(WindowForm)
    door = FormField(DoorForm)
    
    # Keep simple notes for fallback or other needs
    # Notes handled by Dynamic Fields now
    # framing_notes = TextAreaField('Framing Notes', validators=[Optional()])
    # siding_notes = TextAreaField('Siding Notes', validators=[Optional()])
    # shingle_notes = TextAreaField('Shingle Notes', validators=[Optional()])
    # deck_notes = TextAreaField('Deck Notes', validators=[Optional()])
    # trim_notes = TextAreaField('Trim Notes', validators=[Optional()])
    # window_notes = TextAreaField('Window Notes', validators=[Optional()])
    # door_notes = TextAreaField('Door Notes', validators=[Optional()])

    plan_key = HiddenField()
    email_key = HiddenField()

    plan_file = FileField('Plan PDF', validators=[Optional(), FileAllowed(['pdf'], 'PDFs only!')])
    email_file = FileField('Email/Doc', validators=[Optional(), FileAllowed(['pdf', 'msg', 'eml', 'png', 'jpg', 'jpeg'], 'Documents or Images!')])

    notes = TextAreaField('Notes')
    branch_id = SelectField('Branch', coerce=int, choices=[])
    submit = SubmitField('Submit')

class CustomerForm(FlaskForm):
    customerCode = StringField('Customer Code', validators=[DataRequired()])
    name = StringField('Customer Name', validators=[DataRequired()])
    sales_agent = StringField('Sales Agent', validators=[Optional()])
    branch_id = SelectField('Branch', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Customer')

class SearchForm(FlaskForm):
    search_input = StringField('Search', validators=[DataRequired()])

class FilterForm(FlaskForm):
    sales_rep = StringField('Sales Rep', validators=[Optional()])
    customer = StringField('Customer', validators=[Optional()])
    login_date = DateField('Login Date', validators=[Optional()])
    layout_date = DateField('Layout Date', validators=[Optional()])
    submit = SubmitField('Filter')

class UploadForm(BaseForm):
    file = FileField('Upload CSV File of Historical Bids', validators=[DataRequired(), FileAllowed(['csv'], 'CSV files only!')])
    submit = SubmitField('Upload')

class BidRequestForm(BaseForm):
    sales_rep = SelectField('Sales Rep Name', validators=[DataRequired()])
    customer_id = SelectField('Customer', coerce=int, validators=[Optional()])  # Dropdown for Customer, coerce ensures int values
    contractor = StringField('Custom Contractor Name', validators=[Optional()])  # Free-text custom entry
    project_address = StringField('Project Address/Name', validators=[DataRequired()])
    contractor_phone = StringField('Contractor/Customer Phone', validators=[Optional()])
    contractor_email = StringField('Contractor/Customer Email', validators=[
        Optional(),
        Regexp(r'^\S+@\S+\.\S+$', message="Invalid email address")
    ])
    branch_id = SelectField('Branch', coerce=int, validators=[DataRequired()])

    include_framing = BooleanField('Framing')
    include_siding = BooleanField('Siding')
    include_shingles = BooleanField('Shingles')
    include_deck = BooleanField('Exterior Deck')
    include_doors = BooleanField('Exterior Doors')
    include_windows = BooleanField('Windows')
    include_trim = BooleanField('Trim')

    file_upload = FileField('File Upload', validators=[Optional()])
    submit = SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(BidRequestForm, self).__init__(*args, **kwargs)

        # Populate sales rep dropdown
        self.sales_rep.choices = [
            ('', 'Select Sales Rep (or Cash if N/A)')
        ] + [(rep.id, rep.name) for rep in SalesRep.query.order_by(SalesRep.name).all()]

        # Populate customer dropdown
        self.customer_id.choices = [
            (0, 'Select Customer')  # Default value, coerce=int will set this as 0
        ] + [(customer.id, customer.name) for customer in Customer.query.order_by(Customer.name).all()]

class ITServiceForm(FlaskForm):
    issue_type = SelectField('Issue Type',
                             choices=[
                                 ('Website Spec Sheet', 'Website Spec Sheet'),
                                 ('Missing or wrong product in bids', 'Missing or wrong product in bids'),
                                 ('other', 'Other')
                             ], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Open', 'Open'), ('In Progress', 'In Progress'), ('Completed', 'Completed')], default='Open')
    notes = TextAreaField('Notes')
    submit = SubmitField('Submit')

class NotificationRuleForm(FlaskForm):
    event_type = SelectField('Trigger Event', validators=[DataRequired()])
    recipient_type = SelectField('Recipient Type', choices=[('role', 'User Role'), ('user', 'Specific User')], validators=[DataRequired()])
    # We will populate these choices dynamically in the view or leave them empty and let JS/Validation handle logic
    recipient_role = SelectField('Role', coerce=int, validators=[Optional()])
    recipient_user = SelectField('User', coerce=int, validators=[Optional()])
    submit = SubmitField('Create Rule')


class BidFieldForm(FlaskForm):
    name = StringField('Field Label', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('General', 'General'), 
        ('Framing', 'Framing'), 
        ('Siding', 'Siding'), 
        ('Shingles', 'Shingles'), 
        ('Deck', 'Deck'), 
        ('Trim', 'Trim'), 
        ('Windows', 'Windows'), 
        ('Doors', 'Doors')
    ], validators=[DataRequired()])
    field_type = SelectField('Input Type', choices=[
        ('text', 'Text Input'), 
        ('textarea', 'Text Area'), 
        ('select', 'Dropdown Menu'), 
        ('checkbox', 'Checkbox')
    ], validators=[DataRequired()])
    options = TextAreaField('Options (for Dropdown)', validators=[Optional()])
    branch_ids = SelectField('Limit to Branch', choices=[], validators=[Optional()], id='branch_ids') # Populated in view, usually multiselect which requires adjustment if SelectMultipleField
    # Note: For multi-select with Select2, capturing data might require SelectMultipleField or specific handling. 
    # For now, we'll try SelectMultipleField if possible, or just text handling. 
    # Let's use SelectMultipleField for branch_ids.
    is_required = BooleanField('Required Field')
    sort_order = StringField('Sort Order', default="0")
    submit = SubmitField('Save Field')
