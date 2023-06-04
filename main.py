import os
from flask import Flask, render_template, request, url_for, redirect, session
import pandas as pd
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
        # app.logger.error("ADMIN Connected to MySQL Server")
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
def home():
    new_line = model.line.copy()
    new_line.columns = new_line.columns.astype(str)
    # symptoms_with_underscore = [symptom.lower().replace(' ', '_') for symptom in symptoms]
    # print(new_line)

    if request.method == 'POST':
        selected_symptoms = request.form.getlist('selected_symptoms')
        for symptom in selected_symptoms:
            index = symptoms.index(symptom)
            new_line.iloc[0][index] = 1
        # print(new_line)
        prediction = model.make_prediction(new_line)

        # print(model.line.columns)

        print(prediction)
        return render_template('main.html', symptoms=symptoms)

    else:
        return render_template('main.html',symptoms=symptoms)


    # TODO: check point from user


if __name__ == '__main__':
    app.run(debug=True)
