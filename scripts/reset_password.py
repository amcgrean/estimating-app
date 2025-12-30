from flask import Flask
from project import db, create_app  # Adjust the import according to your app structure
from project.models import User  # Adjust the import according to your app structure
from werkzeug.security import generate_password_hash

app = create_app()
app.app_context().push()

user = User.query.get(2)
if user:
    user.password = generate_password_hash("valley forge")
    db.session.commit()
    print("Password updated for user with ID 2.")
else:
    print("No user with ID 2 found.")
