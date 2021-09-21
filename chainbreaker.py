from types import CoroutineType
from flask import Flask, request, jsonify, make_response, render_template
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

app = Flask(__name__, static_url_path='')
def get_resource_as_string(name, charset='utf-8'):
    with app.open_resource(name) as f:
        return f.read().decode(charset)
app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string

app.config['CORS_HEADERS'] = 'Content-Type' # Set headers.
app.config["SECRET_KEY"] = "u[NDYu>N:~)93-#u"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://reader:GaJ4a54RvaM94k4a@juanchobanano.com:3306/chainbreaker?charset=utf8mb4"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = "chainbreakerinfo@gmail.com"
app.config['MAIL_PASSWORD'] = "chain#6125"
app.config['MAIL_USE_TLS'] = False 
app.config['MAIL_USE_TLS'] = True 
mail = Mail(app)

app.config["TUTORIAL_API"] = "https://chainbreaker.community"#"https://drive.google.com/file/d/1yQItms-GYHFbJhnMNKNstfFL8B6MLqZX/view?usp=sharing"
app.config["DATA_VERSION"] = "2"
app.config["MAX_ADS_PER_REQUEST"] = 500
app.config["SHOP_AND_SERVICES_CATEGORIES"] = ["servicios-virtuales", "sex-shop"]
# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))

permission_level = {
    "reader": 1,
    "labeler": 2,
    "scraper": 3,
    "admin": 4
}

"""
Get size of object.
"""
def getsize(obj):
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

"""
Return the frontend of the application.
"""
@app.route('/')
def root():
    return app.send_static_file('index.html')

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

    def __init__(self, name, email, password, permission):
        self.name = name
        self.email = email
        self.password = password
        self.permission = permission


"""
Define GeoLocation Model
class GeoLocation(db.Model):
    __tablename__ = "geolocation"
    id_geolocation = id_ad = db.Column(db.Integer, primary_key=True)
    place_id = id_ad = db.Column(db.Integer)
    country = db.Column(db.String(30))
    country_code = db.Column(db.String(5))
    region = db.Column(db.String(30))
    state = db.Column(db.String(30))
    city = db.Column(db.String(30))
    district = db.Column(db.String(30))
    neighborhood = db.Column(db.String(30))
    address = db.Column(db.String(100))
    location_type = db.Column(db.String(20))
    street = db.Column(db.String(50))
    suburb = db.Column(db.String(50))
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    confidence = db.Column(db.Float)
"""

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

    whatsapp = db.Column(db.Integer)
    email = db.Column(db.String(100))
    verified_ad = db.Column(db.Boolean())
    prepayment = db.Column(db.Boolean())
    promoted_ad = db.Column(db.Boolean())
    external_website = db.Column(db.String(100))
    reviews_website = db.Column(db.String(100))

    def __init__(self, data_version, author, language, link, id_page, title, text, 
                category, first_post_date, extract_date, website, 
                whatsapp = None, email = None, verified_ad = None, prepayment = None, 
                promoted_ad = None, external_website = None, reviews_website = None):

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

        self.whatsapp = whatsapp
        self.email = email
        self.verified_ad = verified_ad
        self.prepayment = prepayment
        self.promoted_ad = promoted_ad
        self.external_website = external_website
        self.reviews_website = reviews_website

"""
Define Date Model
"""
class Date(db.Model): 
    __tablename__ = "date"
    id_date = db.Column(db.Integer, primary_key = True)
    id_ad = db.Column(db.Integer)
    date = db.Column(db.DateTime(10))

    def __init__(self, id_ad, date):
        self.id_ad = id_ad
        self.date = date


"""
Define Comment Model
"""
class Comment(db.Model):
    __tablename__ = "comment"
    id_comment = db.Column(db.Integer, primary_key = True)
    id_ad = db.Column(db.Integer)
    comment = db.Column(db.String(1000))

    #ad = relation(Ad, backref = "comments") 

    def __init__(self, id_ad, comment):
        self.id_ad = id_ad
        self.comment = comment

