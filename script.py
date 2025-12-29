import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from project import create_app, db



db.create_all()

