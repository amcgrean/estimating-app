from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app, jsonify, abort
from flask_login import login_user, login_required, logout_user, current_user
from project import mail, db
from project.models import (
    Bid, Customer, Estimator, Design, User, EWP, UserType, UserSecurity,
    Branch, SalesRep, LoginActivity, ITService, Project, Framing, Siding,
    Shingle, Deck, Door, Window, Trim, BidActivity
)
import csv
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta,date
import io
import calendar
import chardet
from sqlalchemy import func, cast, Date
from flask_mail import Message
from werkzeug.security import generate_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, RadioField, SelectField, HiddenField
from wtforms.validators import DataRequired
from project.forms import (BidRequestForm, UpdateUserForm, LoginForm, RegistrationForm, FramingForm, SidingForm, ShingleForm,
                    DoorForm, WindowForm, TrimForm, DeckForm, UserForm, UserTypeForm, DesignForm, LayoutForm, BidForm,
                    UploadForm, CustomerForm, SearchForm, UserSecurityForm, UserSettingsForm,ITServiceForm)
try:
    from PyPDF2 import PdfFileReader, PdfFileWriter  # For older versions
except ImportError:
    from PyPDF2 import PdfReader as PdfFileReader  # For newer versions
    from PyPDF2 import PdfWriter as PdfFileWriter
from reportlab.pdfgen import canvas
from project.decorators import login_required_for_blueprint 
import string
import random
from io import StringIO
import logging
from project.utils import safe_str_cmp  # Import the custom function
from flask_session import Session  # Import the Session object from Flask-Session

# Create a Blueprint named 'main'
main = Blueprint('main', __name__)

@main.route('/')
@login_required
def index():
    logging.info('Checking authentication for route: main.index')
    logging.info(f'User authenticated: {current_user.is_authenticated}')

    current_year = datetime.now().year
    previous_year = current_year - 1
    this_month = datetime.now().month
    _, last_day_of_month = calendar.monthrange(previous_year, this_month)

    start_date = datetime(previous_year, this_month, 1)
    end_date = datetime(previous_year, this_month, last_day_of_month)


    # Branch filtering logic - default to user's branch
    branch_id = request.args.get('branch_id', current_user.user_branch_id, type=int)
    # If branch_id is 0 or 'all', we might show all, but per user request, we default to their branch.
    
    def apply_branch_filter(query, model):
        if branch_id and branch_id != 0:
            return query.filter(model.branch_id == branch_id)
        return query

    # Open bids count (incomplete)
    open_bids_count = apply_branch_filter(Bid.query, Bid).filter(Bid.status == 'Incomplete').count()

    # Bids YTD
    bids_ytd = apply_branch_filter(Bid.query, Bid).filter(Bid.log_date >= datetime(current_year, 1, 1)).count()
    bids_mtd = apply_branch_filter(Bid.query, Bid).filter(Bid.log_date >= datetime(current_year, datetime.now().month, 1)).count()

    # Previous YTD bids
    prev_bids_ytd = apply_branch_filter(Bid.query, Bid).filter(Bid.log_date.between(datetime(previous_year, 1, 1), datetime(previous_year, 12, 31))).count()
    prev_bids_mtd = apply_branch_filter(Bid.query, Bid).filter(Bid.log_date.between(start_date, end_date)).count()

    # Average completion time (in days)
    try:
        # SQLite
        avg_completion_time = db.session.query(func.avg(func.julianday(Bid.completion_date) - func.julianday(Bid.log_date))).filter(Bid.status == 'Complete')
        avg_completion_time = apply_branch_filter(avg_completion_time, Bid).scalar() or 0
    except Exception:
        db.session.rollback()
        # Postgres/Generic
        avg_completion_time = db.session.query(func.avg(func.extract('epoch', Bid.completion_date - Bid.log_date))).filter(Bid.status == 'Complete')
        avg_completion_time = apply_branch_filter(avg_completion_time, Bid).scalar() or 0
        avg_completion_time = avg_completion_time / 86400 
    
    avg_completion_time = round(avg_completion_time)

    # Open designs count (active)
    open_designs_count = apply_branch_filter(Design.query, Design).filter(Design.status == 'Active').count()

    # Designs YTD
    designs_ytd = apply_branch_filter(Design.query, Design).filter(Design.log_date >= datetime(current_year, 1, 1)).count()
    designs_mtd = apply_branch_filter(Design.query, Design).filter(Design.log_date >= datetime(current_year, datetime.now().month, 1)).count()

    # Previous YTD designs
    prev_designs_ytd = apply_branch_filter(Design.query, Design).filter(Design.log_date.between(datetime(previous_year, 1, 1), datetime(previous_year, 12, 31))).count()
    prev_designs_mtd = apply_branch_filter(Design.query, Design).filter(Design.log_date.between(start_date, end_date)).count()

    # Recently opened projects (using BidActivity)
    # Get distinct bid_ids first to avoid duplicates
    recent_activities = db.session.query(BidActivity.bid_id, func.max(BidActivity.timestamp).label('max_time')) \
        .filter(BidActivity.user_id == current_user.id, BidActivity.action == 'viewed') \
        .group_by(BidActivity.bid_id) \
        .order_by(func.max(BidActivity.timestamp).desc()) \
        .limit(5) \
        .all()
    
    recent_bid_ids = [r.bid_id for r in recent_activities]
    
    recently_opened_projects = []
    if recent_bid_ids:
        # Preserve order and apply branch filter
        query = Bid.query.filter(Bid.id.in_(recent_bid_ids))
        if branch_id and branch_id != 0:
            query = query.filter(Bid.branch_id == branch_id)
        
        projects_dict = {b.id: b for b in query.all()}
        recently_opened_projects = [projects_dict[bid_id] for bid_id in recent_bid_ids if bid_id in projects_dict]

    # Recently created projects
    recently_created_projects = apply_branch_filter(db.session.query(Bid), Bid).order_by(Bid.log_date.desc()).limit(5).all()

    search_query = request.args.get('search')
    bids = []
    designs = []
    if search_query:
        bids = apply_branch_filter(Bid.query, Bid).join(Customer).filter(
            (Bid.project_name.ilike(f'%{search_query}%')) |
            (Customer.name.ilike(f'%{search_query}%'))
        ).all()

        designs = apply_branch_filter(Design.query, Design).join(Customer).filter(
            (Design.plan_name.ilike(f'%{search_query}%')) |
            (Customer.name.ilike(f'%{search_query}%'))
        ).all()

    branches = Branch.query.all()

    return render_template(
        'index.html',
        open_bids_count=open_bids_count,
        bids_ytd=bids_ytd,
        bids_mtd=bids_mtd,
        prev_bids_ytd=prev_bids_ytd,
        prev_bids_mtd=prev_bids_mtd,
        avg_completion_time=avg_completion_time,
        open_designs_count=open_designs_count,
        designs_ytd=designs_ytd,
        designs_mtd=designs_mtd,
        prev_designs_ytd=prev_designs_ytd,
        prev_designs_mtd=prev_designs_mtd,
        search_query=search_query,
        bids=bids,
        designs=designs,
        current_year=current_year,
        previous_year=previous_year,
        recently_opened_projects=recently_opened_projects,
        recently_created_projects=recently_created_projects,
        branches=branches,
        current_branch_id=branch_id
    )

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)




