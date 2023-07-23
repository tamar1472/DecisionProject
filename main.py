from flask import Flask, render_template, request, url_for, redirect, session, flash
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import pandas as pd
import db_operations
from db_operations import db_logger
from RandomForestSupportModel import RandomForestSupportModel
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'mysecretkey'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
model_path = "C:\\Users\\תמר\\PycharmProjects\\DecisionProject\\model.pkl"

try:
    connection = mysql.connector.connect(user='tamar', password='123456', host='127.0.0.1', port=3306,
                                         database='decision_project',
                                         auth_plugin='mysql_native_password')
    if connection.is_connected():
        db_Info = connection.get_server_info()
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)
        db_logger.info("Connected to MySQL Server")

        # cursor.close()
        # connection.close()
        # print("MySQL connection is closed")
except Error as e:
    print("Error while connecting to MySQL", e)
    db_logger.error("Error while connecting to MySQL: %s", e)

try:
    model = RandomForestSupportModel.load(model_path)
except Error as e:
    print("Error while loading model", e)
except AttributeError:
    pass

symptoms = ['Itching', 'Muscle pain', 'Dark urine', 'Mild fever', 'Abdominal pain',
            'Unsteadiness', 'Yellowing of eyes', 'Altered sensorium',
            'Red spots over body', 'High fever', 'Fatigue', 'Chest pain',
            'Loss of appetite', 'Dehydration', 'Dischromic patches',
            'Breathlessness', 'Family history', 'Rusty sputum',
            'Pain behind the eyes', 'Nausea', 'Joint pain', 'Diarrhoea', 'Vomiting',
            'Nodal skin eruptions', 'Weight loss', 'Lack of concentration',
            'Headache', 'Stomach bleeding', 'Muscle weakness',
            'Continuous feel of urine', 'Polyuria', 'Sweating',
            'Pus filled pimples', 'Bladder discomfort', 'Patches in throat',
            'Passage of gases', 'Increased appetite',
            'History of alcohol consumption', 'Receiving blood transfusion',
            'Extra marital contacts', 'Lethargy', 'Abnormal menstruation',
            'Ulcers on tongue', 'Small dents in nails', 'Back pain', 'Acidity',
            'Loss of balance', 'Blackheads', 'Pain in anal region',
            'Watering from eyes']


@app.route('/', methods=["POST", "GET"])
def login():
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        result = db_operations.login(username, password)
        if result[0] == 'admin':
            session["username"] = username
            session["role"] = "admin"
            db_logger.info("ADMIN Connected")
            return redirect(url_for('admin'))

        if result[0] == 'patient':
            session["username"] = username
            session["role"] = "patient"
            db_logger.info("PATIENT Connected")
            return redirect(url_for('patient_panel'))

        if result[0] == 'doctor':
            session["username"] = username
            session["role"] = "doctor"
            db_logger.info("DOCTOR Connected")
            return redirect(url_for('doctor'))

    return render_template('login.html')
@app.route('/admin', methods=["POST", "GET"])
def admin():
    if session.get("role") != 'admin':
        return redirect(url_for('login'))
    try:
        feature_imp = model.clf.feature_importances_
        feature_name = model.clf.feature_names_in_
        sorted_list = sorted(list(zip(feature_imp, feature_name)), key=lambda x: x[0], reverse=True)
        sorted_feature_imp = [item[0] for item in sorted_list]
        sorted_feature_name = [item[1] for item in sorted_list]
        feature_imp_df = pd.Series(sorted_feature_imp, index=sorted_feature_name)
        # Generate the graph
        image_base64 = generate_graph(feature_imp_df)

        users = db_operations.users()
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            role = request.form['role']

            if role == 'admin':
                # Add the user to the 'users' table with role='admin'
                db_operations.add_user(username, password, role)
                db_logger.info("ADMIN added a new user admin")

            elif role == 'doctor':

                # Add the doctor to the 'doctors' table
                full_name = request.form['doctor_full_name']
                db_operations.add_doctor(username, password, full_name)

                db_logger.info("ADMIN added a new user doctor")

                # Add the doctor to the 'users' table with role='doctor'
                db_operations.add_user(username, password, role)

            elif role == 'patient':
                # Add the patient to the 'patients' table
                full_name = request.form['full_name']
                gender = request.form['gender']
                contact_number = request.form['contact_number']
                doctor_id = request.form['doctor_id']

                if db_operations.doctor_exists(doctor_id):
                    db_operations.add_patient(username, password, full_name, gender, contact_number, doctor_id)
                    db_logger.info("ADMIN added a new user patient")

                    # Add the patient to the 'users' table with role='patient'
                    db_operations.add_user(username, password, role)
                else:
                    flash("Doctor with the specified ID does not exist. Please choose another doctor.")
                    return render_template('admin.html', image_base64=image_base64, users=users, show_flash=True)

            return redirect(url_for('admin'))

        return render_template('admin.html', image_base64=image_base64, users=users)

    except Exception as e:
        return "Error while loading model: " + str(e)


