from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import and_
from utils.db import db
from middlewares.token_required import token_required
from models.ad import Ad
from models.glossary import Glossary
from models.keyword import Keyword
from utils.ads import format_ads_reduced_to_json, format_ads_to_json
import datetime
from utils.env import get_config
config = get_config()

data = Blueprint("data", __name__)

@data.route('/')
def index():
    return jsonify({"message": "DATA ROUTE"})

@data.route('/get_sexual_ads', methods=['POST', "GET"])
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
        .limit(config["MAX_ADS_PER_REQUEST"]) \
        .all()

    # Close session.
    db.session.close()

    if len(ads) == 0:
        return jsonify({"message": "No results were found for your search"}), 401
    else:
        output, last_id = format_ads_to_json(ads, secure = secure)
        #print("Request memory size: ", getsize(output), " bytes.")
        return jsonify({"total_results": total_results, "last_id":  last_id, "ads": output}), 200
    
@data.route('/get_sexual_ads_by_id', methods=['POST', "GET"])
@token_required
def get_sexual_ads_by_id(current_user):
    """
    This functions allows users to get specific data from ChainBreaker Database.
    SECURE ENDPOINT.
    """
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

    # Close session.
    db.session.close()
    return jsonify({"ads": output}), 200

@data.route('/get_glossary', methods=['POST', "GET"])
@token_required
def get_glossary(current_user):
    """
    This functions allows users to get the ChainBreaker Human Trafficking Glossary.
    """
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

@data.route('/get_keywords', methods=['POST', "GET"])
@token_required
def get_keywords(current_user):
    """
    This functions allows users to get the ChainBreaker Human Trafficking Keywords.
    """
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

@data.route("/search_phone", methods = ["POST", "GET"])
@token_required
def search_phone(current_user):
    """
    Check if phone is in database.
    """
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
        db.session.close()
        return jsonify({"ads": output}), 200
    else:
        db.session.close()
        return jsonify({"message": "No results were found for your search"}), 404

@data.route("/get_phone_score_risk", methods = ["POST", "GET"])
@token_required
def get_phone_score_risk(current_user):
    """
    Get risk score of cellphone.
    """
    ALLOWED_ROLES = ["client", "researcher", "admin"]
    if current_user.permission not in ALLOWED_ROLES:
        return jsonify({'message' : "You don't have the required permissions to execute this function!"})

    data = request.values
    phone = int(data["phone"])
    first_ad = db.session.query(Ad) \
        .filter(Ad.phone == phone) \
        .first()

    db.session()
    if first_ad == None:
        return jsonify({"message": "Phone not in database."}), 404
    else:
        score_risk = first_ad.score_risk
        return jsonify({"score_risk": score_risk}), 200