@main.route('/customer/<int:customer_id>/bids', methods=['GET'])
def view_customer_bids(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)

        # Get the sort column from the query parameters, default to 'plan_type'
        sort_column = request.args.get('sort', 'plan_type')
        # Get the sort direction from the query parameters, default to 'asc'
        sort_direction = request.args.get('direction', 'asc')

        # Validate the sort direction
        if sort_direction not in ['asc', 'desc']:
            sort_direction = 'asc'

        # Define a mapping of column names to SQLAlchemy columns for bids
        column_map_bids = {
            'plan_type': Bid.plan_type,
            'project_name': Bid.project_name,
            'estimator': Estimator.estimatorName,
            'status': Bid.status,
            'log_date': Bid.log_date,
            'due_date': Bid.due_date,
            'notes': Bid.notes
        }

        # Define a mapping of column names to SQLAlchemy columns for designs
        column_map_designs = {
            'planNumber': Design.planNumber,
            'plan_name': Design.plan_name,
            'project_address': Design.project_address,
            'designer': Estimator.estimatorName,
            'status': Design.status,
            'log_date': Design.log_date,
            'notes': Design.notes
        }

        # Define a mapping of column names to SQLAlchemy columns for layouts
        column_map_layouts = {
            'plan_number': EWP.plan_number,
            'sales_rep': User.username,
            'customer': Customer.name,
            'address': EWP.address,
            'notes': EWP.notes,
            'login_date': EWP.login_date,
            'tji_depth': EWP.tji_depth,
            'assigned_designer': EWP.assigned_designer,
            'layout_finalized': EWP.layout_finalized,
            'agility_quote': EWP.agility_quote,
            'imported_stellar': EWP.imported_stellar
        }

        # Get the column to sort by for bids, default to plan_type
        sort_column_attr_bids = column_map_bids.get(sort_column, Bid.plan_type)
        # Get the column to sort by for designs, default to planNumber
        sort_column_attr_designs = column_map_designs.get(sort_column, Design.planNumber)
        # Get the column to sort by for layouts, default to plan_number
        sort_column_attr_layouts = column_map_layouts.get(sort_column, EWP.plan_number)

        # Apply sorting direction
        if sort_direction == 'desc':
            sort_column_attr_bids = sort_column_attr_bids.desc()
            sort_column_attr_designs = sort_column_attr_designs.desc()
            sort_column_attr_layouts = sort_column_attr_layouts.desc()

        # Get the date filters from the query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # Set default date range to the current year
        if not start_date:
            start_date = datetime(datetime.now().year, 1, 1)
        else:
            start_date = datetime.strptime(start_date, '%m/%d/%Y')

        if not end_date:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(end_date, '%m/%d/%Y')

        # Base query for bids
        bids_query = db.session.query(Bid).join(Customer).join(Estimator, isouter=True).filter(Bid.customer_id == customer_id)

        # Apply date filters to bids
        bids_query = bids_query.filter(Bid.log_date >= start_date, Bid.log_date <= end_date)

        # Apply sorting to bids
        bids = bids_query.order_by(sort_column_attr_bids).all()

        # Base query for designs
        designs_query = db.session.query(Design).join(Customer).join(Estimator, isouter=True).filter(Design.customer_id == customer_id)

        # Apply date filters to designs
        designs_query = designs_query.filter(Design.log_date >= start_date, Design.log_date <= end_date)

        # Apply sorting to designs
        designs = designs_query.order_by(sort_column_attr_designs).all()

        # Base query for layouts
        layouts_query = db.session.query(EWP).join(Customer).join(User, isouter=True).filter(EWP.customer_id == customer_id)

        # Apply date filters to layouts
        layouts_query = layouts_query.filter(EWP.login_date >= start_date, EWP.login_date <= end_date)

        # Apply sorting to layouts
        layouts = layouts_query.order_by(sort_column_attr_layouts).all()

        # KPIs
        total_bids = db.session.query(Bid).filter(Bid.customer_id == customer_id).count()
        bids_ytd = db.session.query(Bid).filter(Bid.customer_id == customer_id, Bid.log_date >= datetime(datetime.now().year, 1, 1)).count()
        completed_bids_ytd = db.session.query(Bid).filter(Bid.customer_id == customer_id, Bid.status == 'Complete', Bid.log_date >= datetime(datetime.now().year, 1, 1)).count()

        total_designs = db.session.query(Design).filter(Design.customer_id == customer_id).count()
        designs_ytd = db.session.query(Design).filter(Design.customer_id == customer_id, Design.log_date >= datetime(datetime.now().year, 1, 1)).count()
        completed_designs_ytd = db.session.query(Design).filter(Design.customer_id == customer_id, Design.status == 'Complete', Design.log_date >= datetime(datetime.now().year, 1, 1)).count()

        return render_template(
            'view_customer_bids.html',
            customer=customer,
            bids=bids,
            designs=designs,
            layouts=layouts,
            total_bids=total_bids,
            bids_ytd=bids_ytd,
            completed_bids_ytd=completed_bids_ytd,
            total_designs=total_designs,
            designs_ytd=designs_ytd,
            completed_designs_ytd=completed_designs_ytd,
            sort_column=sort_column,
            sort_direction=sort_direction,
            start_date=start_date.strftime('%m/%d/%Y'),
            end_date=end_date.strftime('%m/%d/%Y')
        )
    except Exception as e:
        # Log the error
        current_app.logger.error(f"Error occurred while fetching customer bids: {e}")
        return "An error occurred while fetching customer bids.", 500


#########bid request#################

