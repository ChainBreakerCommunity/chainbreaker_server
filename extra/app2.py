# Import flask dependencies.
from flask import Flask, request, jsonify, make_response, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message # MAIL CONF: https://www.twilio.com/blog/2018/03/send-email-programmatically-with-gmail-python-and-flask.html

# Import SQL Alchemy.
from sqlalchemy import and_

# Import templates.
from templates import welcome, recover

# Import py2neo.
from py2neo import Graph

# Import other libraries.
from werkzeug.security import generate_password_hash, check_password_hash
import os
import sys
import folium
import hashlib
import jwt
import datetime
from functools import wraps
import random
import json

# Import utils.
import utils.geolocation 
import utils.neo4j
import extra.nlp
import utils.configuration

import logging
logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# Configure app.
app = Flask(__name__, static_url_path='')
app = utils.configuration.configure_app(app)
cors = CORS(app)
db = SQLAlchemy(app)
mail = Mail(app)

# Get Neo4j database.
graph = utils.neo4j.get_neo4j()

@app.route('/')
def root():
    """
    Return the frontend of the application.
    """
    return app.send_static_file('info.html')


"""Keyword, chainbreaker_website_endpoint
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

    try:
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
    except Exception as e: 
        return jsonify({"message": str(e)}), 404
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
        pass
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
            pass
        else: 
            return jsonify({"message": "You have exceeded the free trail API calls. If you want to keep using this service, please contact us to chainbreakerinfo@gmail.com"}), 404
    data = request.values
    phone = data["phone"]
    ads = Ad.query.filter_by(phone = phone).all()
    if len(ads) > 0:
        current_user.successful_phone_search += 1
        current_user.available_phone_calls -= 1
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
    #data = None
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
    #communities = None
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

"""
This function recieves an image and returns the coordinates where there are faces.
"""
@app.route("/api/prueba", methods = ["GET"])
def prueba():
    nlp.prueba()
    return jsonify({"message": "Hey!"}), 200


if __name__ == '__main__':
    print("PORT: ", port)
    app.run(host='0.0.0.0', port = app.config["PORT"], debug=True)