from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, TextAreaField, SubmitField, FileField, PasswordField, HiddenField, DateField
from wtforms.validators import DataRequired, Optional, Regexp, EqualTo, ValidationError
from datetime import datetime, timedelta
import re
from .models import UserType, UserSecurity, Estimator, Branch, GeneralAudit, SalesRep, Customer
from flask_wtf.file import FileAllowed
from flask_login import current_user
from project import db

# Custom email validator
def simple_email_check(form, field):
    email_regex = re.compile(r"[^@]+@[^@]+\.[^@]+")
    if not email_regex.match(field.data):
        raise ValidationError('Invalid email address')

class BaseForm(FlaskForm):
    def log_activity(self, instance, action):
        print(f"Logging activity: {action} for {instance}")
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
        print(f"Saving instance: {instance}")
        is_new = instance.id is None
        db.session.add(instance)
        db.session.commit()
        self.log_activity(instance, 'created' if is_new else 'updated')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

    def __init__(self, *args, **kwargs):
        print("LoginForm instantiated")
        super(LoginForm, self).__init__(*args, **kwargs)

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
    status = SelectField('Status', choices=[
        ('Active', 'Active'),
        ('Bid Set', 'Bid Set'),
        ('Cancelled', 'Cancelled'),
        ('Completed', 'Completed'),
        ('On Hold', 'On Hold')
    ])
    notes = TextAreaField('Notes')
    branch_id = SelectField('Branch', coerce=int, choices=[])
    submit = SubmitField('Save Changes')

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

class BidForm(BaseForm):
    plan_type = SelectField('Plan Type', choices=[('Residential', 'Residential'), ('Commercial', 'Commercial')], validators=[DataRequired()])
    customer_id = SelectField('Customer', coerce=int, validators=[DataRequired()])
    estimator_id = SelectField('Estimator', coerce=int)
    status = SelectField('Status', choices=[('Incomplete', 'Incomplete'), ('Complete', 'Complete'), ('Hold', 'Hold')])
    project_name = StringField('Project Name', validators=[DataRequired()])
    due_date = DateField('Due Date', format='%Y-%m-%d', default=lambda: (datetime.utcnow() + timedelta(days=14)).date(), validators=[DataRequired()])
    notes = TextAreaField('Notes')
    branch_id = SelectField('Branch', coerce=int, choices=[])
    submit = SubmitField('Submit')

class CustomerForm(FlaskForm):
    customerCode = StringField('Customer Code', validators=[DataRequired()])
    name = StringField('Customer Name', validators=[DataRequired()])
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

from wtforms import SelectField

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

class FramingForm(BaseForm):
    plate = SelectField('Plate', choices=[
        ('Treated', 'Treated'), ('TimberStrand', 'TimberStrand'),
        ('Treated w/Triple', 'Treated w/Triple'), ('TimberStrand w/Triple', 'TimberStrand w/Triple')
    ], validators=[DataRequired()])
    lot_type = SelectField('Lot Type', choices=[
        ('Walkout', 'Walkout'), ('Daylight', 'Daylight'), ('Flat Lot', 'Flat Lot'), ('Slab on Grade', 'Slab on Grade')
    ], validators=[DataRequired()])
    basement_wall_height = SelectField('Basement Wall Height', choices=[
        ('8\'', '8\''), ('9\'', '9\''), ('10\'', '10\'')
    ], validators=[Optional()])
    basement_exterior_walls = SelectField('Basement Exterior Walls', choices=[
        ('2x4', '2×4'), ('2x6', '2×6'), ('Other(specify in notes)', 'Other(specify in notes)')
    ], validators=[DataRequired()])
    basement_interior_walls = SelectField('Basement Interior Walls', choices=[
        ('As Shown', 'As Shown'), ('Bearing Only', 'Bearing Only')
    ], validators=[DataRequired()])
    floor_framing = SelectField('Floor Framing', choices=[
        ('TJI I-Joist', 'TJI I-Joist'), ('Floor Trusses', 'Floor Trusses'),
        ('2x', '2x'), ('N/a', 'N/a')
    ], validators=[DataRequired()])
    floor_sheeting = SelectField('Floor Sheeting', choices=[
        ('Edge', 'Edge'), ('Gold', 'Gold'), ('Advantech', 'Advantech')
    ], validators=[DataRequired()])
    floor_adhesive = SelectField('Floor Adhesive', choices=[
        ('SF-450', 'SF-450'), ('Advantech', 'Advantech')
    ], validators=[DataRequired()])
    exterior_walls = SelectField('Exterior Walls', choices=[
        ('2x4', '2×4'), ('2x6', '2×6'), ('Other(specify in notes)', 'Other(specify in notes)')
    ], validators=[DataRequired()])
    first_floor_wall_height = SelectField('1st Floor Wall Height', choices=[
        ('8\'', '8\''), ('9\'', '9\''), ('10\'', '10\''), ('12\'', '12\''), ('Per Plan', 'Per Plan')
    ], validators=[DataRequired()])
    second_floor_wall_height = SelectField('2nd Floor Wall Height', choices=[
        ('8\'', '8\''), ('9\'', '9\''), ('10\'', '10\''), ('12\'', '12\''), ('Per Plan', 'Per Plan')
    ], validators=[Optional()])
    wall_sheeting = SelectField('Wall Sheeting', choices=[
        ('7/16" OSB', '7/16" OSB'), ('1/2" OSB', '1/2" OSB'), ('Zip Panels', 'Zip Panels')
    ], validators=[DataRequired()])
    roof_trusses = SelectField('Roof Trusses', choices=[
        ('Yes', 'Yes'), ('By Others', 'By Others')
    ], validators=[DataRequired()])
    roof_sheeting = SelectField('Roof Sheeting', choices=[
        ('1/2" OSB', '1/2" OSB'), ('7/16" OSB', '7/16" OSB'), ('5/8" OSB', '5/8" OSB'), ('Zip Panels', 'Zip Panels')
    ], validators=[DataRequired()])
    framing_notes = TextAreaField('Framing Notes', validators=[Optional()])

