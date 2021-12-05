
#https://stackoverflow.com/questions/11994325/how-to-divide-flask-app-into-multiple-py-files
import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from py2neo import Graph
import logging
from utils import Environment

# Instantiate app environemnt.
environ = Environment("config.json")

# Configure logging.
logging.basicConfig(filename='./logs/app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# Ini app.
app = Flask(__name__)

# Cors.
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Configure MySQL.
app.config["SECRET_KEY"] = environ.get("secret_key")
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get("db_endpoint")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Configure mail service.
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = environ.get("mail_username")
app.config['MAIL_PASSWORD'] = environ.get("mail_password")
app.config['MAIL_USE_TLS'] = False 
app.config['MAIL_USE_TLS'] = True 
mail = Mail(app)

# Set selenium endpoint.
app.config["SELENIUM_ENDPOINT"] = environ.get("selenium_endpoint")

# Set ML Service Endpoint.
app.config["ML_SERVICE_ENDPOINT"] = environ.get("ml_service_endpoint")

# Configure other env variables.
app.config["TUTORIAL_API"] = "https://chainbreaker.community"#"https://drive.google.com/file/d/1yQItms-GYHFbJhnMNKNstfFL8B6MLqZX/view?usp=sharing"
app.config["DATA_VERSION"] = environ.get("data_version")
app.config["MAX_ADS_PER_REQUEST"] = environ.get("max_ads_per_request")

# Initialize neo4j service.
print("neo4juser: ", environ.get("neo4j_user"))
graph = Graph(environ.get("neo4j_endpoint"), 
              user = environ.get("neo4j_user"),
              password = environ.get("neo4j_password"))

# Resources.
def get_resource_as_string(name, charset='utf-8'):
    with app.open_resource(name) as f:
        return f.read().decode(charset)
app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string

# Main page.
@app.route('/')
def root():
    """
    Return the frontend of the application.
    """
    return app.send_static_file('index.html')

@app.route("/api/status", methods = ["GET"])
def status():
    """
    ChainBreaker IBM Stauts
    """
    return jsonify({'status' : 200})

# Import routes.
import views

if __name__ == '__main__':
    port = int(8000)
    app.run(host='0.0.0.0', port=port, debug=True)