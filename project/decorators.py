from functools import wraps
from flask import redirect, url_for, flash, request
from flask_login import current_user
from sqlalchemy.exc import InvalidRequestError
from project import db
import logging

def login_required_for_blueprint(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logging.info('Checking authentication for route: %s', request.endpoint)
        logging.info('User authenticated: %s', current_user.is_authenticated)
        try:
            if not current_user.is_authenticated:
                if request.path != '/login':  # Avoid redirect loop
                    flash('Please log in to access this page.', 'info')
                    logging.info('Redirecting to login page')
                    return redirect(url_for('main.login'))
            return f(*args, **kwargs)
        except InvalidRequestError:
            db.session.rollback()
            flash("An error occurred. Please try again.", "danger")
            logging.error('Database error, rolling back')
            return redirect(url_for('main.index'))
    return decorated_function
