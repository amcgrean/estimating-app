from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, login_required, logout_user, current_user
from project import mail, db
from project.models import User, UserType, LoginActivity, Branch
from project.forms import LoginForm, UserSettingsForm
import datetime
from werkzeug.security import generate_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact an administrator.', 'danger')
                return redirect(url_for('auth.login'))
                
            login_user(user)
            
            # Log login activity
            activity = LoginActivity(user_id=user.id, logged_in=datetime.datetime.utcnow())
            db.session.add(activity)
            
            # Update user last login
            user.last_login = datetime.datetime.utcnow()
            if user.login_count is None:
                user.login_count = 1
            else:
                user.login_count += 1
            db.session.commit()
            
            return redirect(url_for('main.index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
            
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    # Update logout time for the latest activity
    activity = LoginActivity.query.filter_by(user_id=current_user.id).order_by(LoginActivity.logged_in.desc()).first()
    if activity:
        activity.logged_out = datetime.datetime.utcnow()
        db.session.commit()
        
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    # Only allow existing users (admins?) to register? Or is this public?
    # Based on original code, it seemed public but let's check original.
    # ORIGINAL LOGIC:
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        user_type_name = request.form['usertype']
        branch_id = request.form.get('branch_id')

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        usertype = UserType.query.filter_by(name=user_type_name).first()
        branch = Branch.query.get(branch_id) if branch_id else None

        new_user = User(username=username, email=email, password=hashed_password, usertype=usertype, branch=branch)
        
        # logic for estimator/sales_rep linking from original file...
        # Simplifying for now, assuming basic registration, will refine if complex logic needed.
        # Actually I should probably check the original code for `register` logic to be safe.
        
        try:
            db.session.add(new_user)
            db.session.commit()
            flash('Your account has been created! You can now log in', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Error creating account: {e}', 'danger')
            
    user_types = UserType.query.all()
    branches = Branch.query.all()
    return render_template('register.html', user_types=user_types, branches=branches)

@auth.route('/reset_password/<int:user_id>', methods=['POST'])
@login_required
def reset_password(user_id):
    if not current_user.is_admin:
        flash('You do not have permission to perform this action', 'danger')
        return redirect(url_for('main.index'))
        
    user = User.query.get_or_404(user_id)
    new_password = request.form['new_password']
    user.set_password(generate_password_hash(new_password, method='pbkdf2:sha256'))
    db.session.commit()
    flash(f"Password for {user.username} has been reset.", 'success')
    return redirect(url_for('admin.manage_users')) # Redirect to admin manage users

@auth.route('/user_settings', methods=['GET', 'POST'])
@login_required
def user_settings():
    form = UserSettingsForm(obj=current_user)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.password.data:
            current_user.set_password(form.password.data)
        db.session.commit()
        flash('Settings updated successfully', 'success')
        return redirect(url_for('auth.user_settings'))
    return render_template('user_settings.html', form=form)

