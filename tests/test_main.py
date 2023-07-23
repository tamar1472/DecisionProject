import pytest
import sys
sys.path.append(r"C:\Users\תמר\PycharmProjects\DecisionProject")
from main import app
from flask import session
import db_operations



@pytest.fixture
def client():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['role'] = 'admin'
        yield client

def test_login_admin(client):
    response = client.post('/', data={'username': 'tamar', 'password': '1234'})
    assert b"admin" in response.data

def test_login_admin_not_found(client):
    response = client.post('/', data={'username': 'some_nonexistent_username', 'password': 'some_password'})
    assert b"admin" not in response.data

def test_login_patient(client):
    response = client.post('/', data={'username': 'bathen', 'password': '1234'})
    assert b"patient" in response.data


def test_login_patient_not_found(client):
    response = client.post('/', data={'username': 'some_nonexistent_username', 'password': 'some_password'})
    assert b"patient" not in response.data

def test_login_doctor(client):
    response = client.post('/', data={'username': 'liran', 'password': '1234'})
    assert b"doctor" in response.data

def test_login_doctor_not_found(client):
    response = client.post('/', data={'username': 'some_nonexistent_username', 'password': 'some_password'})
    assert b"doctor" not in response.data


def test_admin_access(client):
    # Set up a session with the role 'admin'
    with client.session_transaction() as sess:
        sess['role'] = 'admin'

    # Send a GET request to the admin route
    response = client.get('/admin')
    assert response.status_code == 200

def test_patient_access(client):

    with client.session_transaction() as sess:
        sess['role'] = 'patient'

    # Send a GET request to the admin route
    response = client.get('/patient')
    assert response.status_code == 200

def test_doctor_access(client):
    with client.session_transaction() as sess:
        sess['role'] = 'doctor'
        sess['username'] = 'dummy_doctor'  # Set a dummy username for the test

    response = client.get('/doctor')
    assert response.status_code == 200


def test_non_admin_redirect(client):
    # Set up a session with a non-admin role (e.g., 'patient' or 'doctor')
    with client.session_transaction() as sess:
        sess['role'] = 'patient'  # or 'doctor'

    # Send a GET request to the admin route
    response = client.get('/admin', follow_redirects=True)
    assert response.status_code == 200  # If it successfully redirects to the login route, it will return 200 for the login page.
    assert b'Please Sign In' in response.data  # Assuming that the login page contains the text "Please Sign In"


def test_non_doctor_redirect(client):
    # Set up a session with a non-admin role (e.g., 'patient' or 'doctor')
    with client.session_transaction() as sess:
        sess['role'] = 'patient'  # or 'doctor'

    # Send a GET request to the admin route
    response = client.get('/doctor', follow_redirects=True)
    assert response.status_code == 200  # If it successfully redirects to the login route, it will return 200 for the login page.
    assert b'Please Sign In' in response.data  # Assuming that the login page contains the text "Please Sign In"

def test_non_patient_redirect(client):
    # Set up a session with a non-admin role (e.g., 'patient' or 'doctor')
    with client.session_transaction() as sess:
        sess['role'] = 'admin'  # or 'doctor'

    # Send a GET request to the admin route
    response = client.get('/patient', follow_redirects=True)
    assert response.status_code == 200  # If it successfully redirects to the login route, it will return 200 for the login page.
    assert b'Please Sign In' in response.data  # Assuming that the login page contains the text "Please Sign In"

def test_diagnose_patient_missing_patient_id_doctor_post(client):
    # Simulate a doctor user
    with client.session_transaction() as sess:
        sess['role'] = 'doctor'

    response = client.post('/symptoms', data={'selected_symptoms': ['Fever']})
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/doctor')

def test_diagnose_patient_missing_symptoms_post(client):
    # Simulate a doctor user
    with client.session_transaction() as sess:
        sess['role'] = 'doctor'

    response = client.post('/symptoms')
    assert response.status_code == 302
    assert b"doctor" in response.data

def test_diagnose_patient_missing_symptoms(client):
    # Simulate a doctor user
    with client.session_transaction() as sess:
        sess['role'] = 'admin'

    response = client.post('/symptoms')
    assert response.status_code == 200
    assert b"admin" in response.data

def test_diagnose_patient_valid_patient_id_post(client):
    # Simulate a doctor user
    with client.session_transaction() as sess:
        sess['role'] = 'doctor'

    response = client.post('/symptoms', data={'selected_symptoms': ['Fatigue'], 'patient_id': 5})
    assert response.status_code == 302
    assert b"doctor" in response.data
def test_diagnose_patient_invalid_patient_id_post(client):
    # Simulate a doctor user
    with client.session_transaction() as sess:
        sess['role'] = 'doctor'

    response = client.post('/symptoms', data={'selected_symptoms': ['szsdf'], 'patient_id': 5})
    assert response.status_code == 302
    assert b"doctor" in response.data

def test_diagnose_patient_invalid_role_get(client):
    # Simulate a user with an invalid role
    with client.session_transaction() as sess:
        sess['role'] = 'invalid'

    response = client.get('/admin')
    assert response.status_code == 302
    assert b"/" in response.data

def test_diagnose_patient_valid_role_get(client):
    # Simulate a user with an invalid role
    with client.session_transaction() as sess:
        sess['role'] = 'admin'

    response = client.get('/admin')
    assert response.status_code == 200
    assert b"Error while loading model: name 'model' is not defined" in response.data

def test_diagnose_patient_invalid_symptoms_get(client):
    # Simulate a doctor user
    with client.session_transaction() as sess:
        sess['role'] = 'doctor'

    response = client.get('/symptoms', data={'selected_symptoms': ['pink elephant']})
    assert response.status_code == 200
    assert b"doctor" in response.data