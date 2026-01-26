from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app, jsonify, abort
from flask_login import login_required, current_user
from project import db, mail
from datetime import date
from sqlalchemy import func, cast, Date
from project.models import User, UserType, Customer, Bid, Estimator, Branch, UserSecurity, Design, LoginActivity, NotificationRule
from project.forms import UserForm, UpdateUserForm, UploadForm, CustomerForm, UserTypeForm, UserSecurityForm, SearchForm, NotificationRuleForm
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import csv
import io
import datetime
import string
import random
import chardet
from flask_mail import Message
from io import StringIO
import logging
from flask_migrate import upgrade

admin = Blueprint('admin', __name__)
logger = logging.getLogger(__name__)

# --- Helper Functions ---
def get_branch_estimators_admin(branch_id, estimator_type=None):
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

# --- Routes ---

@admin.route('/manage_users', methods=['GET', 'POST'])
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
        
    users_query = User.query.options(db.joinedload(User.branch), db.joinedload(User.usertype))
    
    # Branch Filter
    branch_id = request.args.get('branch_id', type=int)
    if branch_id and branch_id != 0:
        users_query = users_query.filter(User.user_branch_id == branch_id)
    
    users = users_query.all()
    branches = Branch.query.all()
    
    # User Types for Bulk Action
    usertypes = UserType.query.all()
    
    return render_template('manage_users.html', users=users, branches=branches, selected_branch_id=branch_id, usertypes=usertypes)

@admin.route('/bulk_update_users', methods=['POST'])
@login_required
def bulk_update_users():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    user_ids = request.form.getlist('user_ids')
    new_usertype_id = request.form.get('new_usertype_id')
    
    if not user_ids or not new_usertype_id:
        flash('Please select users and a user type.', 'warning')
        return redirect(url_for('admin.manage_users'))
        
    try:
        # Update users
        # Use bulk update for efficiency if possible, or loop (loop is safer for signals/listeners if any)
        # SQLAlchemy 'in_' query combined with update()
        count = User.query.filter(User.id.in_(user_ids)).update({User.usertype_id: new_usertype_id}, synchronize_session=False)
        db.session.commit()
        flash(f'Successfully updated {count} users.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating users: {str(e)}', 'danger')
        
    return redirect(url_for('admin.manage_users'))

@admin.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
        
    form = UserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            usertype_id=form.usertype_id.data,
            user_branch_id=form.user_branch_id.data,
            is_estimator=form.is_estimator.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()

        # Sync with Estimator table
        if user.is_estimator:
            existing_estimator = Estimator.query.filter_by(estimatorUsername=user.username).first()
            if not existing_estimator:
                new_estimator = Estimator(
                    estimatorName=user.username,
                    estimatorUsername=user.username,
                    type='Residential'
                )
                db.session.add(new_estimator)
                db.session.flush()
                user.estimatorID = new_estimator.estimatorID
            else:
                user.estimatorID = existing_estimator.estimatorID
        try:
            db.session.commit()
            flash('User created successfully!', 'success')
            return redirect(url_for('admin.manage_users'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating user: {str(e)}', 'danger')

    return render_template('add_user.html', form=form)

@admin.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(user_id)
    form = UpdateUserForm(obj=user)
    form.usertype_id.choices = [(ut.id, ut.name) for ut in UserType.query.all()]
    form.user_branch_id.choices = [(b.branch_id, b.branch_name) for b in Branch.query.all()]

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.usertype_id = form.usertype_id.data
        user.user_branch_id = form.user_branch_id.data
        user.is_estimator = form.is_estimator.data

        # Sync with Estimator table if marked as estimator
        if user.is_estimator:
            existing_estimator = Estimator.query.filter_by(estimatorUsername=user.username).first()
            if not existing_estimator:
                new_estimator = Estimator(
                    estimatorName=user.username, # Default name to username
                    estimatorUsername=user.username,
                    type='Residential' # Default type
                )
                db.session.add(new_estimator)
                db.session.flush() # Get the ID
                user.estimatorID = new_estimator.estimatorID
            else:
                user.estimatorID = existing_estimator.estimatorID

        if form.password.data:
            user.set_password(form.password.data)

        db.session.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for('admin.manage_users'))
    return render_template('edit_user.html', form=form, user=user)

@admin.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
        
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('admin.manage_users'))