"""
Define Location Model
"""
class Location(db.Model):
    __tablename__ = "location"
    id_location = db.Column(db.Integer, primary_key=True)
    id_ad = db.Column(db.Integer)
    country = db.Column(db.String(30))
    region = db.Column(db.String(30))
    city = db.Column(db.String(30))
    place = db.Column(db.String(30))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    zoom = db.Column(db.Integer)

    #ad = relation(Ad, backref = "locations")

    def __init__(self, id_ad, country, region, city, place,
                 latitude, longitude, zoom):
        self.id_ad = id_ad
        self.country = country
        self.region = region
        self.city = city
        self.place = place
        self.latitude = latitude
        self.longitude = longitude
        self.zoom = zoom

"""
Define Phone Model
"""
class Phone(db.Model):
    __tablename__ = "phone"
    id_phone = db.Column(db.Integer, primary_key=True)
    id_ad = db.Column(db.Integer)
    phone = db.Column(db.Integer)
    times_searched = db.Column(db.Integer)
    num_complaints = db.Column(db.Integer)
    first_service_provider = db.Column(db.String(20))
    trust = db.Column(db.String(20))
    frequent_report = db.Column(db.String(20))
    processed = db.Column(db.Boolean)

    #ad = relation(Ad, backref = "phones")
    
    def __init__(self, id_ad, phone, times_searched, 
                num_complaints, first_service_provider, 
                trust, frequent_report, processed):
        self.id_ad = id_ad
        self.phone = phone 
        self.times_searched = times_searched
        self.num_complaints = num_complaints
        self.first_service_provider = first_service_provider
        self.trust = trust
        self.frequent_report = frequent_report
        self.processed = processed

