from flask import Flask, request, jsonify, make_response, render_template
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
from sqlalchemy import or_, and_
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
Return the frontend of the application.
"""
@app.route('/')
def root():
    return app.send_static_file('index.html')

"""
Define User Model
"""
class User(db.Model):
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
Define Ad Model
"""
class Ad(db.Model):
    id_ad = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(20))
    link = db.Column(db.String(100))
    id_page = db.Column(db.Integer)
    title = db.Column(db.String(100))
    text = db.Column(db.String(10000))
    category = db.Column(db.String(20))
    post_date = db.Column(db.DateTime(10))
    verified_ad = db.Column(db.Boolean())
    no_prepayment = db.Column(db.Boolean())
    promoted_ad = db.Column(db.Boolean())
    email = db.Column(db.String(100))
    external_website = db.Column(db.String(100))
    reviews_website = db.Column(db.String(100))
    website = db.Column(db.String(20))
    extract_date = db.Column(db.DateTime(10))

    def __init__(self, language, link, id_page, title, text, 
                category, post_date, verified_ad, no_prepayment, 
                promoted_ad, extract_date, website, email = None, 
                external_website = None, reviews_website = None):

        self.language = language
        self.link = link
        self.id_page = id_page
        self.title = title
        self.text = text
        self.category = category
        self.post_date = post_date
        self.verified_ad = verified_ad
        self.no_prepayment = no_prepayment
        self.promoted_ad = promoted_ad
        self.extract_date = extract_date
        self.website = website
        self.email = email
        self.external_website = external_website
        self.reviews_website = reviews_website

"""
Define Location Model
"""
class Location(db.Model):
    pass

"""
Define Phone Model
"""
class Phone(db.Model):
    pass

"""
Define Feature Model
"""
class Feature(db.Model):
    pass

"""
Define Whatsapp Model
"""
class WhatsApp(db.Model):
    pass


"""
Define Glossary Model
"""
class Glossary(db.Model):
    id_term = db.Column(db.Integer, primary_key=True)
    domain = db.Column(db.String(20))
    term = db.Column(db.String(30))
    definition = db.Column(db.String(1000))

"""
Define Keyword Model
"""
class Keyword(db.Model):
    id_keyword = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(20))
    keyword = db.Column(db.String(30))
    english_translation = db.Column(db.String(30))
    meaning = db.Column(db.String(1000))
    age_flag = db.Column(db.Boolean())
    trafficking_flag = db.Column(db.Boolean())
    movement_flag = db.Column(db.Boolean())


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
        return jsonify({'name': user.name, 'email': user.email, 'permission': user.permission, 'token' : token})
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
@app.route('/api/data/get_ads', methods=['POST', "GET"])
@token_required
def get_ads(current_user):
    level = permission_level[current_user.permission]
    if level == 0:
        return jsonify({'message' : 'Cannot perform that function!'})
    data = request.values
    filtered_args = {k: v for k, v in data.items() if v != ""}
    filters = [getattr(Ad, attribute) == value for attribute, value in filtered_args.items()]
    ads = Ad.query.filter(and_(*filters)).limit(200).all()

    output = list()
    for ad in ads: 
        ad_data = {}
        ad_data["id_ad"] = ad.id_ad
        ad_data["language"] = ad.language
        ad_data["link"] = ad.link
        ad_data["id_page"] = ad.id_page
        ad_data["title"] = ad.title
        ad_data["text"] = ad.text 
        ad_data["category"] = ad.category 
        ad_data["post_date"] = ad.post_date
        ad_data["verified_ad"] = ad.verified_ad
        ad_data["no_prepayment"] = ad.no_prepayment 
        ad_data["promoted_ad"] = ad.promoted_ad 
        ad_data["email"] = ad.email
        ad_data["external_website"] = ad.external_website
        ad_data["reviews_website"] = ad.reviews_website
        ad_data["website"] = ad.website 
        ad_data["extract_date"] = ad.extract_date 
        output.append(ad_data)
    return jsonify({"ads": output})
    
"""
This functions allows users to get the ChainBreaker Human Trafficking Glossary.
"""
@app.route('/api/data/get_glossary', methods=['POST', "GET"])
@token_required
def get_glossary(current_user):
    level = permission_level[current_user.permission]
    print("level: ", level >= 1)
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
    return jsonify({"glossary": output})

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
    return jsonify({"keywords": output})

"""
This function allow writers to add new advertisments to ChainBreaker DB.
"""
@app.route('/api/scraper/insert_ad', methods=['POST', "GET"])
@token_required
def insert_ad(current_user):
    
    level = permission_level[current_user.permission]
    if level >= 3:
        return jsonify({'message' : 'Cannot perform that function!'})
    data = request.values


    # language
    # link
    # id_page
    # title
    # text
    # category
    # post_date
    # verified_ad
    # no_prepayment
    # promoted_ad
    # external_website
    # email
    # reviews_website
    # website
    # extract_date

    # comment

    # country
    # region
    # city
    # place
    # latitude
    # longitude
    # zoom

    # age
    # nationality
    # ethnicity
    # availability
    # weight
    # height
    # hair color
    # eyes color
    # price

    # whatsapp

    return jsonify({"status": 200})
    
"""
This function recieves a name location and returns a GPS location with zoom variable.
"""
@app.route('/api/scraper/get_gps', methods=['POST', "GET"])
@token_required
def get_gps(current_user):
    level = permission_level[current_user.permission]
    if level >= 3:
        return jsonify({'message' : 'Cannot perform that function!'})
    
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
@app.rout("/api/scraper/get_phone_info", mehotds = ["POST", "GET"])
@token_required
def get_phone_info(current_user):
    level = permission_level[current_user.permission]
    if level >= 3:
        return jsonify({'message' : 'Cannot perform that function!'})

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

"""
Machine Learning models. (repo distinto)
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
