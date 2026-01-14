# api/app.py
import sys
import os

# Add the parent directory to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from project import create_app

app = create_app()

# Vercel looks for "app" by default for Flask