@admin.route('/reset_password_admin/<int:user_id>', methods=['POST'])
@login_required
def reset_password(user_id):
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
        
    user = User.query.get_or_404(user_id)
    new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    user.password = generate_password_hash(new_password)
    db.session.commit()

    # Send email to user with new password
    msg = Message('Your Password Has Been Reset', sender='noreply@yourapp.com', recipients=[user.email])
    msg.body = f'Hello, {user.username}. Your new password is: {new_password}'
    mail.send(msg)

    flash('Password has been reset and emailed to the user.', 'success')
    return redirect(url_for('admin.edit_user', user_id=user.id))

@admin.route('/upload_users', methods=['POST'])
@login_required
def upload_users():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
        
    file = request.files['file']
    if file:
        stream = StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)
        headers = next(csv_input)  # Skip the header row
        users_to_add = []

        for row in csv_input:
            if len(row) < 4:  # Make sure the row has enough columns
                continue  # Skip rows that don't have enough columns

            username = row[0]
            email = row[1]
            usertype_id = int(row[2])
            user_branch_id = int(row[3])

            # Create a new user with a generic password
            user = User(
                username=username,
                email=email,
                password=generate_password_hash('beisser123'),  # Generic password
                usertype_id=usertype_id,
                user_branch_id=user_branch_id
            )
            users_to_add.append(user)

        # Bulk add users to the database
        db.session.bulk_save_objects(users_to_add)
        db.session.flush()  # Flush to assign IDs without committing

        db.session.commit()  # Final commit after all operations

        flash('Users uploaded successfully', 'success')
        return redirect(url_for('admin.manage_users'))
    flash('No file part', 'error')
    return redirect(request.url)

@admin.route('/manage_customers', methods=['GET', 'POST'])
@login_required
def manage_customers():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
        
    add_customer_form = CustomerForm()
    search_form = SearchForm()

    if add_customer_form.validate_on_submit():
        customer_code = add_customer_form.customerCode.data.strip()
        customer_name = add_customer_form.name.data.strip()
        if customer_code and customer_name:
            existing_customer = Customer.query.filter_by(customerCode=customer_code).first()
            if existing_customer:
                flash('Customer code already exists!', 'danger')
            else:
                new_customer = Customer(
                    customerCode=customer_code, 
                    name=customer_name,
                    branch_id=current_user.user_branch_id
                )
                db.session.add(new_customer)
                db.session.commit()
                flash('Customer added successfully!', 'success')
        else:
            flash('Please enter both customer code and name', 'danger')
        return redirect(url_for('admin.manage_customers'))

    branch_id = request.args.get('branch_id', current_user.user_branch_id, type=int)
    customers = Customer.query
    if branch_id and branch_id != 0:
        customers = customers.filter(Customer.branch_id == branch_id)
    customers = customers.order_by(Customer.customerCode).all()
    branches = Branch.query.all()
    return render_template('manage_customers.html', add_customer_form=add_customer_form, search_form=search_form, customers=customers, branches=branches, current_branch_id=branch_id)

@admin.route('/upload_customers', methods=['POST'])
@login_required
def upload_customers():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))

    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file:
        filename = secure_filename(file.filename)
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']

        stream = io.StringIO(raw_data.decode(encoding), newline=None)
        csv_input = csv.reader(stream)
        next(csv_input)  # Skip header if your CSV has one

        for row in csv_input:
            if len(row) < 2:
                continue  # Skip rows that do not have enough columns
            customer_code = row[0].strip()
            customer_name = row[1].strip()
            if not customer_code or not customer_name:
                continue  # Skip rows with empty fields

            existing_customer = Customer.query.filter_by(customerCode=customer_code).first()
            if existing_customer:
                existing_customer.name = customer_name  # Update the customer name if the code exists
            else:
                new_customer = Customer(customerCode=customer_code, name=customer_name)
                db.session.add(new_customer)

        try:
            db.session.commit()
            flash('Customers uploaded successfully!')
        except Exception as e:
            db.session.rollback()
            flash(f'Error uploading customers: {str(e)}')

        return redirect(url_for('admin.manage_customers'))

    return "Something went wrong", 400

