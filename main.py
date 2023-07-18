import os
from flask import Flask, render_template, request, url_for, redirect, session
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import pandas as pd
import db_operations
from Prediction import RandomForestSupportModel

import logging
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'mysecretkey'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

try:
    connection = mysql.connector.connect(user='tamar', password='123456', host='127.0.0.1', port=3306,
                                         database='decision_project',
                                         auth_plugin='mysql_native_password')
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)

        # cursor.close()
        # connection.close()
        # print("MySQL connection is closed")
except Error as e:
    print("Error while connecting to MySQL", e)

try:
    model = RandomForestSupportModel.load("model.pkl")
except Error as e:
    print("Error while loading model", e)

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
            # app.logger.error("ADMIN Connected")
            return redirect(url_for('admin'))

        if result[0] == 'patient':
            session["username"] = username
            session["role"] = "user"
            # app.logger.error("REGULAR USER Connected")
            return redirect(url_for('home'))

        if result[0] == 'doctor':
            session["username"] = username
            session["role"] = "doctor"
            # app.logger.error("RESEARCH STUDENT Connected")
            return redirect(url_for('doctor'))

    return render_template('login.html')


@app.route('/admin', methods=["POST", "GET"])
def admin():
    if session["role"] != 'admin':
        return redirect(url_for('login'))

    try:
        feature_imp = model.clf.feature_importances_
        feature_name = model.clf.feature_names_in_
        sorted_list = sorted(list(zip(feature_imp, feature_name)), key=lambda x: x[0], reverse=True)
        sorted_feature_imp = [item[0] for item in sorted_list]
        sorted_feature_name = [item[1] for item in sorted_list]
        feature_imp_df = pd.Series(sorted_feature_imp,index=sorted_feature_name)

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

            elif role == 'doctor':
                # Add the doctor to the 'doctors' table
                full_name = request.form['full_name']
                db_operations.add_doctor(username, password, full_name)

                # Add the doctor to the 'users' table with role='doctor'
                db_operations.add_user(username, password, role)

            elif role == 'patient':
                # Add the patient to the 'patients' table
                full_name = request.form['full_name']
                gender = request.form['gender']
                contact_number = request.form['contact_number']
                doctor_id = request.form['doctor_id']
                db_operations.add_patient(username, password, full_name, gender, contact_number, doctor_id)

                # Add the patient to the 'users' table with role='patient'
                db_operations.add_user(username, password, role)

            return redirect(url_for('admin'))

        return render_template('admin.html', image_base64=image_base64, users = users)

    except Exception as e:
        return "Error while loading model: " + str(e)



@app.route('/doctor', methods=["POST", "GET"])
def doctor():
    if session["role"] != 'doctor':
        return redirect(url_for('login'))
    # Get the doctor's ID based on their username

    doctor_id = db_operations.get_doctor_id(session["username"])
    assigned_patients = db_operations.get_assigned_patients(doctor_id)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        gender = request.form['gender']
        contact_number = request.form['contact_number']
        # Add the patient to the 'patients' table
        patient_id = db_operations.add_patient(username, password, full_name, gender, contact_number, doctor_id)

        if patient_id is not None:
            # Add the patient to the 'users' table with role='patient'
            db_operations.add_user(username, password, 'patient')


        return redirect(url_for('doctor'))

    print(assigned_patients)
    return render_template('doctor.html',assigned_patients = assigned_patients)




@app.route('/symptoms', methods=["POST", "GET"])
def home():
    new_line = model.line.copy()
    new_line.columns = new_line.columns.astype(str)

    if request.method == 'POST':
        selected_symptoms = request.form.getlist('selected_symptoms')
        for symptom in selected_symptoms:
            index = symptoms.index(symptom)
            new_line.iloc[0][index] = 1
        prediction = model.make_prediction(new_line)

        # Retrieve the logged-in patient's information
        patient_id = db_operations.get_patient_id(session["username"])

        # Store the prediction and accuracy in the patient_predictions table
        query = "INSERT INTO patient_predictions (patient_id, symptoms, disease, accuracy) VALUES (%s, %s, %s, %s)"
        symptoms_str = ", ".join(selected_symptoms)
        prediction_disease = prediction[0]  # Extract the disease name
        prediction_accuracy = prediction[1]  # Extract the accuracy value
        values = (patient_id, symptoms_str, prediction_disease, prediction_accuracy)
        converted_values = tuple(str(value) for value in values)  # Convert values to strings
        cursor.execute(query, converted_values)
        connection.commit()


        return render_template('main.html', symptoms=symptoms, prediction=prediction)

    return render_template('main.html',symptoms=symptoms)


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




# def add_patient():
#     return

if __name__ == '__main__':
    app.run(debug=True)



# def scatter():
#     try:
#         # Generate the scatter plot
#         plt.figure(figsize=(10, 8))
#         sns.scatterplot(x=data['x'], y=data['y'], hue=data['prediction'], palette='Set1')
#         plt.xlabel('X-axis')
#         plt.ylabel('Y-axis')
#         plt.title('Scatter Plot')
#
#         # Save the plot to a BytesIO object
#         buffer = BytesIO()
#         plt.savefig(buffer, format='png', bbox_inches='tight')
#         buffer.seek(0)
#
#         # Encode the plot image as base64
#         scatter_image_base64 = base64.b64encode(buffer.getvalue()).decode()
#         return render_template('admin.html', scatter_image_base64=scatter_image_base64)
#     except Exception as e:
#         return "Error while generating scatter plot: " + str(e)
# #