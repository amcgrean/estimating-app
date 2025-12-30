import pytest
from flask import url_for

def test_login_page(test_client):
    response = test_client.get(url_for('auth.login'))
    assert response.status_code == 200
    assert b'Login' in response.data

def test_login_successful(test_client, init_database):
    response = test_client.post(url_for('auth.login'), data={
        'username': 'testuser',
        'password': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'testuser' in response.data or b'Dashboard' in response.data

def test_logout(test_client, init_database):
    test_client.post(url_for('auth.login'), data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    response = test_client.get(url_for('auth.logout'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data