@admin.route('/download_customers', methods=['GET'])
@login_required
def download_customers():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
        
    customers = Customer.query.all()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(['Code', 'Name'])
    for customer in customers:
        cw.writerow([customer.customerCode, customer.name])
    
    output = si.getvalue()
    si.close() # Close the StringIO object manually or assume it's GC'd, returning output is fine.
    
    # Need 'make_response'? Or just return string/bytes?
    # Original code likely used make_response or similar. 
    # I'll just return it as a Response object.
    from flask import Response
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=customers.csv"}
    )


@admin.route('/upload_historical_bids', methods=['GET', 'POST'])
@login_required
def upload_historical_bids():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
        
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        if file:
            filename = secure_filename(file.filename)
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']

            logger.info(f"Detected file encoding: {encoding}")

            stream = io.StringIO(raw_data.decode(encoding), newline=None)
            csv_input = csv.reader(stream)
            header = next(csv_input)  # Skip header if your CSV has one
            logger.info(f"CSV Header: {header}")

            for row in csv_input:
                try:
                    logger.info(f"Processing row: {row}")
                    plan_type = row[0]
                    customer_id = row[1]
                    project_name = row[2]
                    estimator_id = row[3] if row[3] else None
                    status = row[4]

                    # Handle missing dates
                    log_date = datetime.datetime.strptime(row[5], '%m/%d/%Y') if row[5] else None
                    due_date = datetime.datetime.strptime(row[6], '%m/%d/%Y') if row[6] else None

                    if not log_date or not due_date:
                        logger.warning(f"Skipping row due to missing log_date or due_date: {row}")
                        continue  # Ignore row if log_date or due_date is missing

                    completion_date = datetime.datetime.strptime(row[7], '%m/%d/%Y') if row[7] else None
                    notes = row[8]

                    new_bid = Bid(
                        plan_type=plan_type,
                        customer_id=customer_id,
                        project_name=project_name,
                        estimator_id=estimator_id,
                        status=status,
                        log_date=log_date,
                        due_date=due_date,
                        completion_date=completion_date,
                        notes=notes
                    )

                    db.session.add(new_bid)
                except Exception as e:
                    logger.error(f"Error processing row {row}: {e}")
                    flash(f"Error processing row: {row}", 'error')
                    db.session.rollback()

            try:
                db.session.commit()
                flash('Historical bids uploaded successfully!', 'success')
                logger.info("Historical bids uploaded successfully!")
            except Exception as e:
                logger.error(f"Error committing to database: {e}")
                flash('Error uploading historical bids. Please try again.', 'error')
                db.session.rollback()
            return redirect(url_for('main.index'))

    return render_template('upload_historical_bids.html', form=form)

@admin.route('/upload_historical_designs', methods=['GET', 'POST'])
@login_required
def upload_historical_designs():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))

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
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']

            stream = io.StringIO(raw_data.decode(encoding), newline=None)
            csv_input = csv.reader(stream)
            next(csv_input)  # Skip header if your CSV has one
            for row in csv_input:
                plan_number = row[0]
                plan_name = row[1]
                customer_id = row[2]
                project_address = row[3]
                contractor = row[4] if row[4] else None
                try:
                    login_date = datetime.datetime.strptime(row[5], '%Y-%m-%d')
                except ValueError:
                    continue  # Skip the row if date format is invalid
                designer_id = row[6] if row[6] else None
                status = row[7]
                plan_description = row[8] if len(row) > 8 else None
                notes = row[9] if len(row) > 9 else None

                new_design = Design(
                    planNumber=plan_number,
                    plan_name=plan_name,
                    customer_id=customer_id,
                    project_address=project_address,
                    contractor=contractor,
                    log_date=login_date,
                    designer_id=designer_id,
                    status=status,
                    plan_description=plan_description,
                    notes=notes
                )

                db.session.add(new_design)
            db.session.commit()
            flash('Historical designs uploaded successfully!')
            return redirect(url_for('main.index'))

    return render_template('upload_historical_designs.html')

