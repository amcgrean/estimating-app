import os
from flask import Flask
from project import db, create_app  # Ensure you import create_app if you have a factory function
from project.models import Bid

# Create the Flask application
app = create_app()  # If you have a factory function, use it to create the app

# Ensure the app context is set up correctly
with app.app_context():
    # Define the old and new customer IDs
    old_customer_id = 614
    new_customer_id = 586

    # Query for bids with the old customer_id
    bids_to_update = Bid.query.filter_by(customer_id=old_customer_id).all()

    # Update the customer_id for these bids
    for bid in bids_to_update:
        bid.customer_id = new_customer_id

    # Commit the changes to the database
    db.session.commit()

    print(f"Updated {len(bids_to_update)} bids from customer ID {old_customer_id} to {new_customer_id}.")