class SidingForm(BaseForm):
    lap_type = SelectField('Lap Type', choices=[
        ('', 'Lap Type'), ('LP', 'LP'), ('Hardie', 'Hardie'), ('100% LP', '100% LP'), ('100% Hardie', '100% Hardie'),
        ('N/a - other', 'N/a - other')
    ], validators=[DataRequired()])
    panel_type = SelectField('Panel Type', choices=[
        ('', 'Panel Type'), ('LP', 'LP'), ('Hardie', 'Hardie'), ('N/a - other', 'N/a - other')
    ], validators=[DataRequired()])
    shake_type = SelectField('Shake Type', choices=[
        ('', 'Shake Type'), ('LP', 'LP'), ('Hardie', 'Hardie'), ('N/a - other', 'N/a - other')
    ], validators=[DataRequired()])
    soffit_trim = SelectField('Soffit/Trim', choices=[
        ('', 'Soffit/Trim Type'), ('LP', 'LP'), ('Hardie', 'Hardie'), ('Rollex', 'Rollex'), ('N/a - other', 'N/a - other')
    ], validators=[DataRequired()])
    window_trim_detail = SelectField('Window Trim Detail', choices=[
        ('Per Plan', 'Per Plan'), ('Front Only', 'Front Only'), ('All Sides', 'All Sides'), ('No Window Trim', 'No Window Trim')
    ], validators=[DataRequired()])
    siding_notes = TextAreaField('Siding Notes', validators=[Optional()])

class ShingleForm(BaseForm):
    shingle_notes = TextAreaField('Shingle Notes', validators=[DataRequired()])

class DoorForm(BaseForm):
    door_notes = TextAreaField('Door Notes', validators=[DataRequired()])

class WindowForm(BaseForm):
    window_notes = TextAreaField('Window Notes', validators=[DataRequired()])

