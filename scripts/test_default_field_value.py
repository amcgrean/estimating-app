
import sys
import os
import unittest
import traceback
import random
import string

# Add project root to path
sys.path.append(os.getcwd())

from project import create_app, db
from project.models import User, BidField, UserType, Branch

class TestDefaultValue(unittest.TestCase):
    def test_full_flow(self):
        app = create_app()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        client = app.test_client()
        app_context = app.app_context()
        app_context.push()

        test_field = None
        user = None

        try:
            print("Beginning Test Setup...")
            # Create Unique Test User
            suffix = ''.join(random.choices(string.ascii_lowercase, k=6))
            username = f'test_def_{suffix}'
            
            # Ensure UserType
            ut = UserType.query.filter_by(name='Estimator').first()
            if not ut:
                 ut = UserType(name='Estimator')
                 db.session.add(ut)
                 db.session.commit()
            
            # Ensure Branch
            br = Branch.query.first()
            if not br:
                br = Branch(branch_name="Test Branch")
                db.session.add(br)
                db.session.commit()

            user = User(
                username=username,
                email=f'{username}@example.com',
                usertype_id=ut.id,
                user_branch_id=br.branch_id,
                password='hashed_password_placeholder' 
            )
            user.set_password('testpass')
            db.session.add(user)
            db.session.commit()
            print(f"Created User: {username}")

            # Create Test BidField
            test_field = BidField(
                name=f'Test Default Field {suffix}',
                category='Framing',
                field_type='select',
                options='Option A, Option B, Option C',
                default_value='Option B',
                sort_order=999
            )
            db.session.add(test_field)
            db.session.commit()
            print(f"Created Field: {test_field.name} with ID: {test_field.id}")

            # Login
            login_resp = client.post('/login', data=dict(
                username=username,
                password='testpass'
            ), follow_redirects=True)
            
            if b'Dashboard' not in login_resp.data and b'Logout' not in login_resp.data:
                 print("Login Response Logic Check Failed. Dumping partial response:")
                 print(login_resp.data[:500])
                 raise Exception("Login failed")

            # GET Add Bid Page
            response = client.get('/add_bid')
            if response.status_code != 200:
                print(f"Add Bid route failed with {response.status_code}")
                raise Exception("Failed to load add_bid page")
            
            html = response.data.decode('utf-8')
            
            # Verify Field Name Presence
            if test_field.name not in html:
                print("HTML content excerpt around expected field:")
                # Try to find something close or just dump generic info
                raise Exception(f"Field name '{test_field.name}' not found in HTML")

            # Verify Default Value Selection
            # We expect: value="Option B" selected OR selected value="Option B" (order varies but typically value then selected)
            # Jinja rendered: <option value="Option B" selected>Option B</option>
            
            target_str = 'value="Option B" selected'
            if target_str not in html:
                # Try alternative check
                if 'selected value="Option B"' not in html:
                     print("Available options in HTML for debugging:")
                     # In a real scenario I'd regex search, but here just print failure
                     raise Exception("Default value 'Option B' not marked as selected in HTML")

            print("SUCCESS: Default value verified correctly.")

        except Exception:
            traceback.print_exc()
            self.fail("Test raised an exception")
        
        finally:
            print("Teardown...")
            if test_field:
                db.session.delete(test_field)
            if user:
                db.session.delete(user)
            db.session.commit()
            app_context.pop()

if __name__ == '__main__':
    unittest.main()
