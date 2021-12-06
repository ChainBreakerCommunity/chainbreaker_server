
from flask import Flask, request, jsonify, make_response, render_template
from flask.helpers import send_file
from sqlalchemy.sql.expression import select
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
#from sqlalchemy import create_engine
import os
from templates import welcome, recover
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import random
import codecs
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Session, backref, column_property, relation
from sqlalchemy import or_, and_, func
import json
import requests
import time
import geolocation 
import folium
import hashlib

from py2neo import Graph
import neo4j_utils

import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

with open("config.json") as json_file: 
    data = json.load(json_file)

app = Flask(__name__, static_url_path='')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type' # Set headers.

def get_resource_as_string(name, charset='utf-8'):
    with app.open_resource(name) as f:
        return f.read().decode(charset)
app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string

# MySQL Service.
app.config["SECRET_KEY"] = data["secret_key"]
app.config['SQLALCHEMY_DATABASE_URI'] = data["db_endpoint"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Free Trial.
app.config["FREE_TRIAL"] = data["free_trial"]

# Email Service.
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = data["mail_username"]
app.config['MAIL_PASSWORD'] = data["mail_password"]
app.config['MAIL_USE_SSL'] = False 
app.config['MAIL_USE_TLS'] = True 
mail = Mail(app)

app.config["TUTORIAL_API"] = "https://chainbreaker.community"#"https://drive.google.com/file/d/1yQItms-GYHFbJhnMNKNstfFL8B6MLqZX/view?usp=sharing"
app.config["DATA_VERSION"] = data["data_version"]
app.config["MAX_ADS_PER_REQUEST"] = data["max_ads_per_request"]
#app.config["GEOLOCATION_SERVICE_ENDPOINT"] = data["geolocation_service_endpoint"]
app.config["ML_SERVICE_ENDPOINT"] = data["ml_service_endpoint"]

# Neo4j service.
neo4j_enable = (data["neo4j_enable"] == "true")
graph = None
if neo4j_enable:
    graph = Graph(data["neo4j_endpoint"], user = data["neo4j_user"], password = data["neo4j_password"])

# Scrap enable.
selenium_enable = (data["selenium_enable"] == "true")

# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', int(data["port"])))

def getsize(obj):
    """
    Get size of object.
    """
    from types import ModuleType, FunctionType
    from gc import get_referents
    import sys

    BLACKLIST = type, ModuleType, FunctionType
    """sum size of object & members."""
    if isinstance(obj, BLACKLIST):
        raise TypeError('getsize() does not take argument of type: '+ str(type(obj)))
    seen_ids = set()
    size = 0
    objects = [obj]
    while objects:
        need_referents = []
        for obj in objects:
            if not isinstance(obj, BLACKLIST) and id(obj) not in seen_ids:
                seen_ids.add(id(obj))
                size += sys.getsizeof(obj)
                need_referents.append(obj)
        objects = get_referents(*need_referents)
    return size

def textToHash(text):
    hash_function = hashlib.sha256()
    x = bytes(str(text), "utf-8")
    hash_function.update(x)
    hash = hash_function.hexdigest()
    return hash

def format_ads_reduced_to_json(ads):
    """
    Format reduced version of ads data to json.
    """
    output = list()
    for ad in ads: 
        ad_data = {}

        # Ad data.
        ad_data["id_ad"] = ad.id_ad
        ad_data["language"] = ad.language
        ad_data["title"] = ad.title
        ad_data["text"] = ad.text 
        ad_data["category"] = ad.category 

        # Location data.
        ad_data["country"] = ad.country
        ad_data["city"] = ad.city

        # Website.
        ad_data["external_website"] = ad.external_website
        output.append(ad_data)

    return output

def format_ads_to_json(ads, secure = False):
    """
    Format Ads Data to json.
    """
    last_id = 0
    output = list()
    for ad in ads: 
        ad_data = {}

        # Ad data.
        ad_data["id_ad"] = ad.id_ad
        ad_data["data_version"] = ad.data_version
        ad_data["author"] = ad.author
        ad_data["language"] = ad.language
        ad_data["link"] = textToHash(ad.link) if (not secure and ad.link != None) else ad.link
        ad_data["id_page"] = ad.id_page
        ad_data["title"] = ad.title
        ad_data["text"] = ad.text 
        ad_data["category"] = ad.category 
        ad_data["first_post_date"] = ad.first_post_date
        ad_data["extract_date"] = ad.extract_date 
        ad_data["website"] = ad.website 

        # Phone data.
        ad_data["phone"] = textToHash(ad.phone) if (not secure and ad.phone != None) else ad.phone

        # Location data.
        ad_data["country"] = ad.country
        ad_data["region"] = ad.region
        ad_data["city"] = ad.city
        ad_data["place"] = ad.place
        ad_data["latitude"] = ad.latitude
        ad_data["longitude"] = ad.longitude
        ad_data["zoom"] = ad.zoom
        ad_data["email"] = textToHash(ad.email) if (not secure and ad.email != None) else ad.email
        ad_data["verified_ad"] = ad.verified_ad
        ad_data["prepayment"] = ad.prepayment 
        ad_data["promoted_ad"] = ad.promoted_ad 
        ad_data["external_website"] = textToHash(ad.external_website) if (not secure and ad.external_website != None) else ad.external_website
        ad_data["reviews_website"] = textToHash(ad.reviews_website) if (not secure and ad.reviews_website != None) else ad.reviews_website
        ad_data["nationality"] = ad.nationality
        ad_data["age"] = ad.age
        ad_data["score_risk"] = ad.score_risk

        last_id = ad.id_ad
        output.append(ad_data)

    return output, last_id

def register_user(data):

    password_length = 5
    possible_characters = "abcdefghijklmnopqrstuvwxyz1234567890"
    random_character_list = [random.choice(possible_characters) for i in range(password_length)]
    random_password = "".join(random_character_list)

    data = request.values
    name = data["name"]
    email = data["email"]
    permission = "reader"
    link = app.config["TUTORIAL_API"]

    hashed_password = generate_password_hash(random_password, method='sha256')
    new_user = User(name = name,
                    email = email, 
                    password = hashed_password, 
                    permission = permission)
    db.session.add(new_user)
    db.session.commit()

    with app.app_context():
        with mail.connect() as conn:
            msg = Message(subject = "Welcome to ChainBreaker Community!", 
                        recipients = [data["email"]], 
                        sender = app.config['MAIL_USERNAME'])
            #render_template("welcome.html")
            template = welcome(name, email[0: email.find("@")] + " (" + email[email.find("@"):  ] + ")", random_password, link)
            msg.html = template
            msg.attach("chain-white.png", "image/png", open("static/images/chain-white.png", "rb").read(), disposition="inline", headers=[["Content-ID",'<chainlogo>'],]) 
            msg.attach("hero-img.png", "image/png", open("static/images/hero-img.png", "rb").read(), disposition="inline", headers=[["Content-ID",'<communitylogo>'],])
            conn.send(msg)
    return True

@app.route('/')
def root():
    """
    Return the frontend of the application.
    """
    return app.send_static_file('info.html')


"""
Define User Model
"""
class User(db.Model):
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
        self.available_phone_calls = app.config["FREE_TRIAL"]


"""
Define Ad Model
"""
class Ad(db.Model):
    __tablename__ = "ad"
    id_ad = db.Column(db.Integer, primary_key=True)
    data_version = db.Column(db.Integer)
    author = db.Column(db.String(30))
    language = db.Column(db.String(20))
    link = db.Column(db.String(100))
    id_page = db.Column(db.Integer)
    title = db.Column(db.String(100))
    text = db.Column(db.String(10000))
    category = db.Column(db.String(20))
    first_post_date = db.Column(db.DateTime(10))
    extract_date = db.Column(db.DateTime(10))
    website = db.Column(db.String(20))

    phone = db.Column(db.Integer)

    country = db.Column(db.String(30))
    region = db.Column(db.String(30))
    city = db.Column(db.String(30))
    place = db.Column(db.String(30))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    zoom = db.Column(db.Integer)

    email = db.Column(db.String(100))
    verified_ad = db.Column(db.Boolean())
    prepayment = db.Column(db.Boolean())
    promoted_ad = db.Column(db.Boolean())
    external_website = db.Column(db.String(100))
    reviews_website = db.Column(db.String(100))

    nationality = db.Column(db.String(100))
    age = db.Column(db.Integer)

    score_risk = db.Column(db.Float)

    def __init__(self, data_version, author, language, link, id_page, title, text, 
                category, first_post_date, extract_date, website, phone, country, region, 
                city, place, latitude, longitude, zoom, email = None, 
                verified_ad = None, prepayment = None, promoted_ad = None, external_website = None,
                reviews_website = None, nationality = None, age = None, score_risk = None):

        self.data_version = data_version
        self.author = author
        self.language = language
        self.link = link
        self.id_page = id_page
        self.title = title
        self.text = text
        self.category = category
        self.first_post_date = first_post_date
        self.extract_date = extract_date
        self.website = website

        self.phone = phone

        self.country = country
        self.region = region
        self.city = city
        self.place = place
        self.latitude = latitude
        self.longitude = longitude
        self.zoom = zoom

        self.email = email
        self.verified_ad = verified_ad
        self.prepayment = prepayment
        self.promoted_ad = promoted_ad
        self.external_website = external_website
        self.reviews_website = reviews_website

        self.nationality = nationality
        self.age = age
        self.score_risk = score_risk

"""
Define Comment Model
"""
class Comment(db.Model):
    __tablename__ = "comment"
    id_comment = db.Column(db.Integer, primary_key = True)
    id_ad = db.Column(db.Integer)
    comment = db.Column(db.String(1000))

    def __init__(self, id_ad, comment):
        self.id_ad = id_ad
        self.comment = comment

"""
Define Glossary Model
"""
class Glossary(db.Model):
    __tablename__ = "glossary"
    id_term = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(20))
    term = db.Column(db.String(30))
    definition = db.Column(db.String(1000))

