from project import db, create_app
from project.models import User
import logging

app = create_app()
with app.app_context():
    logging.info("Starting password deletion script...")
    users = User.query.all()
    logging.info(f"Found {len(users)} users to update...")
    for user in users:
        logging.info(f"Deleting password for user {user.username}...")
        user.password = None
    db.session.commit()
    logging.info("Password deletion script complete!")