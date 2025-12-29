import os
from flask import Flask
from project import db, create_app  # Ensure you import create_app if you have a factory function
from project.models import Estimator  # Ensure you import the Estimator model

# Create the Flask application
app = create_app()  # If you have a factory function, use it to create the app

# Ensure the app context is set up correctly
with app.app_context():
    # Define the new estimator details
    estimator_name = "Aaron McGrean"
    estimator_username = "amcgrean"
    estimator_type = "Estimator"

    # Create a new estimator instance
    new_estimator = Estimator(estimatorName=estimator_name, estimatorUsername=estimator_username, type=estimator_type)

    # Add the new estimator to the session
    db.session.add(new_estimator)

    # Commit the changes to the database
    db.session.commit()

    print(f"Added new estimator: {estimator_name} with username: {estimator_username} and type: {estimator_type}.")
