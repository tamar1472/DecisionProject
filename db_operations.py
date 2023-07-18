import logging
import flask
import mysql.connector
from datetime import datetime


# Disable Werkzeug logs in the console
logger = logging.getLogger(__name__)
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.propagate = False

# database connection
connection = mysql.connector.connect(host="localhost", user="tamar", passwd="123456", database="decision_project")

cursor = connection.cursor()
def login(username, password):
    fetch = 'SELECT role FROM users WHERE username = %s AND password = %s'
    cursor.execute(fetch, (username, password,))
    result = cursor.fetchall()
    if result is None:
        return "Invalid credentials"
    else:
        role = result[0]
    return role

def users():
    cursor.execute("SELECT id, username, role FROM users")
    users = cursor.fetchall()
    return users

def get_doctor_id(username):
    query = "SELECT id FROM doctors WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    if result:
        doctor_id = result[0]
        return doctor_id
    else:
        return None

def get_patient_id(username):
    query = "SELECT id FROM patients WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    if result:
        patient_id = result[0]
        return patient_id
    else:
        return None
def assign_patient_to_doctor(patient_id, doctor_id):
    query = "UPDATE patients SET doctor_id = %s WHERE id = %s"
    cursor.execute(query, (doctor_id, patient_id))
    connection.commit()


def get_assigned_patients(doctor_id):
    # Retrieve the patients assigned to the specified doctor
    query = "SELECT * FROM patients WHERE doctor_id = %s"
    cursor.execute(query, (doctor_id,))
    assigned_patients = cursor.fetchall()

    return assigned_patients

def add_user_to_table(username, password, full_name, role, doctor_id=None):
    # Insert the user's details into the users table
    query = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
    cursor.execute(query, (username, password, role))
    connection.commit()

    # Get the last inserted user ID
    user_id = cursor.lastrowid

    # Insert the user's details into the corresponding table based on their role
    if role == 'patient':
        query = "INSERT INTO patients (user_id, gender, contact_number, doctor_id) " \
                "VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (user_id, 'Male', '', doctor_id))
    elif role == 'doctor':
        query = "INSERT INTO doctors (username, password, full_name) VALUES (%s, %s, %s)"
        cursor.execute(query, (username, password, full_name))

    connection.commit()

    # Close the database connection
    # cursor.close()
    # connection.close()

    # Usage example


def add_patient(username, password, full_name, gender, contact_number, doctor_id):
    query = "INSERT INTO patients (username, password, full_name, gender, contact_number, doctor_id) " \
            "VALUES (%s, %s, %s, %s, %s, %s)"
    values = (username, password, full_name, gender, contact_number, doctor_id)
    cursor.execute(query, values)
    connection.commit()
    return cursor.lastrowid

def add_user(username, password, role):
    query = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
    values = (username, password, role)
    cursor.execute(query, values)
    connection.commit()
    return cursor.lastrowid


def add_doctor(username, password, full_name):
    query = "INSERT INTO doctors (username, password, full_name) VALUES (%s, %s, %s)"
    values = (username, password, full_name)
    cursor.execute(query, values)
    connection.commit()
    return cursor.lastrowid