import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

bcrypt = Bcrypt()
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()


def create_app():
    app = Flask(__name__)

    # --- Core secrets ---
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # --- Database ---
    db_url = (
        os.environ.get("DATABASE_URL") 
        or os.environ.get("POSTGRES_URL") 
        or os.environ.get("SQLALCHEMY_DATABASE_URI")
    )
    if not db_url:
        db_url = "sqlite:///bids.db"

    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    engine_opts = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
    if db_url.startswith("sqlite:"):
        engine_opts = {"connect_args": {"timeout": 30}}
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = engine_opts

    # --- Email Configuration ---
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT') or 587)
    app.config['MAIL_USE_TLS'] = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER')

    # --- Paths / files ---
    app.config["UPLOAD_FOLDER"] = os.environ.get("UPLOAD_FOLDER", "uploads")
    app.config["PDF_TEMPLATE"] = os.environ.get("PDF_TEMPLATE", "project/form.pdf")
    app.config["PDF_OUTPUT"] = os.environ.get("PDF_OUTPUT", "output.pdf")

    # Session Configuration
    # Vercel (serverless) cannot use filesystem sessions.
    # If on Vercel, we skip Flask-Session and use Flask's default client-side secure cookies.
    is_vercel = os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME")

    if not is_vercel:
        app.config["SESSION_TYPE"] = "filesystem"
    
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    
    if not is_vercel:
        from flask_session import Session
        Session(app)

    from .models import Branch
    @app.context_processor
    def inject_branches():
        from flask import session
        from flask_login import current_user
        
        branches = Branch.query.all()
        
        # Default branch logic
        current_branch_id = session.get('branch_id')
        if current_branch_id is None and current_user.is_authenticated:
            current_branch_id = current_user.user_branch_id
            session['branch_id'] = current_branch_id
        
        return {
            'all_branches': branches,
            'current_branch_id': current_branch_id
        }

    # Flask-Login configuration
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    from .models import User  # noqa: E402

    @login_manager.user_loader
    def load_user(user_id):
        # Works on SQLAlchemy 1.4+; if you upgraded to SQLAlchemy 2.x use db.session.get
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    # Register blueprint
    # Register blueprints
    from .blueprints.main.routes import main as main_blueprint
    from .blueprints.auth.routes import auth as auth_blueprint
    from .blueprints.admin.routes import admin as admin_blueprint
    from .blueprints.debug.routes import debug_bp
    
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(debug_bp)

    # Logging (stdout is safest on serverless)
    if not app.debug:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)

    return app
