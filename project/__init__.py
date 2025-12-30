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

    engine_opts = {}
    if db_url.startswith("sqlite:"):
        engine_opts = {"connect_args": {"timeout": 30}}
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = engine_opts

    # --- Paths / files ---
    app.config["UPLOAD_FOLDER"] = os.environ.get("UPLOAD_FOLDER", "uploads")
    app.config["PDF_TEMPLATE"] = os.environ.get("PDF_TEMPLATE", "project/form.pdf")
    app.config["PDF_OUTPUT"] = os.environ.get("PDF_OUTPUT", "output.pdf")

    app.config["SESSION_TYPE"] = "filesystem"
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)

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
    
    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(admin_blueprint)

    # Logging (stdout is safest on serverless)
    if not app.debug:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)

    return app
