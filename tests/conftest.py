import pytest
from project import db, create_app
from project.models import User, UserType, Branch, Customer, Estimator, Bid, Design, SalesRep

@pytest.fixture(scope='module')
def test_app():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SERVER_NAME': 'localhost.localdomain'
    })

    with app.app_context():
        db.create_all()
        
        # Setup initial data for tests
        admin_type = UserType(name='Admin')
        user_type = UserType(name='User')
        db.session.add_all([admin_type, user_type])
        
        test_branch = Branch(branch_name='Test Branch', branch_code='TB', branch_type=1)
        db.session.add(test_branch)
        db.session.commit()
        
        yield app
        db.drop_all()

@pytest.fixture(scope='module')
def test_client(test_app):
    return test_app.test_client()

@pytest.fixture(scope='module')
def init_database(test_app):
    with test_app.app_context():
        # Create a test user
        user = User(username='testuser', email='test@example.py', user_branch_id=1, usertype_id=2)
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
        yield db
        db.session.remove()
