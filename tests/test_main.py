import pytest
from flask import url_for

def test_dashboard_access_denied(test_client):
    response = test_client.get(url_for('main.index'))
    assert response.status_code == 302 # Redirect to login

def test_dashboard_authorized(test_client, init_database):
    test_client.post(url_for('auth.login'), data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    response = test_client.get(url_for('main.index'))
    assert response.status_code == 200
    assert b'Dashboard' in response.data

def test_open_bids_view(test_client, init_database):
    test_client.post(url_for('auth.login'), data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    response = test_client.get(url_for('main.open_bids'))
    assert response.status_code == 200
    assert b'Open Bids' in response.data