"""
Define Keyword Model
"""
class Keyword(db.Model):
    __tablename__ = "keyword"
    id_keyword = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(20))
    keyword = db.Column(db.String(30))
    english_translation = db.Column(db.String(30))
    meaning = db.Column(db.String(1000))
    age_flag = db.Column(db.Boolean())
    trafficking_flag = db.Column(db.Boolean())
    movement_flag = db.Column(db.Boolean())

"""
Token required middleware.
"""
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401
        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(email=data['email']).first()
            current_user.api_calls += 1
            current_user.last_api_call_date = datetime.datetime.now()
            db.session.commit()
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated


"""
ChainBreaker IBM Stauts
"""
@app.route("/api/status", methods = ["GET"])
def status():
    return jsonify({'status' : 200})

################################
## ChainBreaker API Endpoints ##
################################

"""
This functions recieves an email and a password
and returns an authorization token.
"""
@app.route('/api/user/login', methods = ["POST"])
def login():
    auth = request.get_json()
    if auth == None: 
       auth = request.values

    #print((not auth))
    #print((not auth["email"]))
    #print((not auth["password"]))
    #print((not auth["expiration"]), auth["expiration"])

    if not auth or not auth["email"] or not auth["password"] or not auth["expiration"]:
        print("bad requests...")
        return make_response('Bad request', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
    user = User.query.filter_by(email=auth["email"]).first()
    if not user:
        print("user does not exist")
        return make_response('User does not exist', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
    if check_password_hash(user.password, auth["password"]):
        minutes = max(int(auth["expiration"]), 999999)
        token = jwt.encode({'id_user' : user.id_user, "email": user.email, "permission": user.permission, "expiresIn": minutes}, app.config['SECRET_KEY'], algorithm = "HS256")
        return jsonify({'name': user.name, 'email': user.email, 'permission': user.permission, 'token' : token}), 200
    print("could not verified")
    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

"""
This functions allows users to create an account.
"""
@app.route('/api/user/register', methods=['PUT'])
def register():
    res = register_user(data)
    if res:
        return jsonify({'message' : 'New user created!'}), 200
    else: 
        return jsonify({'message' : 'There has been an error.'}), 404
    
"""
This functions allows administrators to create new users.
"""
@app.route('/api/user/create_user', methods=['PUT'])
@token_required
def create_user(current_user):
    if not current_user.permission == "admin":
        return jsonify({'message' : "You don't have the required permissions to execute this function!"})
    res = register_user(data)
    if res:
        return jsonify({'message' : 'New user created!'}), 200
    else: 
        return jsonify({'message' : 'There has been an error.'}), 404

"""
This function allows users to change their password.
"""
@app.route("/api/user/change_password", methods=["PUT"])
@token_required
def change_password(current_user):
    data = request.values
    if data["recover_password"] == "False":
        if check_password_hash(current_user.password, data["old_password"]):
            hashed_password = generate_password_hash(data['new_password'], method='sha256')
            current_user.password = hashed_password
            db.session.commit()
            return jsonify({'message' : 'Password updated!'}), 200
    else: 
        hashed_password = generate_password_hash(data['new_password'], method='sha256')
        current_user.password = hashed_password
        db.session.commit()
        return jsonify({'message' : 'Password changed!'}), 200
    return jsonify({'message' : 'Password could not be updated!'}), 400

"""
This functions allows administrators to create new users.
"""
@app.route('/api/user/recover_password', methods=['POST'])
def recover_password():
    data = request.values
    email = data["email"]
    link = app.config["TUTORIAL_API"]
    user = User.query.filter_by(email = email).first()
    token = jwt.encode({'id_user' : user.id_user, "email": user.email, "permission": user.permission, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes = 10)}, app.config['SECRET_KEY'], algorithm = "HS256")

    with app.app_context():
        with mail.connect() as conn:
            msg = Message(subject = "Chainbreaker Password Recovery", 
                          recipients = [data["email"]], 
                          sender = app.config['MAIL_USERNAME'])
            template = recover(user.name, email[0: email.find("@")] + " (" + email[email.find("@"): ] + ")", token, link)
            msg.html = template
            msg.attach("chain-white.png", "image/png", open("static/images/chain-white.png", "rb").read(), disposition="inline", headers=[["Content-ID",'<chainlogo>'],]) 
            msg.attach("why-us.png", "image/png", open("static/images/why-us.png", "rb").read(), disposition="inline", headers=[["Content-ID",'<communitylogo>'],])
            conn.send(msg)

    return jsonify({'message' : 'We have sent you a recovery e-mail to' + email + '! You have 10 minutes to change your password.'})

"""
This functions allows users to get data from ChainBreaker Database.
# https://flask-sqlalchemy.palletsprojects.com/en/2.x/models/
"""
@app.route('/api/data/get_sexual_ads', methods=['POST', "GET"])
@token_required
def get_sexual_ads(current_user):
    SECURE_ROLES = ["client", "researcher", "admin"]
    secure = (current_user.permission in SECURE_ROLES)

    # Some documentation: 
    # - https://stackoverflow.com/questions/18227100/sqlalchemy-subquery-in-fplease%20pass%20a%20select()%20construct%20explicitlyom-clause-without-join

    # Get data from requests.
    data = request.values
    EXCLUDE_FILTERS = ["start_date", "end_date", "from_id"]

    # Filters by: language, website, data_version
    filtered_args = {k: v for k, v in data.items() if v != "" and k not in EXCLUDE_FILTERS} 
    #print("filter keys: ", filtered_args.keys())
    filters = [getattr(Ad, attribute) == value for attribute, value in filtered_args.items()]

    # Dates filters.
    start_date = data["start_date"]#datetime.datetime.strptime(data["start_date"], "%Y-%m-%d") 
    end_date = data["end_date"]#datetime.datetime.strptime(data["end_date"], "%Y-%m-%d")
    from_id = int(request.args.get("from_id"))

    # Get ids of ads inside the dates range.
    if neo4j_enable: 
        dates_subquery = neo4j_utils.get_ads_inside_dates(graph, start_date, end_date)
    else:
        start_date = datetime.datetime.strptime(data["start_date"], "%Y-%m-%d") 
        end_date = datetime.datetime.strptime(data["end_date"], "%Y-%m-%d")
        subquery = db.session.query(Ad.id_ad) \
            .filter(and_(Ad.first_post_date >= start_date, Ad.first_post_date <= end_date)) \
            .all()
        dates_subquery = list()
        for id in subquery:
            dates_subquery.append(id[0])

    total_results = db.session.query(Ad.id_ad) \
        .filter(*filters) \
        .filter(Ad.id_ad.in_(dates_subquery)) \
        .count()
        
    ads = db.session.query(Ad) \
        .filter(Ad.id_ad > from_id) \
        .filter(*filters) \
        .filter(Ad.id_ad.in_(dates_subquery)) \
        .limit(app.config["MAX_ADS_PER_REQUEST"]) \
        .all()

    if len(ads) == 0:
        return jsonify({"message": "No results were found for your search"}), 401
    else:
        output, last_id = format_ads_to_json(ads, secure = secure)
        #print("Request memory size: ", getsize(output), " bytes.")
        return jsonify({"total_results": total_results, "last_id":  last_id, "ads": output}), 200
    
"""
This functions allows users to get specific data from ChainBreaker Database.
SECURE ENDPOINT.
"""
@app.route('/api/data/get_sexual_ads_by_id', methods=['POST', "GET"])
@token_required
def get_sexual_ads_by_id(current_user):
    ALLOWED_ROLES = ["client", "researcher", "admin"]
    if current_user.permission not in ALLOWED_ROLES:
        return jsonify({'message' : "You don't have the required permissions to execute this function!"})

    data = request.values
    reduced_version = int(data["reduced_version"])
    ads_ids = data.getlist("ads_ids")

    ids_filter = list()
    for id in ads_ids: 
        ids_filter.append(int(id))

    if reduced_version == 0:
        ads = db.session.query(Ad) \
            .filter(Ad.id_ad.in_(ids_filter)) \
            .all()
        output, last_id = format_ads_to_json(ads, secure = True)
    else:
        ads = db.session.query(Ad.id_ad, Ad.language, Ad.title, Ad.text, Ad.category, Ad.country, Ad.city, Ad.external_website) \
            .filter(Ad.id_ad.in_(ids_filter)) \
            .all()
        output = format_ads_reduced_to_json(ads)

    return jsonify({"ads": output}), 200

"""
This functions allows users to get the ChainBreaker Human Trafficking Glossary.
"""
@app.route('/api/data/get_glossary', methods=['POST', "GET"])
@token_required
def get_glossary(current_user):
    data = request.values
    domain = data["domain"]
    if domain != "":
        glossary = Glossary.query.filter_by(domain=domain).all()
    else: 
        glossary = Glossary.query.all()

    output = list()
    for term in glossary:
        term_data = {}
        term_data["id_term"] = term.id_term
        term_data["domain"] = term.domain 
        term_data["term"] = term.term 
        term_data["definition"] = term.definition 
        output.append(term_data)
    return jsonify({"glossary": output}), 200

"""
This functions allows users to get the ChainBreaker Human Trafficking Keywords.
"""
@app.route('/api/data/get_keywords', methods=['POST', "GET"])
@token_required
def get_keywords(current_user):
    data = request.values
    language = data["language"]
    if language != "":
        keywords = Keyword.query.filter_by(language = language).all()
    else: 
        keywords = Keyword.query.all()

    output = list()
    for keyword in keywords:
        keyword_data = {}
        keyword_data["id_keyword"] = keyword.id_keyword 
        keyword_data["language"] = keyword.language 
        keyword_data["keyword"] = keyword.keyword
        keyword_data["english_translation"] = keyword.english_translation 
        keyword_data["meaning"] = keyword.meaning 
        keyword_data["age_flag"] = keyword.age_flag 
        keyword_data["trafficking_flag"] = keyword.trafficking_flag
        keyword_data["movement_flag"] = keyword.movement_flag 
        output.append(keyword_data)
    return jsonify({"keywords": output}), 200

"""
Check if phone is in database.
"""
@app.route("/api/data/search_phone", methods = ["POST", "GET"])
@token_required
def search_phone(current_user):
    SECURE_ROLES = ["client", "researcher", "admin"]
    secure = (current_user.permission in SECURE_ROLES)
    reader = (current_user.permission == "reader")
    current_user.phone_search += 1
    db.session.commit()
    if reader: 
        if current_user.available_phone_calls >= 1:
            current_user.available_phone_calls -= 1
            db.session.commit()
        else: 
            return jsonify({"message": "You have exceeded the free trail API calls. If you want to keep using this service, please contact us to chainbreakerinfo@gmail.com"}), 404
    data = request.values
    phone = data["phone"]
    ads = Ad.query.filter_by(phone = phone).all()
    if len(ads) > 0:
        current_user.successful_phone_search += 1
        db.session.commit()
        output, last_id = format_ads_to_json(ads, secure = secure)
        return jsonify({"ads": output}), 200
    else:
        return jsonify({"message": "No results were found for your search"}), 404

"""
Get risk score of cellphone.
"""
@app.route("/api/data/get_phone_score_risk", methods = ["POST", "GET"])
@token_required
def get_phone_score_risk(current_user):
    ALLOWED_ROLES = ["client", "researcher", "admin"]
    if current_user.permission not in ALLOWED_ROLES:
        return jsonify({'message' : "You don't have the required permissions to execute this function!"})

    data = request.values
    phone = int(data["phone"])
    first_ad = db.session.query(Ad) \
        .filter(Ad.phone == phone) \
        .first()

    if first_ad == None:
        return jsonify({"message": "Phone not in database."}), 404
    else:
        score_risk = first_ad.score_risk
        #avg = db.session.query(func.avg(Ad.score_risk)) \
        #    .filter(Ad.country == "colombia").first()[0]
        #std = db.session.query(func.std(Ad.score_risk)) \
        #    .filter(Ad.country == "colombia").first()[0]
        #standard_score = (score_risk - avg) / std
        #def sigmoid_function(x):
        #    import math
        #    return 1 / (1 + math.exp(-x))
        #sigmoid_value = round(sigmoid_function(standard_score), 4)
        return jsonify({"score_risk": score_risk}), 200

"""
Counts the number of nodes per label in neo4j
"""
@app.route("/api/graph/get_labels_count", methods = ["GET"])
def get_labels_count():
    if not neo4j_enable: 
        return jsonify({"message": "Sorry. Service not available at the moment."}), 400
    data = neo4j_utils.get_labels_count(graph)
    return jsonify({"labels_count": data})

"""
Returns the communities identified using community detection algorithm
"""
@app.route("/api/graph/get_communities", methods = ["GET", "POST"])
@token_required
def get_communities(current_user):
    if not neo4j_enable: 
        return jsonify({"message": "Sorry. Service not available at the moment."}), 400
    ALLOWED_ROLES = ["super_reader", "researcher", "admin"]
    if current_user.permission not in ALLOWED_ROLES:
        return jsonify({'message' : "You don't have the required permissions to execute this function!"})
    data = request.values
    country = data["country"] if data["country"] != "" else None
    communities = neo4j_utils.get_communities(graph, country)
    return jsonify({"communities": communities})

"""
Returns the community of an specific advertisement.
"""
@app.route("/api/graph/get_community_ads", methods = ["GET", "POST"])
def get_community_ads():
    if not neo4j_enable: 
        return jsonify({"message": "Sorry. Service not available at the moment."}), 400
    data = request.values
    id_community = int(data["id_community"])
    communities = neo4j_utils.get_communities(graph, country = None)
    return jsonify({"ads_ids": communities[str(id_community - 1)]})

#####################################
##         Render Websites         ##
#####################################
@app.route("/api/data/get_locations_map", methods = ["GET"])
def get_locations_map():
    #Great Folium Tutorial https://www.youtube.com/watch?v=t9Ed5QyO7qY
    start_coords = (4.581440, -73.397964)
    folium_map = folium.Map(location=start_coords, zoom_start=3)

    zoom_filter = 0
    ads = db.session.query(Ad) \
        .filter(Ad.zoom >= zoom_filter) \
        .all()

    from random import shuffle
    data = list()
    shuffle(ads)
    counter = 0
    for ad in ads: 
        counter += 1
        data.append([ad.latitude, ad.longitude])
        """
        popup = "Ad Id: " + str(ad.id_ad) + ". Location: " + ad.city + " "
        if ad.place != None:
            popup += ad.place
        folium.Marker(
            [ad.latitude, ad.longitude], 
            popup = popup
        ).add_to(folium_map)
        if counter >= app.config["MAX_ADS_PER_REQUEST"]:
            break
        """
    #folium.PolyLine(data, weight = 1, color = "blue", opacity = 0.6).add_to(folium_map)
    from folium.plugins import HeatMap, Draw
    draw = Draw(export = True)
    draw.add_to(folium_map)
    HeatMap(data).add_to(folium.FeatureGroup(name="Heat Map")).add_to(folium_map)
    folium.LayerControl().add_to(folium_map)
    print("Request memory size: ", getsize(folium_map), " bytes.")
    #folium_map._repr_html_()
    folium_map.save(outfile = "folium_map.html")
    return jsonify({"message": "ok"})

@app.route("/template")
def template():
    return render_template("folium_map.html")

#####################################
## ChainBreaker Scrapers Endpoints ##
#####################################
"""
Get soup given an url.
"""
@app.route("/api/scraper/get_soup", methods = ["POST", "GET"])
@token_required
def get_soup(current_user):

    ALLOWED_ROLES = ["scraper", "researcher", "admin"]
    if current_user.permission not in ALLOWED_ROLES:
        return jsonify({'message' : "You don't have the required permissions to execute this function!"})
    data = request.values
    url = data["url"]
    return jsonify({"message": "Sorry. Service not available at the moment."}), 400

"""
Get if ad exists.
"""
@app.route("/api/scraper/does_ad_exists", methods = ["POST", "GET"])
@token_required
def does_ad_exists(current_user):

    ALLOWED_ROLES = ["scraper", "reseacher", "admin"]
    if current_user.permission not in ALLOWED_ROLES:
        return jsonify({'message' : "You don't have the required permissions to execute this function!"})

    WEBSITE_WITH_ADS_REPETEAD = ["mileroticos"]

    does_ad_exist = 1
    data = request.values
    id_page = str(data["id_page"])
    website = data["website"]
    country = data["country"]
    ads = Ad.query.filter_by(website = website) \
          .filter_by(id_page = id_page) \
          .filter_by(country = country) \
          .first()

    if ads == None:
        does_ad_exist = 0
    else: 
        if website in WEBSITE_WITH_ADS_REPETEAD and neo4j_enable:
            id_ad = int(ads.id_ad)
            neo4j_utils.create_new_date_for_ad(graph, id_ad)

    return jsonify({"does_ad_exist": does_ad_exist})

"""
This function allow writers to add new advertisments to ChainBreaker DB.
"""
@app.route('/api/scraper/insert_ad', methods=['POST', "GET"])
@token_required
def insert_ad(current_user):


    ALLOWED_ROLES = ["scraper", "researcher", "admin"]
    if current_user.permission not in ALLOWED_ROLES:
        return jsonify({'message' : "You don't have the required permissions to execute this function!"})
    data = request.values

    #print("Data keys: ")
    #print(data.keys())

    # Ad data.
    data_version = app.config["DATA_VERSION"]
    author = data["author"]
    language = data["language"]
    link = data["link"]
    id_page = data["id_page"]
    title = data["title"]
    text = data["text"]
    category = data["category"] 
    first_post_date = data["first_post_date"]
    extract_date = data["extract_date"]
    website = data["website"]

    # Phone.
    phone = data["phone"]

    # Location.
    country = data["country"]
    region = data["region"]
    city = data["city"] if data["city"] != "" else None
    place = data["place"] if data["place"] != "" else None
    latitude = float(data["latitude"]) if data["latitude"] != "" else 0
    longitude = float(data["longitude"]) if data["longitude"] != "" else 0
    zoom = 0

    # Optional parameters.
    nationality = data["nationality"] if data["nationality"] != "" else None
    age = int(data["age"]) if data["age"] != "" else None

    # Get GPS location.
    if latitude == 0 and longitude == 0 and selenium_enable:
        latitude, longitude, zoom = geolocation.get_geolocation(country, region, city, place)

    # Optional fields.
    email = data["email"] if data["email"] != "" else None
    verified_ad = int(data["verified_ad"]) if data["verified_ad"] != "" else None
    prepayment = int(data["prepayment"]) if data["prepayment"] != "" else None
    promoted_ad = int(data["promoted_ad"]) if data["promoted_ad"] != "" else None
    external_website = data["external_website"] if data["external_website"] != "" else None
    reviews_website = data["reviews_website"] if data["reviews_website"] != "" else None

    # Risk Score.
    risk_score = None

    # Create Ad in MySQL.
    new_ad = Ad(data_version, author, language, link, id_page, title, text, category, first_post_date,
                extract_date, website, phone, country, region, city, place, latitude, longitude, zoom, 
                email, verified_ad, prepayment, promoted_ad, external_website, reviews_website, nationality, age, 
                risk_score)

    # Add to DB.
    db.session.add(new_ad)
    db.session.commit()

    # Get last Ad id.
    id_ad = int(Ad.query.filter_by(id_page = id_page).first().id_ad)

    # Create Ad in Neo4j and correspoding relationships.
    if neo4j_enable:
        neo4j_data = data.to_dict(flat = True)
        neo4j_data["id_ad"] = id_ad
        neo4j_utils.create_ad(graph, neo4j_data)

    # Upload comments.
    comments = data.getlist("comments")
    for comment in comments: 
        new_comment = Comment(id_ad, comment)
        db.session.add(new_comment)

    return jsonify({"message": "Ad successfully uploaded!"}), 200
    
"""
This function recieves a phonumber and return different variables related with it.
"""
@app.route("/api/scraper/get_phone_info", methods = ["POST", "GET"])
@token_required
def get_phone_info(current_user):

    ALLOWED_ROLES = ["scraper", "researcher", "admin"]
    if current_user.permission not in ALLOWED_ROLES:
        return jsonify({'message' : "You don't have the required permissions to execute this function!"})
    return jsonify({"result": "Sorry. Service not available at the moment."}), 400

    data = request.values
    phone = data["phone"]

    times_searched, num_complaints, first_service_provider, trust, frequent_report = \
        [None, None, None, None, None]

    phone_data = {}
    phone_data["times_searched"] = times_searched
    phone_data["num_complaints"] = num_complaints
    phone_data["first_service_provider"] = first_service_provider
    phone_data["trust"] = trust
    phone_data["frequent_report"] = frequent_report

    return jsonify({'phone_data': phone_data})

#####################################
##    ChainBreaker ML Endpoints    ##
#####################################
"""
This function recieves an image and returns the coordinates where there are faces.
"""
@app.route("/api/machine_learning/get_image_faces", methods = ["POST", "GET"])
@token_required
def get_image_faces(current_user):
    #return requests.post(app.config["ML_SERVICE_ENDPOINT"], data = request.data)
    return jsonify({"message": "Service currently unavailable."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)