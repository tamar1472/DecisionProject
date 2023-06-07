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