class TrimForm(BaseForm):
    base = SelectField('Base', choices=[
        ('MDF 1x6', 'MDF 1×6'), ('MDF 1x8', 'MDF 1×8'), ('MDF 1x4', 'MDF 1×4'),
        ('MDF 421', 'MDF 421 (3-1/4")'), ('MDF 430', 'MDF 430 (1/2x4.25")'),
        ('MDF 432', 'MDF 432 (1/2x3.5")'), ('MDF 473', 'MDF 473 (2-1/4")'),
        ('MDF 512', 'MDF 512 (1/2x5.5")'), ('Claycoat 356J', 'Claycoat 356J (2-1/4")'),
        ('Claycoat 444J', 'Claycoat 444J (3-1/4")'), ('Poplar Miss', 'Poplar Miss 3-1/4"'),
        ('Poplar BIG Mission', 'Poplar BIG Mission 5-1/4"'), ('Poplar Colonial Base 2-5/8"', 'Poplar Colonial Base 2-5/8"'),
        ('Poplar Colonial Base 4-1/4"', 'Poplar Colonial Base 4-1/4"'), ('Poplar Colonial Base 5-1/4"', 'Poplar Colonial Base 5-1/4"'),
        ('Maple Mission', 'Maple Mission 3-1/4"'), ('Oak Mission', 'Oak Mission 3-1/4"')
    ], validators=[DataRequired()])
    case = SelectField('Case', choices=[
        ('MDF 1x4', 'MDF 1×4'), ('MDF 1x6', 'MDF 1×6'), ('MDF 1x8', 'MDF 1×8'),
        ('MDF 421', 'MDF 421 (3-1/4")'), ('MDF 430', 'MDF 430 (1/2x4.25")'),
        ('MDF 432', 'MDF 432 (1/2x3.5")'), ('MDF 473', 'MDF 473 (2-1/4")'),
        ('MDF 512', 'MDF 512 (1/2x5.5")'), ('Claycoat 356J', 'Claycoat 356J (2-1/4")'),
        ('Claycoat 444J', 'Claycoat 444J (3-1/4")'), ('Poplar Miss', 'Poplar Miss 7/16 x 3-1/4"'),
        ('Poplar BIG Miss', 'Poplar BIG Miss 9/16 x 3-1/4"'), ('Poplar Colonial F115', 'Poplar Colonial F115 2-1/4"'),
        ('Poplar Colonial F134', 'Poplar Colonial F134 3-1/4"'), ('Maple Mission', 'Maple Mission 3-1/4"'),
        ('Oak Mission', 'Oak Mission 3-1/4"')
    ], validators=[DataRequired()])
    stair_material = SelectField('Stair Material', choices=[
        ('Poplar', 'Poplar'), ('Primed', 'Primed'), ('Maple', 'Maple'), ('Oak', 'Oak')
    ], validators=[DataRequired()])
    door_material_type = SelectField('Door Material/Type', choices=[
        ('Molded - H/C', 'Molded - H/C'), ('Molded - S/C', 'Molded - S/C'), ('Poplar', 'Poplar'),
        ('Maple', 'Maple'), ('Oak', 'Oak'), ('N/A', 'N/A')
    ], validators=[DataRequired()])
    number_of_panels = StringField('# of Panels', validators=[DataRequired()])
    door_hardware = SelectField('Door Hardware', choices=[
        ('Schlage', 'Schlage'), ('Dexter', 'Dexter')
    ], validators=[DataRequired()])
    built_in_materials_type = SelectField('Built-in Materials Type', choices=[
        ('Poplar', 'Poplar'), ('Birch', 'Birch'), ('Maple', 'Maple'), ('Oak', 'Oak'), ('N/A', 'N/A')
    ], validators=[DataRequired()])
    plywood_1x_count = SelectField('Plywood/1x Count', choices=[
        ('Small (3-5 pcs)', 'Small (3-5 pcs)'), ('Medium (5-8 pcs)', 'Medium (5-8 pcs)'),
        ('Large (10-12 pcs)', 'Large (10-12 pcs)'), ('Other', 'Other')
    ], validators=[Optional()])
    specify_count = StringField('Please specify a count', validators=[DataRequired()])
    trim_allowance = StringField('Trim Allowance', validators=[Optional()])
    trim_notes = TextAreaField('Trim Notes', validators=[Optional()])

class DeckForm(BaseForm):
    decking_type = SelectField('Decking Type', choices=[
        ('Treated', 'Treated'), ('Composite - Stock', 'Composite - Stock'), ('Composite - Midgrade', 'Composite - Midgrade'),
        ('Composite - High End', 'Composite - High End'), ('Cedar', 'Cedar')
    ], validators=[DataRequired()])
    railing_type = SelectField('Railing Type', choices=[
        ('Treated', 'Treated'), ('Treated w/Facemount', 'Treated w/Facemount'), ('Cedar', 'Cedar'),
        ('Cedar w/Facemount', 'Cedar w/Facemount'), ('Westbury - Black', 'Westbury - Black'),
        ('Westbury - Dark Bronze', 'Westbury - Dark Bronze'), ('Westbury - Gloss White', 'Westbury - Gloss White')
    ], validators=[DataRequired()])
    stairs = SelectField('Stairs', choices=[
        ('None', 'None'), ('Yes', 'Yes'), ('N/a', 'N/a')
    ], validators=[DataRequired()])
    deck_notes = TextAreaField('Deck Notes', validators=[Optional()])

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

