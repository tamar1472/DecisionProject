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

        if result[0] == 'regular user':
            session["username"] = username
            session["role"] = "regular user"
            # app.logger.error("REGULAR USER Connected")
            return redirect(url_for('home'))

        if result[0] == 'research student':
            session["username"] = username
            session["role"] = "research student"
            # app.logger.error("RESEARCH STUDENT Connected")
            return redirect(url_for('rs_panel'))

    return render_template('login.html')


@app.route('/admin', methods=["POST", "GET"])
def admin():
    if session["role"] != 'admin':
        return redirect(url_for('login'))
    try:
        accuracy, feature_imp = model.train_model()

        # Convert feature_imp to a DataFrame
        feature_imp_df = pd.DataFrame({'Feature': feature_imp})

        # Generate the graph
        image_base64 = generate_graph(feature_imp_df)

        return render_template('adminPanel.html', image_base64=image_base64)
    except Exception as e:
        return "Error while loading model: " + str(e)



@app.route('/RS_panel', methods=["POST", "GET"])
def rs_panel():
    if session["role"] != 'research student':
        return redirect(url_for('login'))

    return render_template('RS_panel.html')


@app.route('/symptoms', methods=["POST", "GET"])
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


def generate_graph(feature_imp_df):
    # Adjust the figure size and margins
    plt.figure(figsize=(12, 9))
    plt.subplots_adjust(left=0.25, right=0.75, top=0.9, bottom=0.1)

    # Generate the graph
    sns.set_style("whitegrid")
    ax = sns.barplot(x=feature_imp_df.index, y=feature_imp_df['Feature'], data=feature_imp_df, palette='Blues_d')
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

# def scatter():
#     try:
#         # Load the saved model
#         model = RandomForestSupportModel.load("model.pkl")
#
#         # Load the data for scatter plot
#         data = pd.read_csv("scatter_data.csv")
#
#         # Make predictions on the data
#         data['prediction'] = model.predict(data.drop('category', axis=1))
#
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
#         return render_template('adminPanel.html', scatter_image_base64=scatter_image_base64)
#     except Exception as e:
#         return "Error while generating scatter plot: " + str(e)
#

if __name__ == '__main__':
    app.run(debug=True)



