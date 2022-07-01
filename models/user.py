
from utils.db import db
import datetime
from dotenv import dotenv_values
config = dotenv_values(".env")

class User(db.Model):
    """
    Define User Model
    """
    __tablename__ = "user"
    id_user = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password = db.Column(db.String(100))
    permission = db.Column(db.String(10))
    registration_date = db.Column(db.DateTime(10))
    api_calls = db.Column(db.Integer)
    last_api_call_date = db.Column(db.DateTime(10))
    phone_search = db.Column(db.Integer)
    successful_phone_search = db.Column(db.Integer)
    available_phone_calls = db.Column(db.Integer)

    def __init__(self, name, email, password, permission):
        self.name = name
        self.email = email
        self.password = password
        self.permission = permission
        self.registration_date = datetime.datetime.now()
        self.api_calls = 0
        self.last_api_call_date = None
        self.phone_search = 0
        self.successful_phone_search = 0
        self.available_phone_calls = config["FREE_TRIAL"]