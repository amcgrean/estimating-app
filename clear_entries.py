import os
from werkzeug.security import generate_password_hash
from flask import Flask
from project import db, create_app  # Adjust the import according to your app structure
from project.models import User  # Adjust the import according to your app structure

# Create the Flask application
app = create_app()  # If you have a factory function, use it to create the app

# Ensure the app context is set up correctly
with app.app_context():
    try:
        # Find the user with id=2
        user = User.query.get(2)
        if user:
            # Hash the new password
            new_password = "valley forge"
            hashed_password = generate_password_hash(new_password)

            # Update the user's password
            user.password = hashed_password
            db.session.commit()

            print("Password for user with id=2 has been successfully updated.")
        else:
            print("User with id=2 not found.")
    except Exception as e:
        db.session.rollback()
        print(f"An error occurred: {e}")