@admin.route('/user_security', methods=['GET', 'POST'])
@login_required
def user_security():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))

    usertypes = UserType.query.all()
    form = UserSecurityForm(usertypes)

    if form.validate_on_submit():
        try:
            for usertype in usertypes:
                security = UserSecurity.query.filter_by(user_type_id=usertype.id).first()
                if security:
                    security.admin = getattr(form, f"admin_{usertype.id}").data
                    security.estimating = getattr(form, f"estimating_{usertype.id}").data
                    security.bid_request = getattr(form, f"bid_request_{usertype.id}").data
                    security.design = getattr(form, f"design_{usertype.id}").data
                    security.ewp = getattr(form, f"ewp_{usertype.id}").data
                    security.service = getattr(form, f"service_{usertype.id}").data
                    security.install = getattr(form, f"install_{usertype.id}").data
                    security.picking = getattr(form, f"picking_{usertype.id}").data
                    security.work_orders = getattr(form, f"work_orders_{usertype.id}").data
                    security.dashboards = getattr(form, f"dashboards_{usertype.id}").data
                    
                    # Manually mapping all security columns as per original code seems verbose but necessary.
                    # Or I can assume they are mapped. Original code had many updates.
                    # I'll include the ones visible in original.
                    security.security_10 = getattr(form, f"security_10_{usertype.id}").data
                    security.security_11 = getattr(form, f"security_11_{usertype.id}").data
                    security.security_12 = getattr(form, f"security_12_{usertype.id}").data
                    security.security_13 = getattr(form, f"security_13_{usertype.id}").data
                    security.security_14 = getattr(form, f"security_14_{usertype.id}").data
                    security.security_15 = getattr(form, f"security_15_{usertype.id}").data
                    security.security_16 = getattr(form, f"security_16_{usertype.id}").data
                    security.security_17 = getattr(form, f"security_17_{usertype.id}").data
                    security.security_18 = getattr(form, f"security_18_{usertype.id}").data
                    security.security_19 = getattr(form, f"security_19_{usertype.id}").data
                    security.security_20 = getattr(form, f"security_20_{usertype.id}").data
            db.session.commit()
            flash('User security updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating user security: {str(e)}', 'danger')
        return redirect(url_for('admin.user_security'))

    return render_template('user_security.html', form=form, usertypes=usertypes)

# Sales Rep management routes removed as SalesRep table is deprecated.
# Sales Reps are now managed via User roles.

@admin.route('/user_type', methods=['GET', 'POST'])
@login_required
def user_type():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
        
    form = UserTypeForm()
    usertypes = UserType.query.all()
    if form.validate_on_submit():
        usertype = UserType(name=form.name.data)
        db.session.add(usertype)
        db.session.commit()
        flash('User type added successfully!', 'success')
        return redirect(url_for('admin.user_type'))
    return render_template('user_type.html', form=form, usertypes=usertypes)

@admin.route('/delete_user_type/<int:usertype_id>', methods=['POST'])
@login_required
def delete_user_type(usertype_id):
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
        
    usertype = UserType.query.get_or_404(usertype_id)
    db.session.delete(usertype)
    db.session.commit()
    flash('User type deleted successfully', 'success')
    return redirect(url_for('admin.user_type'))

@admin.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))

    # Get the current date
    today = date.today()

    bids_completed_today = db.session.query(func.count(Bid.id)).filter(
        cast(Bid.completion_date, Date) == today
    ).scalar()

    users_logged_in_today = db.session.query(func.count(User.id)).filter(
        cast(User.last_login, Date) == today
    ).scalar()

    # Get the number of currently active users (assuming you have a way to track this)
    active_users = db.session.query(func.count(LoginActivity.user_id)).filter(
        LoginActivity.logged_out == None  # Assuming logged_out is set to NULL when the user is active
    ).scalar()

    return render_template(
        'admin_dashboard.html',
        bids_completed_today=bids_completed_today,
        users_logged_in_today=users_logged_in_today,
        active_users=active_users
    )

@admin.route('/perform_db_upgrade')
@login_required
def perform_db_upgrade():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    try:
        # Run the upgrade
        upgrade()
        return "Database upgraded successfully! You can go back now."
    except Exception as e:
        return f"Error during upgrade: {str(e)}", 500

@admin.route('/manage_notifications')
@login_required
def manage_notifications():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    
    rules = NotificationRule.query.order_by(NotificationRule.created_at.desc()).all()
    return render_template('manage_notifications.html', rules=rules)

