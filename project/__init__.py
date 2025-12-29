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

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/amcgrean/mysite/instance/bids.db?timeout=60'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'connect_args': {'timeout': 30}
    }
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
    app.config['UPLOAD_FOLDER'] = '/home/amcgrean/mysite/project/upload/folder'
    app.config['PDF_TEMPLATE'] = '/home/amcgrean/mysite/project/form.pdf'
    app.config['PDF_OUTPUT'] = '/home/amcgrean/mysite/project/output.pdf'
    app.config['SESSION_TYPE'] = 'filesystem'  # Update this line
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.config['LOGIN_VIEW'] = 'main.login'

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
    if not app.debug:
        handler = RotatingFileHandler('error.log', maxBytes=10000, backupCount=1)
        handler.setLevel(logging.INFO)
        app.logger.addHandler(handler)

    return app