@app.route('/doctor', methods=["POST", "GET"])
def doctor():
    if session["role"] != 'doctor':
        return redirect(url_for('login'))
    # Get the doctor's ID based on their username
    doctor_id = db_operations.get_doctor_id(session["username"])
    print(doctor_id)
    assigned_patients = db_operations.get_assigned_patients(doctor_id)

    if request.method == 'POST':
        print(request.method)
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        gender = request.form['gender']
        contact_number = request.form['contact_number']
        # Add the patient to the 'patients' table
        print("Doctor function called.")
        patient_id = db_operations.add_patient(username, password, full_name, gender, contact_number, doctor_id)
        db_logger.info("DOCTOR added a new user patient")

        if patient_id is not None:
            # Add the patient to the 'users' table with role='patient'
            db_operations.add_user(username, password, 'patient')

        return redirect(url_for('doctor'))

    return render_template('doctor.html', assigned_patients=assigned_patients)


@app.route('/patient', methods=["GET"])
def patient_panel():
    if 'role' not in session or session["role"] != 'patient':
        return redirect(url_for('login'))
    # Get the patient_id using the username from the session
    patient_id = db_operations.get_patient_id(session.get("username"))

    # Retrieve the assigned doctor and patient's diagnosis history from the database
    assigned_doctor = db_operations.get_assigned_doctor(patient_id)
    diagnosis_history = db_operations.get_diagnosis_history(patient_id)

    return render_template('patient.html', patient_id=patient_id, assigned_doctor=assigned_doctor,
                           diagnosis_history=diagnosis_history)


@app.route('/symptoms', methods=["GET", "POST"])
def diagnose_patient():
    if 'role' not in session:
        return redirect(url_for('login'))

    patient_id = request.form.get('patient_id', type=int)

    if session["role"] == 'doctor' and request.method == 'POST':
        # If the user is a doctor, check the patient_id provided in the form submission
        patient_id = request.args.get('patient_id', type=int)
        if patient_id is None:
            # If patient_id is not provided, redirect to the doctor's panel or display an error message
            db_logger.warning("No patient_id provided in form submission for doctor.")
            return redirect(url_for('doctor'))

    if session["role"] == 'patient':
        # If the user is a patient, use their own patient_id if available
        patient_id = db_operations.get_patient_id(session.get("username"))

    if request.method == 'POST':
        selected_symptoms = request.form.getlist('selected_symptoms')

        if selected_symptoms:
            # Perform the diagnosis and store the result
            new_line = model.line.copy()
            new_line.columns = new_line.columns.astype(str)
            for symptom in selected_symptoms:
                index = symptoms.index(symptom)
                new_line.iloc[0][index] = 1
            prediction = model.make_prediction(new_line)

            if session["role"] == 'admin':
                # If the user is an admin, store the admin diagnosis in the admin_predictions table
                query = "INSERT INTO admin_predictions (admin_username, symptoms, disease, accuracy) VALUES (%s, %s, %s, %s)"
                admin_username = session["username"]
                symptoms_str = ", ".join(selected_symptoms)
                prediction_disease = prediction[0]
                prediction_accuracy = prediction[1]
                values = (admin_username, symptoms_str, prediction_disease, prediction_accuracy)
            else:
                # If the user is a patient, store the patient diagnosis in the patient_predictions table
                query = "INSERT INTO patient_predictions (patient_id, symptoms, disease, accuracy) VALUES (%s, %s, %s, %s)"
                symptoms_str = ", ".join(selected_symptoms)
                values = (patient_id, symptoms_str, prediction[0], prediction[1])

            cursor.execute(query, values)
            connection.commit()
            db_logger.info("Diagnosis stored for patient_id: %s", patient_id)
            return render_template('main.html', symptoms=symptoms, prediction=prediction, patient_id=patient_id)

        # If no symptoms are selected, show an error message
        error_message = "Please select at least one symptom for diagnosis."
        print(error_message)
        return render_template('main.html', symptoms=symptoms, error_message=error_message, patient_id=patient_id)

    return render_template('main.html', symptoms=symptoms, patient_id=patient_id)


@app.route('/view_diagnosis_history/<int:patient_id>')
def view_diagnosis_history(patient_id):
    diagnosis_history = db_operations.get_diagnosis_history(patient_id)
    db_logger.info("Doctor viewed patient ID %s Diagnose history", patient_id)
    return render_template('diagnosis_history.html', diagnosis_history=diagnosis_history)


def generate_graph(feature_imp):
    # Adjust the figure size and margins
    plt.figure(figsize=(12, 9))
    plt.subplots_adjust(left=0.25, right=0.75, top=0.9, bottom=0.1)
    # Generate the graph
    sns.set_style("whitegrid")
    ax = sns.barplot(x=feature_imp, y=feature_imp.index, palette='Blues_d')
    ax.set_xlabel('Feature Importance Score', fontsize=14)
    ax.set_ylabel('Features', fontsize=14)
    ax.set_title("Visualizing Important Features", fontsize=16)
    # Adjust the background transparency 
    ax.patch.set_alpha(0.7)
    ax.figure.patch.set_alpha(0.0)
    # Save the graph to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png', transparent=True, bbox_inches='tight')
    buffer.seek(0)
    # Encode the graph image as base64
    image_base64 = base64.b64encode(buffer.getvalue()).decode()

    return image_base64


if __name__ == '__main__':
    app.run(debug=True)
