
import sys
import os
sys.path.append(os.getcwd())
from project import create_app, db
from project.models import User

def test_branch_login():
    app = create_app()
    app.config['WTF_CSRF_ENABLED'] = False # Disable CSRF for testing
    
    with app.test_client() as client:
        with app.app_context():
            # Get admin user details
            admin = User.query.filter_by(username='admin').first()
            if not admin:
                print("Admin user not found for test.")
                return
            
            print(f"Testing login for user: {admin.username} (Branch ID: {admin.user_branch_id})")
            
            # Login
            response = client.post('/login', data={
                'username': 'admin',
                'password': 'password123'
            }, follow_redirects=True)
            
            if response.status_code == 200:
                with client.session_transaction() as sess:
                    branch_id = sess.get('branch_id')
                    print(f"Session Branch ID: {branch_id}")
                    
                    if branch_id == admin.user_branch_id:
                        print("SUCCESS: Session branch matches user branch.")
                    else:
                        print(f"FAILURE: Session branch {branch_id} != User branch {admin.user_branch_id}")
            else:
                print(f"Login failed with status {response.status_code}")

if __name__ == "__main__":
    test_branch_login()
