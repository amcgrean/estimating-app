import os
import sys
from unittest.mock import patch

# Add project root to path
sys.path.append(os.getcwd())

from project import create_app

def test_cron_endpoint():
    # Set the secret in environment
    secret = "beisser_erp_sync_secret_2024"
    os.environ["CRON_SECRET"] = secret
    
    app = create_app()
    client = app.test_client()
    
    print("--- Testing Unauthorized Request (No Header) ---")
    resp = client.get('/api/cron/sync-erp')
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 401
    
    print("\n--- Testing Unauthorized Request (Wrong Secret) ---")
    resp = client.get('/api/cron/sync-erp', headers={"Authorization": "Bearer wrong_secret"})
    print(f"Status: {resp.status_code}")
    assert resp.status_code == 401
    
    print("\n--- Testing Authorized Request (Dry Run Simulation) ---")
    # We use a patch to avoid actually importing thousands of rows during verification
    # just to see if the routing and auth works.
    with patch('project.blueprints.api.cron_routes.import_data') as mock_import:
        resp = client.get('/api/cron/sync-erp', headers={"Authorization": f"Bearer {secret}"})
        print(f"Status: {resp.status_code}")
        print(f"Response Body: {resp.data.decode()}")
        assert resp.status_code == 200
        assert mock_import.called == True
        print("Verification Successful: Endpoint is secure and correctly triggers import_data().")

if __name__ == "__main__":
    test_cron_endpoint()