def get_form_fields(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        reader = PdfFileReader(pdf_file)
        fields = reader.getFields()
        return fields

def create_form_class(fields):
    class DynamicForm(FlaskForm):
        pass

    for field_name, field_data in fields.items():
        field_type = field_data.get('/FT')
        field_title = field_data.get('/T', '')
        field_value = field_data.get('/V', '')

        if field_type == '/Tx':  # Text field
            setattr(DynamicForm, field_name, StringField(field_title, validators=[DataRequired()]))
        elif field_type == '/Btn':  # Button field (can be checkbox or radio button)
            if field_data.get('/Ff') is not None and field_data.get('/Ff') & 65536:  # Checkbox
                setattr(DynamicForm, field_name, BooleanField(field_title))
            else:  # Radio button
                radio_options = [("Option1", "Option 1"), ("Option2", "Option 2")]  # Placeholder options
                setattr(DynamicForm, field_name, RadioField(field_title, choices=radio_options))
        elif field_type == '/Ch':  # Choice field (dropdown)
            options = field_data.get('/Opt', [])
            dropdown_options = [(option, option) if isinstance(option, str) else (option[0], option[0]) for option in options]
            setattr(DynamicForm, field_name, SelectField(field_title, choices=dropdown_options))

    setattr(DynamicForm, 'submit', SubmitField('Submit'))
    return DynamicForm

def fill_pdf(pdf_path, output_path, data):
    reader = PdfFileReader(pdf_path)
    writer = PdfFileWriter()

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=reader.getPage(0).mediaBox)

    for field_name, value in data.items():
        x, y = 100, 750 - 20 * list(data.keys()).index(field_name)  # Adjust coordinates as needed
        can.drawString(x, y, f'{field_name}: {value}')

    can.save()
    packet.seek(0)
    new_pdf = PdfFileReader(packet)

    for i in range(reader.getNumPages()):
        page = reader.getPage(i)
        if i < new_pdf.getNumPages():
            page.mergePage(new_pdf.getPage(i))
        writer.addPage(page)

    with open(output_path, 'wb') as output_pdf:
        writer.write(output_pdf)


#####user mgmt#########

#####Admin & User mgmt##########


# Update the manage_users route



@main.route('/get_roles')
def get_roles():
    role_type = request.args.get('type')
    roles = Estimator.query.filter_by(type=role_type).all()
    return jsonify([{'id': role.estimatorID, 'name': role.estimatorName} for role in roles])

@main.route('/get_estimators')
def get_estimators():
    estimator_type = request.args.get('type', type=int)
    estimators = Estimator.query.filter_by(type=estimator_type).all()
    estimator_list = [{'estimatorID': e.estimatorID, 'name': e.estimatorName} for e in estimators]
    return jsonify(estimator_list)

def get_branch_estimators(branch_id, estimator_type=None):
    """Helper to get estimators for a specific branch, optionally filtered by type."""
    query = db.session.query(Estimator).join(
        User, User.username == Estimator.estimatorUsername
    ).filter(User.is_active == True)

    if branch_id and branch_id != 0:
        query = query.filter(User.user_branch_id == branch_id)
    
    if estimator_type:
        query = query.filter(Estimator.type == estimator_type)

    estimators = query.all()
    
    return [(0, 'No Estimator')] + [(e.estimatorID, e.estimatorName) for e in estimators]

def get_branch_sales_reps(branch_id):
    """Helper to get sales reps for a specific branch."""
    query = db.session.query(SalesRep).join(
        User, User.sales_rep_id == SalesRep.id
    ).filter(User.is_active == True)

    if branch_id and branch_id != 0:
        query = query.filter(User.user_branch_id == branch_id)
    
    reps = query.all()
    return [('', 'Select Sales Rep')] + [(rep.id, rep.name) for rep in reps]


# Route to manage user types



#################### EWP #########################################
from project.forms import FilterForm

@main.route('/layouts', methods=['GET'])
def view_layouts():
    form = FilterForm(request.args)

    # Get filters from the form data
    sales_rep = form.sales_rep.data if form.sales_rep.data else ''
    customer = form.customer.data if form.customer.data else ''
    login_date = form.login_date.data if form.login_date.data else ''
    layout_date = form.layout_date.data if form.layout_date.data else ''

    # Get sorting parameters
    sort_column = request.args.get('sort', 'login_date')
    sort_direction = request.args.get('direction', 'asc')

    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    # Define a mapping of column names to SQLAlchemy columns
    column_map = {
        'plan_number': EWP.plan_number,
        'sales_rep': User.username,
        'customer': Customer.name,
        'address': EWP.address,
        'login_date': EWP.login_date,
        'layout_finalized': EWP.layout_finalized,
    }

    # Get the column to sort by, default to login_date
    sort_column_attr = column_map.get(sort_column, EWP.login_date)

    # Apply sorting direction
    if sort_direction == 'desc':
        sort_column_attr = sort_column_attr.desc()

    # Build query with filters
    query = EWP.query.join(Customer).join(User, isouter=True)

    # Branch filtering
    branch_id = request.args.get('branch_id', current_user.user_branch_id, type=int)
    if branch_id and branch_id != 0:
        query = query.filter(EWP.branch_id == branch_id)

    if sales_rep:
        query = query.filter(User.username.ilike(f"%{sales_rep}%"))
    if customer:
        query = query.filter((Customer.name.ilike(f"%{customer}%")) | (EWP.address.ilike(f"%{customer}%")))
    if login_date:
        try:
            query = query.filter(EWP.login_date == login_date)
        except ValueError:
            pass  # Handle invalid date format if needed
    if layout_date:
        try:
            query = query.filter(EWP.layout_finalized == layout_date)
        except ValueError:
            pass  # Handle invalid date format if needed

    # Apply sorting
    query = query.order_by(sort_column_attr)

    # Paginate the results
    pagination = query.paginate(page=page, per_page=per_page)
    layouts = pagination.items

    branches = Branch.query.all()
    return render_template(
        'layouts.html',
        layouts=layouts,
        form=form,
        pagination=pagination,
        sort_column=sort_column,
        sort_direction=sort_direction,
        branches=branches,
        current_branch_id=branch_id
    )


@main.route('/create_layout', methods=['GET', 'POST'])
def create_layout():
    form = LayoutForm()

    # Determine the branch_id for populating choices
    selected_branch_id = form.branch_id.data or request.args.get('branch_id', current_user.user_branch_id, type=int)

    # Populate the sales reps and customers
    form.sales_rep_id.choices = get_branch_sales_reps(selected_branch_id)
    
    customer_query = Customer.query
    if selected_branch_id and selected_branch_id != 0:
        customer_query = customer_query.filter((Customer.branch_id == selected_branch_id) | (Customer.branch_id == None))
    form.customer_id.choices = [(customer.id, customer.name) for customer in customer_query.all()]
    
    form.branch_id.choices = [(b.branch_id, b.branch_name) for b in Branch.query.all()]
    if not form.branch_id.data:
        form.branch_id.data = selected_branch_id

    if form.validate_on_submit():
        new_ewp = EWP(
            plan_number=form.plan_number.data,
            sales_rep_id=form.sales_rep_id.data,
            customer_id=form.customer_id.data,
            address=form.address.data,
            notes=form.notes.data,
            login_date=form.login_date.data,
            tji_depth=form.tji_depth.data,
            assigned_designer=form.assigned_designer.data,
            layout_finalized=form.layout_finalized.data,
            agility_quote=form.agility_quote.data,
            imported_stellar=form.imported_stellar.data,
            branch_id=form.branch_id.data
        )

        form.save_instance(new_ewp)  # This will save the instance and log the activity
        flash('New layout entry created successfully!')
        return redirect(url_for('main.view_layouts'))

    return render_template('create_layout.html', form=form)

