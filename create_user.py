from project import create_app, db
from project.models import User
from werkzeug.security import generate_password_hash

app = create_app()
app.app_context().push()

def create_user():
    user = User(
        username='rboes',
        email='rboes@beisserlumber.com',
        usertype_id=2,
        estimatorID=4
    )
    user.password = generate_password_hash('your_password_here')
    db.session.add(user)
    try:
        db.session.commit()
        print('User created successfully!')
    except Exception as e:
        db.session.rollback()
        print(f'Error creating user: {str(e)}')

if __name__ == '__main__':
    create_user()
