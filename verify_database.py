from project import create_app, db
from project.models import Bid, User

app = create_app()
app.app_context().push()

# Check bids table
bids = Bid.query.all()
print("Bids in the database:")
for bid in bids:
    print(bid)

# Check user table
users = User.query.all()
print("\nUsers in the database:")
for user in users:
    print(user)

# Check if user with id=2 is correctly set up
user = User.query.get(2)
if user:
    print("\nUser with ID 2:")
    print(user)
else:
    print("\nNo user with ID 2 found.")