@main.route('/edit_layout/<int:layout_id>', methods=['GET', 'POST'])
def edit_layout(layout_id):
    layout = EWP.query.get_or_404(layout_id)
    form = LayoutForm(obj=layout)

    # Populate the sales reps and customers
    form.sales_rep_id.choices = [(rep.id, rep.username) for rep in User.query.join(UserType).filter(UserType.name == 'Sales Rep').all()]
    form.customer_id.choices = [(customer.id, customer.name) for customer in Customer.query.all()]

    if form.validate_on_submit():
        form.save_instance(layout)
        flash('Layout updated successfully!', 'success')
        return redirect(url_for('main.view_layouts'))

    return render_template('edit_layout.html', form=form, layout=layout)

@main.route('/upload_ewp_layouts', methods=['GET', 'POST'])
def upload_ewp_layouts():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            raw_data = file.read().decode('utf-8')
            csv_reader = csv.reader(io.StringIO(raw_data), delimiter=',')
            next(csv_reader)  # Skip header row

            batch_size = 100  # Adjust this number based on your testing
            batch = []
            default_customer_id = 770  # Default customer ID for unknown customers

            for row in csv_reader:
                plan_number, sales_rep_name, customer_name, address, notes, login_date, tji_depth, assigned_designer, layout_finalized, agility_quote, imported_stellar = row

                customer = Customer.query.filter_by(name=customer_name).first()
                if not customer:
                    customer_id = default_customer_id
                else:
                    customer_id = customer.id

                sales_rep = User.query.filter_by(username=sales_rep_name).first()

                new_ewp = EWP(
                    plan_number=plan_number,
                    sales_rep_id=sales_rep.id if sales_rep else None,  # Use the id from the User table
                    customer_id=customer_id,
                    address=address,
                    notes=notes,
                    login_date=datetime.strptime(login_date, '%m/%d/%Y').date() if login_date else None,
                    tji_depth=tji_depth,
                    assigned_designer=assigned_designer,
                    layout_finalized=datetime.strptime(layout_finalized, '%m/%d/%Y').date() if layout_finalized else None,
                    agility_quote=datetime.strptime(agility_quote, '%m/%d/%Y').date() if agility_quote else None,
                    imported_stellar=datetime.strptime(imported_stellar, '%m/%d/%Y').date() if imported_stellar else None
                )

                batch.append(new_ewp)

                if len(batch) >= batch_size:
                    db.session.bulk_save_objects(batch)
                    db.session.commit()
                    batch = []

            # Commit any remaining objects in the last batch
            if batch:
                db.session.bulk_save_objects(batch)
                db.session.commit()

            flash('Historical EWP layouts uploaded successfully!')
            return redirect(url_for('main.index'))

    return render_template('upload_ewp_layouts.html')



@main.route('/submit_issue', methods=['GET', 'POST'])
@login_required
def submit_issue():
    form = ITServiceForm()
    if form.validate_on_submit():
        new_issue = ITService(
            issue_type=form.issue_type.data,
            createdby=current_user.username,  # Auto-fill the "Created By" field with the current user's name
            description=form.description.data,
            status=form.status.data,
            notes=form.notes.data
        )
        db.session.add(new_issue)
        db.session.commit()
        flash('Issue submitted successfully!', 'success')
        return redirect(url_for('main.view_issues'))
    return render_template('submit_issue.html', form=form)

@main.route('/update_issue/<int:issue_id>', methods=['GET', 'POST'])
@login_required
def update_issue(issue_id):
    issue = ITService.query.get_or_404(issue_id)
    form = ITServiceForm(obj=issue)
    if form.validate_on_submit():
        issue.status = form.status.data
        issue.updatedby = current_user.username  # Automatically update the "Updated By" field with the current user's name
        issue.notes = form.notes.data
        db.session.commit()
        flash('Issue updated successfully!', 'success')
        return redirect(url_for('main.view_issues'))
    return render_template('update_issue.html', form=form, issue=issue)

@main.route('/view_issues')
def view_issues():
    issues = ITService.query.order_by(ITService.createdDate.desc()).all()  # Fetch all issues, ordered by created date
    return render_template('view_issues.html', issues=issues)

@main.route('/delete_issue/<int:issue_id>', methods=['POST'])
@login_required
def delete_issue(issue_id):
    issue = ITService.query.get_or_404(issue_id)  # Get the issue by ID or return 404 if not found

    # Restrict deletion to user with userid = 2
    if current_user.id != 2:  # Assuming you're using Flask-Login and current_user contains the logged-in user
        abort(403)  # Return a 403 Forbidden error if the user is not allowed to delete

    db.session.delete(issue)  # Delete the issue
    db.session.commit()  # Commit the deletion to the database
    flash('Issue deleted successfully!', 'success')
    return redirect(url_for('main.view_issues'))  # Redirect back to the issues list

@main.errorhandler(403)
def forbidden(e):
    flash("You do not have permission to delete this issue.", "danger")
    return redirect(url_for('main.view_issues'))




