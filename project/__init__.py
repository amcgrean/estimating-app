from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from datetime import timedelta
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt


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
    if os.environ.get("VERCEL") and app.config["SECRET_KEY"] == "dev-secret-change-me":
        raise RuntimeError("SECRET_KEY is required in production")


    # --- Database ---
    # Prefer DATABASE_URL (common on hosts like Vercel/Render/Heroku-style)
    # Fall back to SQLALCHEMY_DATABASE_URI if you want to set that directly.
    db_url = os.environ.get("DATABASE_URL") or os.environ.get("SQLALCHEMY_DATABASE_URI")

    if not db_url:
        # local default for dev only (keeps you running locally)
        db_url = "sqlite:///bids.db"

    # Some providers supply postgres:// which SQLAlchemy expects as postgresql://
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    engine_opts = {}
    if db_url.startswith("sqlite:"):
        engine_opts = {"connect_args": {"timeout": 30}}
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = engine_opts


    # --- Paths / files (make these env-configurable) ---
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
    login_manager.login_view = 'main.login'
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "info"

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        logging.info(f'Loading user with ID: {user_id}')
        print("Loading user with ID:", user_id)
        return User.query.get(int(user_id))

    # Register blueprint
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Set up logging
import sys

if not app.debug:
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    app.logger.addHandler(stream_handler)


    return app