"""
Define Feature Model
"""
class Feature(db.Model):
    __tablename__ = "feature"
    id_feature = db.Column(db.Integer, primary_key=True)
    id_ad = db.Column(db.Integer)
    age = db.Column(db.Integer)
    nationality = db.Column(db.String(20))
    ethnicity = db.Column(db.String(20))
    availability = db.Column(db.String(20))
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    hair_color = db.Column(db.String(20))
    eyes_color = db.Column(db.String(20))
    price = db.Column(db.Float)

    #ad = relation(Ad, backref = "features")

    def __init__(self, id_ad, age, nationality, ethnicity, 
                availability, weight, height, hair_color, eyes_color, 
                price):
        self.id_ad = id_ad
        self.age = age
        self.nationality = nationality
        self.ethnicity = ethnicity
        self.availability = availability
        self.weight = weight
        self.height = height
        self.hair_color = hair_color
        self.eyes_color = eyes_color
        self.price = price

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
@app.route('/api/user/login', methods = ["POST", "GET"])
def login():
    auth = request.values
    if not auth or not auth["email"] or not auth["password"] or not auth["expiration"]:
        return make_response('Bad request', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
    user = User.query.filter_by(email=auth["email"]).first()
    if not user:
        return make_response('User does not exist', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
    if check_password_hash(user.password, auth["password"]):
        minutes = max(int(auth["expiration"]), 999999)
        token = jwt.encode({'id_user' : user.id_user, "email": user.email, "permission": user.permission, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes = minutes)}, app.config['SECRET_KEY'], algorithm = "HS256")
        return jsonify({'name': user.name, 'email': user.email, 'permission': user.permission, 'token' : token}), 200
    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

"""
This functions allows administrators to create new users.
"""
@app.route('/api/user/create_user', methods=['PUT'])
@token_required
def create_user(current_user):
    if not current_user.permission == "admin":
        return jsonify({'message' : 'Cannot perform that function!'})

    password_length = 5
    possible_characters = "abcdefghijklmnopqrstuvwxyz1234567890"
    random_character_list = [random.choice(possible_characters) for i in range(password_length)]
    random_password = "".join(random_character_list)

    data = request.values
    name = data["name"]
    email = data["email"]
    permission = data["permission"]
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

    return jsonify({'message' : 'New user created!'})

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
    # Some documentation: 
    # - https://stackoverflow.com/questions/18227100/sqlalchemy-subquery-in-fplease%20pass%20a%20select()%20construct%20explicitlyom-clause-without-join
    
    level = permission_level[current_user.permission]
    if level == 0:
        return jsonify({'message' : 'Cannot perform that function!'})
    
    data = request.values
    EXCLUDE_FILTERS = ["start_date", "end_date", "from_id", "shop_and_services"]
    # language, website, data_version
    filtered_args = {k: v for k, v in data.items() if v != "" and k not in EXCLUDE_FILTERS} 
    filters = [getattr(Ad, attribute) == value for attribute, value in filtered_args.items()]

    shop_and_services = int(data["shop_and_services"])
    if shop_and_services == 1: 
        shop_filters = [Ad.category == value for value in app.config["SHOP_AND_SERVICES_CATEGORIES"]]
        filters = filters + shop_filters

    start_date = datetime.datetime.strptime(data["start_date"], "%Y-%m-%d") 
    end_date =  datetime.datetime.strptime(data["end_date"], "%Y-%m-%d")
    from_id = int(request.args.get("from_id"))

    dates_subquery = db.session.query(Date.id_ad) \
        .filter(and_(Date.date >= start_date, Date.date <= end_date)) \
        .group_by(Date.id_ad).having(func.count(Date.id_date) >= 1) \
        .scalar_subquery()
        
    total_results = db.session.query(Ad.id_ad, Phone.id_ad, Location.id_ad) \
        .filter(and_(*filters)) \
        .filter(Ad.id_ad.in_(dates_subquery)) \
        .filter(Ad.id_ad == Phone.id_ad) \
        .filter(Ad.id_ad == Location.id_ad) \
        .count()

    ads = db.session.query(Ad, Phone, Location) \
        .filter(Ad.id_ad > from_id) \
        .filter(and_(*filters)) \
        .filter(Ad.id_ad.in_(dates_subquery)) \
        .filter(Ad.id_ad == Phone.id_ad) \
        .filter(Ad.id_ad == Location.id_ad) \
        .limit(app.config["MAX_ADS_PER_REQUEST"]) \
        .all()

    if len(ads) == 0:
        return jsonify({"message": "No results were found for your search"}), 401
    else:
        output = list()
        for ad, phone, location in ads: 
            ad_data = {}

            # Ad data.
            ad_data["id_ad"] = ad.id_ad
            ad_data["data_version"] = ad.data_version
            ad_data["author"] = ad.author
            ad_data["language"] = ad.language
            ad_data["link"] = ad.link
            ad_data["id_page"] = ad.id_page
            ad_data["title"] = ad.title
            ad_data["text"] = ad.text 
            ad_data["category"] = ad.category 
            ad_data["first_post_date"] = ad.first_post_date
            ad_data["extract_date"] = ad.extract_date 
            ad_data["website"] = ad.website 

            ad_data["whatsapp"] = ad.whatsapp
            ad_data["email"] = ad.email
            ad_data["verified_ad"] = ad.verified_ad
            ad_data["prepayment"] = ad.prepayment 
            ad_data["promoted_ad"] = ad.promoted_ad 
            ad_data["external_website"] = ad.external_website
            ad_data["reviews_website"] = ad.reviews_website

            # Phone data.
            ad_data["phone"] = phone.phone

            # Location data.
            ad_data["country"] = location.country
            ad_data["region"] = location.region
            ad_data["city"] = location.city
            ad_data["place"] = location.place
            ad_data["latitude"] = location.latitude
            ad_data["longitude"] = location.longitude
            ad_data["zoom"] = location.zoom

            output.append(ad_data)

        last_id = ads[-1][0].id_ad
        print("Request memory size: ", getsize(output), " bytes.")
        
        return jsonify({"total_results": total_results, "last_id":  last_id, "ads": output}), 200
    
"""
This functions allows users to get the ChainBreaker Human Trafficking Glossary.
"""
@app.route('/api/data/get_glossary', methods=['POST', "GET"])
@token_required
def get_glossary(current_user):
    level = permission_level[current_user.permission]
    if level == 0:
        return jsonify({'message' : 'Cannot perform that function!'})

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
    level = permission_level[current_user.permission]
    if level == 0:
        return jsonify({'message' : 'Cannot perform that function!'})
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

#####################################
## ChainBreaker Scrapers Endpoints ##
#####################################
"""
Get soup given an url.
"""
@app.route("/api/scraper/get_soup", methods = ["POST", "GET"])
def get_soup():
    data = request.values
    url = data["url"]
    return jsonify({"result": "Service not currently available"}), 400

"""
Get if ad exists.
"""
@app.route("/api/scraper/does_ad_exists", methods = ["POST", "GET"])
def does_ad_exists():

    WEBSITE_WITH_ADS_REPETEAD = ["mileroticos"]

    does_ad_exist = 1
    data = request.values
    id_page = str(data["id_page"])
    website = data["website"]
    ads = Ad.query.filter_by(id_page = id_page).first()

    if ads == None:
        does_ad_exist = 0
    else: 
        if website in WEBSITE_WITH_ADS_REPETEAD:
            now = datetime.datetime.now()
            id_ad = int(ads.id_ad)
            date = Date.query.filter_by(id_ad = id_ad).filter_by(date = now).first()

            if date == None:
                new_date = Date(id_ad, now)
                db.session.add(new_date)
                db.session.commit()

    return jsonify({"does_ad_exist": does_ad_exist})

"""
This function format text.
"""
@app.route("/api/scraper/format_text", methods = ["POST", "GET"])
def format_text():


    import re
    import unicodedata as uc
    from string import punctuation

    def deEmojify(text):
        regrex_pattern = re.compile(pattern = "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                            "]+", flags = re.UNICODE)
        s = regrex_pattern.sub(r'',text)
        val_aux = re.sub(r'[\u200b|\u2010|\u1967]+', '', s)  
        s = uc.normalize('NFC',val_aux)
        return s
    def remove_special_characters(text):
        s = ""
        for char in text:
            if char.isalnum() or char.isspace() or char in punctuation:
                s+=char
        s_ = " ".join(s.split())
        val_aux = re.sub(r'[\u200b|\u2010]+', '', s_)  
        s = uc.normalize('NFC',val_aux)
        return s
    def tolower(text):
        return text.lower()

    data = request.values
    text = data["text"]
 
    text = deEmojify(text)
    text = remove_special_characters(text)
    text = tolower(text)

    return jsonify({"text": text})

"""
This function allow writers to add new advertisments to ChainBreaker DB.
"""
@app.route('/api/scraper/insert_ad', methods=['POST', "GET"])
@token_required
def insert_ad(current_user):

    level = permission_level[current_user.permission]
    if not level >= 3:
        return jsonify({'message' : 'Cannot perform that function!'})
    data = request.values

    ################
    ##   1. Ad    ##
    ################

    # Mandatory fields.
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
    
    # Optional fields.
    email = data["email"] if data["email"] != "" else None
    whatsapp = data["whatsapp"] if data["whatsapp"] != "" else None
    email = data["email"] if data["email"] != "" else None
    verified_ad = int(data["verified_ad"]) #if data["verified_ad"] != "" else None
    prepayment = int(data["prepayment"]) #if data["prepayment"] != "" else None
    promoted_ad = int(data["promoted_ad"]) #if data["promoted_ad"] != "" else None
    external_website = data["external_website"] if data["external_website"] != "" else None
    reviews_website = data["reviews_website"] if data["reviews_website"] != "" else None
    
    # Create Ad.
    new_ad = Ad(data_version, author, language, link, id_page, title, text, category, first_post_date,
                extract_date, website, whatsapp, email, verified_ad, prepayment,
                promoted_ad, external_website, reviews_website)
    
    # Add to DB.
    db.session.add(new_ad)
    db.session.commit()

    # Get Ad Id.
    id_ad = int(Ad.query.filter_by(id_page = id_page).first().id_ad)

    #####################
    ##   2. Date       ##
    #####################
    new_date = Date(id_ad, first_post_date)
    db.session.add(new_date)

    #####################
    ##   3. Phone      ##
    #####################
    phone = data["phone"]
    new_phone = Phone(id_ad, phone, None, None, None, None, None, 0)
    db.session.add(new_phone)

    #####################
    ##   4. Comments   ##
    #####################
    comments = data.getlist("comments")
    for comment in comments: 
        new_comment = Comment(id_ad, comment)
        db.session.add(new_comment)

    #####################
    ##   5. Location   ##
    #####################

    # Mandatory fields.
    country = data["country"]
    region = data["region"]
    city = data["city"]
    place = data["place"]
    latitude = None
    longitude = None
    zoom = None

    #####################
    ##   6. Images     ##
    #####################
    if app.config["DATA_VERSION"] == "3": 
        # Insert images.
        pass

    # Create Location.
    new_location = Location(id_ad, country, region, city, place, 
                            latitude, longitude, zoom)
    # Add to DB.
    db.session.add(new_location)

    # Commit database.
    db.session.commit()
    return jsonify({"message": "Ad successfully uploaded!"}), 200
    
"""
This function recieves a name location and returns a GPS location with zoom variable.
"""
@app.route('/api/scraper/get_gps', methods=['POST', "GET"])
@token_required
def get_gps(current_user):
    level = permission_level[current_user.permission]
    if not level >= 3:
        return jsonify({'result' : 'Cannot perform that function!'})
    return jsonify({"result": "Sorry. Service not available at the moment."}), 400

    data = request.values
    location = data["location"]
    latitude, longitude, zoom = [None, None, None]

    gps_data = {}
    gps_data["latitude"] = latitude
    gps_data["longitude"] = longitude
    gps_data["zoom"] = zoom
    return jsonify({"gps_data": gps_data})

"""
This function recieves a phonumber and return different variables related with it.
"""
@app.route("/api/scraper/get_phone_info", methods = ["POST", "GET"])
@token_required
def get_phone_info(current_user):
    level = permission_level[current_user.permission]
    if not level >= 3:
        return jsonify({'result' : 'Cannot perform that function!'})
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

#############################################
## ChainBreaker Machine Learning Endpoints ##
#############################################

### Fase 1.
@app.route("/api/machine_learning/compute_nlp", methods = ["POST", "GET"])
@token_required
def compute_nlp(current_user):
    level = permission_level[current_user.permission]
    if not level >= 3:
        return jsonify({'message' : 'Cannot perform that function!'})
    return jsonify({"message": 200})

### Fase 3.
@app.route("/api/machine_learning/detect_faces", methods = ["POST", "GET"])
@token_required
def detect_faces(current_user):
    level = permission_level[current_user.permission]
    if not level >= 3:
        return jsonify({'message' : 'Cannot perform that function!'})
    return jsonify({"message": 200})

### Fase 3.
@app.route("/api/machine_learning/encode_face", methods = ["POST", "GET"])
@token_required
def encode_faces(current_user):
    level = permission_level[current_user.permission]
    if not level >= 3:
        return jsonify({'message' : 'Cannot perform that function!'})
    return jsonify({"message": 200})

### Fase 3.
@app.route("/api/machine_learning/decode_face", methods = ["POST", "GET"])
@token_required
def decode_face(current_user):
    level = permission_level[current_user.permission]
    if not level >= 3:
        return jsonify({'message' : 'Cannot perform that function!'})
    return jsonify({"message": 200})

### Fase 3.
@app.route("/api/machine_learning/process_image", methods = ["POST", "GET"])
@token_required
def process_image(current_user):
    level = permission_level[current_user.permission]
    if not level >= 3:
        return jsonify({'message' : 'Cannot perform that function!'})

    # face
    # age 
    # weight 
    # height 
    # hair_color 
    # eyes_color 
    # save crop_image?

    return jsonify({"message": 200})

### Fase 3.
@app.route("/api/machine_learning/get_image_from_encoding", methods = ["POST", "GET"])
@token_required
def get_image_from_encoding(current_user):
    level = permission_level[current_user.permission]
    if not level >= 3:
        return jsonify({'message' : 'Cannot perform that function!'})
    return jsonify({"message": 200})

### Fase 1.
@app.route("/api/machine_learning/predict_ad_category", methods = ["POST", "GET"])
@token_required
def predict_ad_category(current_user):
    level = permission_level[current_user.permission]
    if not level >= 3:
        return jsonify({'message' : 'Cannot perform that function!'})
    return jsonify({"category": 0})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)