@main.route('/add_bid', methods=['GET', 'POST'])
def add_bid():
    form = BidForm()

    # Determine the branch_id for populating choices
    selected_branch_id = form.branch_id.data or request.args.get('branch_id', current_user.user_branch_id, type=int)

    # Populate Customer choices based on branch
    customer_query = Customer.query
    if selected_branch_id and selected_branch_id != 0:
        customer_query = customer_query.filter((Customer.branch_id == selected_branch_id) | (Customer.branch_id == None))
    
    form.customer_id.choices = [(0, 'Select a customer')] + [(customer.id, customer.name) for customer in customer_query.all()]
    form.estimator_id.choices = get_branch_estimators(selected_branch_id)
    form.branch_id.choices = [(b.branch_id, b.branch_name) for b in Branch.query.all()]
    
    if not form.branch_id.data:
        form.branch_id.data = selected_branch_id

    # Set default value for due_date to 14 days from today
    if not form.due_date.data:
        form.due_date.data = (datetime.utcnow() + timedelta(days=14)).date()

    if form.validate_on_submit():
        plan_type = form.plan_type.data
        customer_id = form.customer_id.data if form.customer_id.data != 0 else None
        project_name = form.project_name.data
        estimator_id = form.estimator_id.data if form.estimator_id.data != 0 else None
        status = form.status.data
        due_date = form.due_date.data
        notes = form.notes.data

        # Update last_updated_by and last_updated_at
        last_updated_by = current_user.username
        last_updated_at = datetime.utcnow()

        new_bid = Bid(
            plan_type=plan_type,
            customer_id=customer_id,
            project_name=project_name,
            estimator_id=estimator_id,
            status=status,
            due_date=due_date,
            notes=notes,
            last_updated_by=last_updated_by,
            last_updated_at=last_updated_at,
            branch_id=form.branch_id.data
        )
        db.session.add(new_bid)
        try:
            db.session.commit()
            flash('Bid added successfully!', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
            return redirect(url_for('main.add_bid'))

    return render_template('add_bid.html', form=form)

@main.route('/manage_bid/<int:bid_id>', methods=['GET', 'POST'])
def manage_bid(bid_id):
    bid = Bid.query.get_or_404(bid_id)

    # Log view activity
    try:
        activity = BidActivity(
            user_id=current_user.id,
            bid_id=bid.id,
            action='viewed',
            timestamp=datetime.utcnow()
        )
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # Fail silently for logging to avoid breaking the user experience
        print(f"Error logging bid view: {e}")

    form = BidForm(obj=bid)

    # Populate customer and estimator choices with a branch filter
    customer_query = Customer.query
    if bid.branch_id:
        customer_query = customer_query.filter((Customer.branch_id == bid.branch_id) | (Customer.branch_id == None))
    
    form.customer_id.choices = [(customer.id, customer.name) for customer in customer_query.all()]
    form.estimator_id.choices = get_branch_estimators(bid.branch_id)
    form.branch_id.choices = [(b.branch_id, b.branch_name) for b in Branch.query.all()]

    if form.validate_on_submit():
        if current_user.usertype.name == 'Sales Rep':
            flash('Sales Reps do not have permission to update bids.', 'danger')
            return redirect(url_for('main.manage_bid', bid_id=bid.id))

        form.populate_obj(bid)
        db.session.commit()
        flash('Bid updated successfully!', 'success')
        return redirect(url_for('main.open_bids'))
    return render_template('manage_bid.html', bid=bid, form=form)

@main.route('/delete_bid/<int:bid_id>', methods=['POST'])
def delete_bid(bid_id):
    try:
        bid = Bid.query.get_or_404(bid_id)
        db.session.delete(bid)
        db.session.commit()
        flash('Bid deleted successfully!')
        return redirect(url_for('main.index'))
    except Exception as e:
        flash('Error deleting bid: {}'.format(e))
        return redirect(url_for('main.index'))

@main.route('/update_bid/<int:bid_id>', methods=['POST'])
def update_bid(bid_id):
    bid = Bid.query.get_or_404(bid_id)
    bid.plan_type = request.form['plan_type']
    bid.customer_id = request.form['customer_id']
    bid.project_name = request.form['project_name']
    bid.estimator_id = request.form['estimator_id'] if request.form['estimator_id'] else None
    bid.status = request.form['status']
    bid.due_date = datetime.strptime(request.form['due_date'], '%Y-%m-%d')
    db.session.commit()
    flash('Bid updated successfully!')
    return redirect(url_for('main.index'))

@main.route('/view_bids')
def view_bids():
    bids = Bid.query.all()
    return render_template('view_bids.html', bids=bids)

@main.route('/open_bids', methods=['GET'])
@login_required
def open_bids():
    # Get the sort column from the query parameters, default to 'log_date'
    sort_column = request.args.get('sort', 'due_date')
    # Get the sort direction from the query parameters, default to 'asc'
    sort_direction = request.args.get('direction', 'asc')

    # Validate the sort direction
    if sort_direction not in ['asc', 'desc']:
        sort_direction = 'asc'

    # Get the plan type filter from the query parameters
    plan_type_filter = request.args.get('plan_type', 'all')

    # Get the status filter from the query parameters, default to 'Incomplete'
    status_filter = request.args.get('status', 'Incomplete')

    # Get date range filters from the query parameters
    due_date_start = request.args.get('due_date_start')  # No default value, will be None if not provided
    due_date_end = request.args.get('due_date_end')

    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    # Handle quick filters
    quick_filter = request.args.get('quick_filter', '')
    if quick_filter == 'residential':
        plan_type_filter = 'Residential'
        status_filter = 'Incomplete'
    elif quick_filter == 'commercial':
        plan_type_filter = 'Commercial'
        status_filter = 'Incomplete'

    # Define a mapping of column names to SQLAlchemy columns
    column_map = {
        'plan_type': Bid.plan_type,
        'customer_name': Customer.name,
        'project_name': Bid.project_name,
        'estimator': Estimator.estimatorName,
        'status': Bid.status,
        'log_date': Bid.log_date,
        'due_date': Bid.due_date,
        'notes': Bid.notes
    }

    # Get the column to sort by, default to log_date
    sort_column_attr = column_map.get(sort_column, Bid.log_date)

    # Apply sorting direction
    if sort_direction == 'desc':
        sort_column_attr = sort_column_attr.desc()

    # Base query for bids
    query = db.session.query(Bid).join(Customer).join(Estimator, isouter=True)

    # Branch filtering
    branch_id = request.args.get('branch_id', current_user.user_branch_id, type=int)
    if branch_id and branch_id != 0:
        query = query.filter(Bid.branch_id == branch_id)

    # Apply status filter
    if status_filter != 'all':
        query = query.filter(Bid.status == status_filter)

    # Apply plan type filter if provided
    if plan_type_filter != 'all':
        query = query.filter(Bid.plan_type == plan_type_filter)

    # Apply date range filters if provided
    if due_date_start:
        query = query.filter(Bid.due_date >= due_date_start)
    if due_date_end:
        query = query.filter(Bid.due_date <= due_date_end)

    # Apply sorting
    query = query.order_by(sort_column_attr)

    # Paginate the results
    pagination = query.paginate(page=page, per_page=per_page)
    open_bids = pagination.items

    # Group bids by plan type
    bids_by_plan_type = {}
    for bid in open_bids:
        if bid.plan_type not in bids_by_plan_type:
            bids_by_plan_type[bid.plan_type] = []
        bids_by_plan_type[bid.plan_type].append(bid)

    # Calculate total number of open bids by plan type
    total_bids_by_plan_type = {}
    for plan_type, bids in bids_by_plan_type.items():
        total_bids_by_plan_type[plan_type] = len(bids)

    # Fetch distinct plan types and statuses for the filter dropdowns
    plan_types = [pt[0] for pt in db.session.query(Bid.plan_type).distinct().all()]
    statuses = ['all', 'Incomplete']

    branches = Branch.query.all()
    now = datetime.now()
    return render_template('open_bids.html', bids_by_plan_type=bids_by_plan_type, sort_column=sort_column, sort_direction=sort_direction,
                           plan_types=plan_types, statuses=statuses, current_status=status_filter, current_plan_type=plan_type_filter,
                           due_date_start=due_date_start, due_date_end=due_date_end, pagination=pagination, total_bids_by_plan_type=total_bids_by_plan_type,
                           branches=branches, current_branch_id=branch_id, now=now)

@main.route('/print_open_bids')
@login_required
def print_open_bids():
    # Retrieve selected columns and filters from query parameters
    selected_columns = request.args.getlist('columns')
    plan_type = request.args.get('plan_type', 'all')
    status = request.args.get('status', 'Incomplete')

    # Filter bids based on the status and plan type
    query = Bid.query.filter_by(status=status)

    if plan_type != 'all':
        query = query.filter_by(plan_type=plan_type)

    bids = query.all()
    current_date = datetime.now().strftime('%m/%d/%y')  # Format the current date as MM/DD/YY


    # Pass only selected columns and filtered bids to the template, plus current date
    return render_template('print_open_bids.html', bids=bids, selected_columns=selected_columns,current_date=current_date)

@main.route('/bids_calendar')
@login_required
def bids_calendar():
    branch_id = request.args.get('branch_id', current_user.user_branch_id, type=int)
    branches = Branch.query.all()
    return render_template('bids_calendar.html', branches=branches, current_branch_id=branch_id)

@main.route('/api/bids_events')
@login_required
def api_bids_events():
    branch_id = request.args.get('branch_id', type=int)
    
    query = Bid.query.filter(Bid.status == 'Incomplete')
    if branch_id and branch_id != 0:
        query = query.filter(Bid.branch_id == branch_id)
        
    bids = query.all()
    events = []
    
    for bid in bids:
        if bid.due_date:
            # Color coding based on Plan Type
            color = '#00008b' if bid.plan_type == 'Residential' else '#6c757d'
            
            events.append({
                'id': bid.id,
                'title': f"{bid.customer.name if bid.customer else 'Unassigned'} - {bid.project_name}",
                'start': bid.due_date.strftime('%Y-%m-%d'),
                'url': url_for('main.manage_bid', bid_id=bid.id),
                'backgroundColor': color,
                'borderColor': color,
                'textColor': '#ffffff',
                'extendedProps': {
                    'customer': bid.customer.name if bid.customer else 'N/A',
                    'project': bid.project_name,
                    'plan_type': bid.plan_type,
                    'estimator': bid.estimator.estimatorName if bid.estimator else 'Unassigned'
                }
            })
            
    return jsonify(events)

@main.route('/completed_bids', methods=['GET'])
@login_required
def completed_bids():
    sort_column = request.args.get('sort', 'due_date')
    sort_direction = request.args.get('direction', 'asc')
    plan_type_filter = request.args.get('plan_type', 'all')
    status_filter = request.args.get('status', 'Complete')  # default to 'Complete'

    due_date_start = request.args.get('due_date_start')
    due_date_end = request.args.get('due_date_end')

    quick_filter = request.args.get('quick_filter', '')

    if quick_filter == 'residential':
        plan_type_filter = 'Residential'
        status_filter = 'Complete'
    elif quick_filter == 'commercial':
        plan_type_filter = 'Commercial'
        status_filter = 'Complete'

    column_map = {
        'plan_type': Bid.plan_type,
        'customer_name': Customer.name,
        'project_name': Bid.project_name,
        'estimator': Estimator.estimatorName,
        'status': Bid.status,
        'log_date': Bid.log_date,
        'due_date': Bid.due_date,
        'notes': Bid.notes
    }

    sort_column_attr = column_map.get(sort_column, Bid.due_date)
    if sort_direction == 'desc':
        sort_column_attr = sort_column_attr.desc()

    # Base query for bids
    query = db.session.query(Bid).join(Customer).join(Estimator, isouter=True)

    # Branch filtering
    branch_id = request.args.get('branch_id', current_user.user_branch_id, type=int)
    if branch_id and branch_id != 0:
        query = query.filter(Bid.branch_id == branch_id)

    if status_filter != 'all':
        query = query.filter(Bid.status == status_filter)

    if plan_type_filter != 'all':
        query = query.filter(Bid.plan_type == plan_type_filter)

    if not due_date_start and not due_date_end:
        from datetime import date
        current_year = date.today().year
        query = query.filter(db.extract('year', Bid.due_date) == current_year)

    if due_date_start:
        query = query.filter(Bid.due_date >= due_date_start)
    if due_date_end:
        query = query.filter(Bid.due_date <= due_date_end)

    query = query.order_by(sort_column_attr)

    all_bids = query.all()  # No pagination, fetch all

    bids_by_plan_type = {}
    for bid in all_bids:
        bids_by_plan_type.setdefault(bid.plan_type, []).append(bid)

    total_bids_by_plan_type = {pt: len(bids) for pt, bids in bids_by_plan_type.items()}
    total_completed_bids = len(all_bids)

    # Estimator stats
    from collections import defaultdict
    bids_by_estimator = defaultdict(int)
    for bid in all_bids:
        estimator_name = bid.estimator.estimatorName if bid.estimator else "Unassigned"
        bids_by_estimator[estimator_name] += 1

    branches = Branch.query.all()
    # Fetch distinct plan types and statuses for the filter dropdowns
    plan_types = [pt[0] for pt in db.session.query(Bid.plan_type).distinct().all()]
    statuses = ['all', 'Complete']

    return render_template('open_bids.html',
                           bids_by_plan_type=bids_by_plan_type,
                           total_bids_by_plan_type=total_bids_by_plan_type,
                           total_open_bids=total_completed_bids, # Renamed for clarity in completed bids context
                           bids_by_estimator=dict(bids_by_estimator),
                           sort_column=sort_column,
                           sort_direction=sort_direction,
                           plan_types=plan_types,
                           statuses=statuses,
                           current_status=status_filter,
                           current_plan_type=plan_type_filter,
                           due_date_start=due_date_start,
                           due_date_end=due_date_end,
                           branches=branches,
                           current_branch_id=branch_id)

@main.route('/debug_bids', methods=['GET'])
def debug_bids():
    incomplete_bids = Bid.query.filter_by(status='incomplete').all()
    return str(incomplete_bids)

@main.route('/add_design', methods=['GET', 'POST'])
def add_design():
    form = DesignForm()

    # Determine the branch_id for populating choices
    selected_branch_id = form.branch_id.data or request.args.get('branch_id', current_user.user_branch_id, type=int)

    # Populate Customer choices based on branch
    customer_query = Customer.query
    if selected_branch_id and selected_branch_id != 0:
        customer_query = customer_query.filter((Customer.branch_id == selected_branch_id) | (Customer.branch_id == None))
    
    form.customer_id.choices = [(0, 'Select a customer')] + [(customer.id, customer.name) for customer in customer_query.all()]
    # Populate designer choices based on branch
    form.designer_id.choices = get_branch_estimators(selected_branch_id, estimator_type='designer')
    form.branch_id.choices = [(b.branch_id, b.branch_name) for b in Branch.query.all()]
    
    if not form.branch_id.data:
        form.branch_id.data = selected_branch_id

    if form.validate_on_submit():
        new_design = Design(
            plan_name=form.plan_name.data, 
            customer_id=form.customer_id.data if form.customer_id.data != 0 else None, 
            project_address=form.project_address.data, 
            contractor=form.contractor.data, 
            preliminary_set_date=form.preliminary_set_date.data, 
            designer_id=form.designer_id.data if form.designer_id.data != 0 else None, 
            status=form.status.data, 
            plan_description=form.plan_description.data, 
            notes=form.notes.data,
            branch_id=form.branch_id.data
        )
        db.session.add(new_design)
        db.session.commit()
        flash('Design added successfully!', 'success')
        return redirect(url_for('main.index'))
    return render_template('add_design.html', form=form)

@main.route('/open_designs', methods=['GET'])
def open_designs():
    # Get the sort column from the query parameters, default to 'log_date'
    sort_column = request.args.get('sort', 'log_date')
    # Get the sort direction from the query parameters, default to 'asc'
    sort_direction = request.args.get('direction', 'asc')

    # Validate the sort direction
    if sort_direction not in ['asc', 'desc']:
        sort_direction = 'asc'

    # Get the status filter from the query parameters, default to 'Active'
    status_filter = request.args.get('status', 'Active')

    # Get the date filters from the query parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Define a mapping of column names to SQLAlchemy columns
    column_map = {
        'planNumber': Design.planNumber,
        'plan_name': Design.plan_name,
        'customer_name': Customer.name,
        'project_address': Design.project_address,
        'designer': Estimator.estimatorName,
        'status': Design.status,
        'log_date': Design.log_date,
        'notes': Design.notes
    }

    # Get the column to sort by, default to log_date
    sort_column_attr = column_map.get(sort_column, Design.log_date)

    # Apply sorting direction
    if sort_direction == 'desc':
        sort_column_attr = sort_column_attr.desc()

    # Base query for designs
    query = db.session.query(Design).join(Customer).join(Estimator, isouter=True)

    # Branch filtering
    branch_id = request.args.get('branch_id', current_user.user_branch_id, type=int)
    if branch_id and branch_id != 0:
        query = query.filter(Design.branch_id == branch_id)

    # Apply status filter
    query = query.filter(Design.status == status_filter)

    # Apply date filters if provided
    if start_date:
        start_date = datetime.strptime(start_date, '%m/%d/%y')
        query = query.filter(Design.log_date >= start_date)
    if end_date:
        end_date = datetime.strptime(end_date, '%m/%d/%y')
        query = query.filter(Design.log_date <= end_date)

    # Apply sorting
    open_designs = query.order_by(sort_column_attr).all()

    # Fetch distinct statuses for the filter dropdowns
    statuses = ['Active', 'Bid Set', 'Cancelled', 'Completed', 'On Hold']

    branches = Branch.query.all()
    return render_template('open_designs.html', designs=open_designs, sort_column=sort_column, sort_direction=sort_direction, statuses=statuses, current_status=status_filter,
                           branches=branches, current_branch_id=branch_id)

@main.route('/manage_design/<int:design_id>', methods=['GET', 'POST'])
def manage_design(design_id):
    design = Design.query.get_or_404(design_id)
    form = DesignForm(obj=design)  # Create an instance of your form and pass the design object

    # Populate customer and designer choices with a branch filter
    customer_query = Customer.query
    if design.branch_id:
        customer_query = customer_query.filter((Customer.branch_id == design.branch_id) | (Customer.branch_id == None))
    
    form.customer_id.choices = [(customer.id, customer.name) for customer in customer_query.all()]
    form.designer_id.choices = get_branch_estimators(design.branch_id, estimator_type='designer')
    form.branch_id.choices = [(b.branch_id, b.branch_name) for b in Branch.query.all()]

    if form.validate_on_submit():
        form.populate_obj(design)
        db.session.commit()
        flash('Design updated successfully!', 'success')
        return redirect(url_for('main.open_designs'))

    statuses = ['Active', 'Bid Set', 'Cancelled', 'Completed', 'On Hold']
    return render_template('manage_design.html', design=design, form=form, statuses=statuses)

@main.route('/bid_request', methods=['GET', 'POST'])
def bid_request():
    form = BidRequestForm()
    framing_form = FramingForm()
    siding_form = SidingForm()
    shingle_form = ShingleForm()
    deck_form = DeckForm()
    door_form = DoorForm()
    window_form = WindowForm()
    trim_form = TrimForm()

    # Determine current branch
    selected_branch_id = form.branch_id.data or request.args.get('branch_id', current_user.user_branch_id, type=int)

    # Filter Sales Reps and Customers by branch
    form.sales_rep.choices = get_branch_sales_reps(selected_branch_id)
    
    customer_query = Customer.query
    if selected_branch_id and selected_branch_id != 0:
        customer_query = customer_query.filter((Customer.branch_id == selected_branch_id) | (Customer.branch_id == None))
    form.customer_id.choices = [(0, 'Select Customer')] + [(c.id, c.name) for c in customer_query.all()]
    
    form.branch_id.choices = [(b.branch_id, b.branch_name) for b in Branch.query.all()]
    if not form.branch_id.data:
        form.branch_id.data = selected_branch_id

    if form.validate_on_submit():
        try:
            # Retrieve the selected Sales Rep
            sales_rep = SalesRep.query.get(form.sales_rep.data)
            if not sales_rep:
                flash('Invalid Sales Rep selected.', 'danger')
                return redirect(url_for('main.bid_request'))

            # Save the main Project instance
            project = Project(
                sales_rep_id=sales_rep.id,
                contractor=form.contractor.data,
                project_address=form.project_address.data,
                contractor_phone=form.contractor_phone.data,
                contractor_email=form.contractor_email.data,
                include_framing=form.include_framing.data,
                include_siding=form.include_siding.data,
                include_shingles=form.include_shingles.data,
                include_deck=form.include_deck.data,
                include_doors=form.include_doors.data,
                include_windows=form.include_windows.data,
                include_trim=form.include_trim.data,
                branch_id=form.branch_id.data
            )
            db.session.add(project)
            db.session.flush()  # Get project.id for related forms

            # Save related data conditionally
            save_related_forms(
                project.id,
                framing_form, siding_form, shingle_form,
                deck_form, door_form, window_form, trim_form,
                form.include_framing.data, form.include_siding.data,
                form.include_shingles.data, form.include_deck.data,
                form.include_doors.data, form.include_windows.data,
                form.include_trim.data
            )

            db.session.commit()
            flash('Bid request submitted successfully!', 'success')
            return redirect(url_for('main.bid_request'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", 'danger')

    return render_template(
        'bid_request.html',
        form=form,
        framing_form=framing_form,
        siding_form=siding_form,
        shingle_form=shingle_form,
        deck_form=deck_form,
        door_form=door_form,
        window_form=window_form,
        trim_form=trim_form
    )


def save_related_forms(
    project_id, framing_form, siding_form, shingle_form, deck_form,
    door_form, window_form, trim_form, include_framing, include_siding,
    include_shingles, include_deck, include_doors, include_windows,
    include_trim
):
    """Helper function to save related form data."""
    if include_framing:
        framing = Framing(
            project_id=project_id,
            plate=framing_form.plate.data,
            lot_type=framing_form.lot_type.data,
            basement_wall_height=framing_form.basement_wall_height.data,
            basement_exterior_walls=framing_form.basement_exterior_walls.data,
            basement_interior_walls=framing_form.basement_interior_walls.data,
            floor_framing=framing_form.floor_framing.data,
            floor_sheeting=framing_form.floor_sheeting.data,
            floor_adhesive=framing_form.floor_adhesive.data,
            exterior_walls=framing_form.exterior_walls.data,
            first_floor_wall_height=framing_form.first_floor_wall_height.data,
            second_floor_wall_height=framing_form.second_floor_wall_height.data,
            wall_sheeting=framing_form.wall_sheeting.data,
            roof_trusses=framing_form.roof_trusses.data,
            roof_sheeting=framing_form.roof_sheeting.data,
            framing_notes=framing_form.framing_notes.data
        )
        db.session.add(framing)

    if include_siding:
        siding = Siding(
            project_id=project_id,
            lap_type=siding_form.lap_type.data,
            panel_type=siding_form.panel_type.data,
            shake_type=siding_form.shake_type.data,
            soffit_trim=siding_form.soffit_trim.data,
            window_trim_detail=siding_form.window_trim_detail.data,
            siding_notes=siding_form.siding_notes.data
        )
        db.session.add(siding)

    if include_shingles:
        shingle = Shingle(
            project_id=project_id,
            shingle_notes=shingle_form.shingle_notes.data
        )
        db.session.add(shingle)

    if include_deck:
        deck = Deck(
            project_id=project_id,
            decking_type=deck_form.decking_type.data,
            railing_type=deck_form.railing_type.data,
            stairs=deck_form.stairs.data,
            deck_notes=deck_form.deck_notes.data
        )
        db.session.add(deck)

    if include_doors:
        door = Door(
            project_id=project_id,
            door_notes=door_form.door_notes.data
        )
        db.session.add(door)

    if include_windows:
        window = Window(
            project_id=project_id,
            window_notes=window_form.window_notes.data
        )
        db.session.add(window)

    if include_trim:
        trim = Trim(
            project_id=project_id,
            base=trim_form.base.data,
            case=trim_form.case.data,
            stair_material=trim_form.stair_material.data,
            door_material_type=trim_form.door_material_type.data,
            number_of_panels=trim_form.number_of_panels.data,
            door_hardware=trim_form.door_hardware.data,
            built_in_materials_type=trim_form.built_in_materials_type.data,
            plywood_1x_count=trim_form.plywood_1x_count.data,
            specify_count=trim_form.specify_count.data,
            trim_allowance=trim_form.trim_allowance.data,
            trim_notes=trim_form.trim_notes.data
        )
        db.session.add(trim)

@main.route('/projects', methods=['GET'])
@login_required
def projects():
    # Get the sort column and direction
    sort_column = request.args.get('sort', 'created_at')
    sort_direction = request.args.get('direction', 'asc')

    # Validate the sort direction
    if sort_direction not in ['asc', 'desc']:
        sort_direction = 'asc'

    # Pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    # Define column mapping
    column_map = {
        'project_address': Project.project_address,
        'contractor': Project.contractor,
        'created_at': Project.created_at,
        'last_updated_at': Project.last_updated_at
    }

    # Apply sorting
    sort_column_attr = column_map.get(sort_column, Project.created_at)
    if sort_direction == 'desc':
        sort_column_attr = sort_column_attr.desc()

    # Base query for projects
    query = Project.query

    # Branch filtering
    branch_id = request.args.get('branch_id', current_user.user_branch_id, type=int)
    if branch_id and branch_id != 0:
        query = query.filter(Project.branch_id == branch_id)

    query = query.order_by(sort_column_attr)

    # Apply pagination
    pagination = query.paginate(page=page, per_page=per_page)
    projects = pagination.items

    branches = Branch.query.all()
    return render_template(
        'projects.html',
        projects=projects,
        pagination=pagination,
        sort_column=sort_column,
        sort_direction=sort_direction,
        branches=branches,
        current_branch_id=branch_id
    )

@main.route('/manage_project/<int:project_id>', methods=['GET', 'POST'])
@login_required
def manage_project(project_id):
    project = Project.query.get_or_404(project_id)

    # Load forms with the project's current data
    form = BidRequestForm(obj=project)
    framing_form = FramingForm(obj=project.framing)
    siding_form = SidingForm(obj=project.siding)
    shingle_form = ShingleForm(obj=project.shingle)
    deck_form = DeckForm(obj=project.deck)
    door_form = DoorForm(obj=project.door)
    window_form = WindowForm(obj=project.window)
    trim_form = TrimForm(obj=project.trim)

    if form.validate_on_submit():
        try:
            # Update project data
            form.populate_obj(project)

            # Update related forms
            # update_related_forms(
            #     project.id,
            #     framing_form, siding_form, shingle_form, deck_form,
            #     door_form, window_form, trim_form,
            #     form.include_framing.data, form.include_siding.data,
            #     form.include_shingles.data, form.include_deck.data,
            #     form.include_doors.data, form.include_windows.data,
            #     form.include_trim.data
            # )

            db.session.commit()
            flash('Project updated successfully!', 'success')
            return redirect(url_for('main.projects'))
        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {str(e)}", 'danger')

    return render_template(
        'manage_project.html',
        project=project,
        form=form,
        framing_form=framing_form,
        siding_form=siding_form,
        shingle_form=shingle_form,
        deck_form=deck_form,
        door_form=door_form,
        window_form=window_form,
        trim_form=trim_form
    )
