import logging
import mysql.connector
from datetime import datetime

# Disable Werkzeug logs in the console
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.propagate = False

# Create a new logger for database-related logs
db_logger = logging.getLogger('database')
db_logger.setLevel(logging.INFO)

# Create a new file handler for database logs
db_file_handler = logging.FileHandler('audit.log')
db_formatter = logging.Formatter('%(asctime)s : %(message)s')
db_file_handler.setFormatter(db_formatter)

# Add the file handler to the database logger
db_logger.addHandler(db_file_handler)

now = datetime.now()
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


def get_admin_id(username):
    query = "SELECT id FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    if result:
        admin_id = result[0]
        return admin_id
    else:
        return None


def assign_patient_to_doctor(patient_id, doctor_id):
    query = "UPDATE patients SET doctor_id = %s WHERE id = %s"
    cursor.execute(query, (doctor_id, patient_id))
    connection.commit()
    db_logger.info("Assigned patient %s to doctor %s", patient_id, doctor_id)


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


def add_patient(username, password, full_name, gender, contact_number, doctor_id):
    try:
        query = "INSERT INTO patients (username, password, full_name, gender, contact_number, doctor_id) " \
                "VALUES (%s, %s, %s, %s, %s, %s)"

        values = (username, password, full_name, gender, contact_number, doctor_id)
        cursor.execute(query, values)
        connection.commit()
        db_logger.info("Added new patient %s and assigned to doctor %s", username, doctor_id)
        return cursor.lastrowid
    except Exception as e:
        print("Error while adding patient:", e)
        return None

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


def get_assigned_doctor(patient_id):
    cursor.execute("SELECT doctor_id FROM patients WHERE id = %s", (patient_id,))
    assigned_doctor_id = cursor.fetchone()

    if assigned_doctor_id:
        # If an assigned doctor is found, fetch their information from the doctors table
        cursor.execute("SELECT username FROM doctors WHERE id = %s", (assigned_doctor_id[0],))
        assigned_doctor = cursor.fetchone()
        return assigned_doctor  # This will be a tuple containing (doctor_name, contact_number)

    return None  # Return None if no assigned doctor is found for the patient


def get_diagnosis_history(patient_id):
    cursor.execute("SELECT symptoms, disease, accuracy FROM patient_predictions WHERE patient_id = %s", (patient_id,))
    diagnosis_history = cursor.fetchall()
    if diagnosis_history:
        return diagnosis_history

    return None  # Return None if no diagnosis history is found for the patient

def doctor_exists(doctor_id):
    query = "SELECT * FROM doctors WHERE id = %s"
    cursor.execute(query, (doctor_id,))
    doctor = cursor.fetchone()
    return doctor is not None
