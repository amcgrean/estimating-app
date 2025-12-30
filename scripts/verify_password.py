from werkzeug.security import check_password_hash
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
            # Password to verify
            password_to_verify = "Beisser1953!"
            
            # Check if the password matches the stored hash
            if check_password_hash(user.password, password_to_verify):
                print("The password matches.")
            else:
                print("The password does not match.")
        else:
            print("User with id=2 not found.")
    except Exception as e:
        print(f"An error occurred: {e}")