@admin.route('/add_notification_rule', methods=['GET', 'POST'])
@login_required
def add_notification_rule():
    if not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))

    form = NotificationRuleForm()
    
    # Populate Event Choices
    form.event_type.choices = [('', 'Choose Event...'), ('new_bid', 'New Bid Submitted'), ('bid_completed', 'Bid Completed')]
    
    # Populate Role Choices
    roles = UserType.query.all()
    form.recipient_role.choices = [(0, 'Select Role...')] + [(r.id, r.name) for r in roles]
    
    # Populate User Choices
    users = User.query.all()
    form.recipient_user.choices = [(0, 'Select User...')] + [(u.id, f"{u.username} ({u.email})") for u in users]

    if form.validate_on_submit():
        event_type = form.event_type.data
        recipient_type = form.recipient_type.data
        
        recipient_name = "Unknown"
        recipient_id = None
        
        if recipient_type == 'user':
            recipient_id = form.recipient_user.data
            user = User.query.get(recipient_id)
            if user:
                 recipient_name = user.username
        elif recipient_type == 'role':
            recipient_id = form.recipient_role.data
            role = UserType.query.get(recipient_id)
            if role:
                recipient_name = role.name

        if event_type and recipient_type and recipient_id and recipient_id != 0:
            new_rule = NotificationRule(
                event_type=event_type,
                recipient_type=recipient_type,
                recipient_id=recipient_id,
                recipient_name=recipient_name
            )
            db.session.add(new_rule)
            db.session.commit()
            flash('Notification rule added.', 'success')
            return redirect(url_for('admin.manage_notifications'))
        else:
             flash('Please select a valid recipient for the chosen type.', 'danger')

    return render_template('add_notification_rule.html', form=form)

@admin.route('/delete_notification_rule/<int:rule_id>', methods=['POST'])
@login_required
def delete_notification_rule(rule_id):
    if not current_user.is_admin:
        abort(403)
        
    rule = NotificationRule.query.get_or_404(rule_id)
    db.session.delete(rule)
    db.session.commit()
    flash('Rule deleted.', 'success')
    return redirect(url_for('admin.manage_notifications'))

# --- Dynamic Bid Fields Management ---

from project.models import BidField, BidValue
from project.forms import BidFieldForm
import json

@admin.route('/manage_fields')
@login_required
def manage_fields():
    if not current_user.is_admin:
        abort(403)
    fields = BidField.query.order_by(BidField.is_active.desc(), BidField.sort_order).all()
    form = BidFieldForm() # For CSRF token in deletion forms
    return render_template('manage_fields.html', fields=fields, form=form)

@admin.route('/toggle_field_status/<int:field_id>', methods=['POST'])
@login_required
def toggle_field_status(field_id):
    if not current_user.is_admin:
        abort(403)
    field = BidField.query.get_or_404(field_id)
    field.is_active = not field.is_active
    db.session.commit()
    status = "Active" if field.is_active else "Inactive"
    flash(f'Field "{field.name}" is now {status}.', 'success')
    return redirect(url_for('admin.manage_fields'))

@admin.route('/add_field', methods=['GET', 'POST'])
@login_required
def add_field():
    if not current_user.is_admin:
        abort(403)
    
    form = BidFieldForm()
    # Populate branches
    branches = Branch.query.all()
    form.branch_ids.choices = [(b.branch_id, b.branch_name) for b in branches]

    if form.validate_on_submit():
        branch_ids_data = form.branch_ids.data 
        # If empty list, it means Applicable to ALL. Storing as JSON '[]' or null is fine.
        # But WTForms SelectMultipleField returns a list of values.
        
        filtered_branch_ids = [b for b in branch_ids_data if b]
        final_branch_ids = json.dumps(filtered_branch_ids) if filtered_branch_ids else None

        new_field = BidField(
            name=form.name.data,
            category=form.category.data,
            field_type=form.field_type.data,
            is_required=form.is_required.data,
            options=form.options.data,
            default_value=form.default_value.data,
            sort_order=int(form.sort_order.data) if form.sort_order.data.isdigit() else 0,
            branch_ids=final_branch_ids
        )
        db.session.add(new_field)
        db.session.commit()
        flash('Bid Field added successfully.', 'success')
        return redirect(url_for('admin.manage_fields'))

    return render_template('add_field.html', form=form, title="Add Bid Field")

