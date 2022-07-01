from flask import Flask, jsonify
from routes.data import data
from routes.user import user
from routes.scraper import scraper
from routes.graph import graph
import utils.configuration
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import logging

app = Flask(__name__)
app = utils.configuration.configure_app(app)
cors = CORS(app)
db = SQLAlchemy(app)
mail = Mail(app)

@app.route('/')
def root():
    return app.send_static_file('info.html')

@app.route("/status", methods = ["GET"])
def status():
    return jsonify({'status' : 200})

# Register routes.
app.register_blueprint(data, url_prefix = "/data")
app.register_blueprint(user, url_prefix = "/user")
app.register_blueprint(scraper, url_prefix = "/scraper")
app.register_blueprint(graph, url_prefix = "/graph")

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = app.config["PORT"], debug = True)