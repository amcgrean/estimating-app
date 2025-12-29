# api/app.py
from project import create_app

app = create_app()

# Vercel looks for "app" by default for Flask