@admin.route('/edit_field/<int:field_id>', methods=['GET', 'POST'])
@login_required
def edit_field(field_id):
    if not current_user.is_admin:
        abort(403)
    
    field = BidField.query.get_or_404(field_id)
    # Create form without binding object to prevent bad data causing crash on init
    form = BidFieldForm() 
    
    # Populate branches
    branches = Branch.query.all()
    form.branch_ids.choices = [(b.branch_id, b.branch_name) for b in branches]

    if request.method == 'GET':
        # Manually populate fields
        form.name.data = field.name
        form.category.data = field.category
        form.field_type.data = field.field_type
        form.is_required.data = field.is_required
        form.options.data = field.options
        form.default_value.data = field.default_value
        form.sort_order.data = str(field.sort_order)

        # Pre-select branches with safety check
        if field.branch_ids:
            try:
                data = json.loads(field.branch_ids)
                # Ensure it's a list (handle case where DB has "123" string or other weirdness)
                form.branch_ids.data = data if isinstance(data, list) else []
            except:
                form.branch_ids.data = []
        else:
            form.branch_ids.data = [] 

    if form.validate_on_submit():
        field.name = form.name.data
        field.category = form.category.data
        field.field_type = form.field_type.data
        field.is_required = form.is_required.data
        field.options = form.options.data
        field.default_value = form.default_value.data
        field.sort_order = int(form.sort_order.data) if form.sort_order.data.isdigit() else 0
        
        branch_ids_data = form.branch_ids.data
        branch_ids = [b for b in branch_ids_data if b]
        field.branch_ids = json.dumps(branch_ids) if branch_ids else None
        
        db.session.commit()
        flash('Bid Field updated successfully.', 'success')
        return redirect(url_for('admin.manage_fields'))

    return render_template('add_field.html', form=form, title="Edit Bid Field")

@admin.route('/delete_field/<int:field_id>', methods=['POST'])
@login_required
def delete_field(field_id):
    if not current_user.is_admin:
        abort(403)
    
    field = BidField.query.get_or_404(field_id)
    db.session.delete(field)
    db.session.commit()
    flash('Bid Field deleted.', 'success')
    return redirect(url_for('admin.manage_fields'))

@admin.route('/fields/reorder', methods=['POST'])
@login_required
def reorder_fields():
    if not current_user.is_admin:
        abort(403)
    
    data = request.get_json()
    field_ids = data.get('field_ids', [])
    
    if not field_ids:
        return jsonify({'error': 'No fields provided'}), 400

    try:
        # Update sort_order for each field in the list
        for index, field_id in enumerate(field_ids):
            field = BidField.query.get(field_id)
            if field:
                field.sort_order = index
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin.route('/fields/bulk_update', methods=['POST'])
@login_required
def bulk_update_fields():
    if not current_user.is_admin:
        abort(403)
    
    field_ids = request.form.getlist('field_ids')
    action = request.form.get('action')
    
    if not field_ids or not action:
        flash('No fields selected or invalid action.', 'warning')
        return redirect(url_for('admin.manage_fields'))
    
    try:
        fields = BidField.query.filter(BidField.id.in_(field_ids)).all()
        
        if action == 'set_required':
            for f in fields: f.is_required = True
        elif action == 'set_optional':
            for f in fields: f.is_required = False
        elif action == 'change_category':
            new_cat = request.form.get('category')
            if new_cat:
                for f in fields: f.category = new_cat
        elif action == 'add_branch':
            branch_id = request.form.get('branch_id')
            if branch_id:
                for f in fields:
                    current_branches = json.loads(f.branch_ids) if f.branch_ids else []
                    if str(branch_id) not in current_branches:
                        current_branches.append(str(branch_id))
                        f.branch_ids = json.dumps(current_branches)
        elif action == 'remove_branch':
            branch_id = request.form.get('branch_id')
            if branch_id:
                for f in fields:
                    current_branches = json.loads(f.branch_ids) if f.branch_ids else []
                    if str(branch_id) in current_branches:
                        current_branches.remove(str(branch_id))
                        f.branch_ids = json.dumps(current_branches)
                        
        db.session.commit()
        flash(f'Bulk action "{action}" applied to {len(fields)} fields.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error performing bulk action: {e}', 'danger')
        
    return redirect(url_for('admin.manage_fields'))
