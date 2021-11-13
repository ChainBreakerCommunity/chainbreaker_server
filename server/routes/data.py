import app
import requests
from middleware import token_required
from flask import request, jsonify
from models import Ad, Glossary, Keyword
from server import db, graph
import neo4j 
import hashlib
from sqlalchemy import func

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

def textToHash(text):
    hash_function = hashlib.sha256()
    x = bytes(str(text), "utf-8")
    hash_function.update(x)
    hash = hash_function.hexdigest()
    return hash

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
        ad_data["link"] = textToHash(ad.link) if not secure else ad.link
        ad_data["id_page"] = ad.id_page
        ad_data["title"] = ad.title
        ad_data["text"] = ad.text 
        ad_data["category"] = ad.category 
        ad_data["first_post_date"] = ad.first_post_date
        ad_data["extract_date"] = ad.extract_date 
        ad_data["website"] = ad.website 

        # Phone data.
        ad_data["phone"] = textToHash(ad.phone) if not secure else ad.phone

        # Location data.
        ad_data["country"] = ad.country
        ad_data["region"] = ad.region
        ad_data["city"] = ad.city
        ad_data["place"] = ad.place
        ad_data["latitude"] = ad.latitude
        ad_data["longitude"] = ad.longitude
        ad_data["zoom"] = ad.zoom
        ad_data["email"] = textToHash(ad.email) if not secure else ad.email
        ad_data["verified_ad"] = ad.verified_ad
        ad_data["prepayment"] = ad.prepayment 
        ad_data["promoted_ad"] = ad.promoted_ad 
        ad_data["external_website"] = textToHash(ad.external_website) if not secure else ad.external_website
        ad_data["reviews_website"] = textToHash(ad.reviews_website) if not secure else ad.reviews_website
        ad_data["nationality"] = ad.nationality
        ad_data["age"] = ad.age

        last_id = ad.id_ad
        output.append(ad_data)
    return output, last_id

@app.route('/api/data/get_sexual_ads', methods=['POST'])
@token_required
def get_sexual_ads(current_user):
    """
    This functions allows users to get data from ChainBreaker Database.
    """
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
    dates_subquery = neo4j.get_ads_inside_dates(graph, start_date, end_date)
    #print(type(dates_subquery[0]), type(Ad.id_ad))

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
        output, last_id = format_ads_to_json(ads)
        #print("Request memory size: ", getsize(output), " bytes.")
        return jsonify({"total_results": total_results, "last_id":  last_id, "ads": output}), 200
    
@app.route('/api/data/get_sexual_ads_by_id', methods=['POST'])
@token_required
def get_sexual_ads_by_id(current_user):
    """
    This functions allows users to get specific data from ChainBreaker Database.
    """
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
        output, last_id = format_ads_to_json(ads)
    else:
        ads = db.session.query(Ad.id_ad, Ad.language, Ad.title, Ad.text, Ad.category, Ad.country, Ad.city, Ad.external_website) \
            .filter(Ad.id_ad.in_(ids_filter)) \
            .all()
        output = format_ads_reduced_to_json(ads)

    return jsonify({"ads": output}), 200

@app.route('/api/data/get_sexual_ad_for_review', methods=["GET"])
@token_required
def get_sexual_ad_for_review(current_user):
    ALLOWED_ROLES = ["expert", "researcher", "admin"]
    if current_user.permission not in ALLOWED_ROLES:
        return jsonify({'message' : "You don't have the required permissions to execute this function!"})
    first_ad = db.session.query(Ad).order_by(func.random()).first()
    output = format_ads_to_json([first_ad], secure = True)[0]
    return jsonify(output)

@app.route("/api/data/submit_review", methods=["POST"])
@token_required
def submit_review(current_user):
    ALLOWED_ROLES = ["expert", "researcher", "admin"]
    if current_user.permission not in ALLOWED_ROLES:
        return jsonify({'message' : "You don't have the required permissions to execute this function!"}), 401
    auth = request.get_json()
    if auth == None: 
       auth = request.values
    print(auth)
    return jsonify({"message": "ok"})

@app.route('/api/data/get_glossary', methods=['POST'])
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

@app.route('/api/data/get_keywords', methods=['POST'])
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

@app.route("/api/data/check_phone_in_db", methods = ["POST"])
@token_required
def check_phone_in_db(current_user):
    """
    Check if phone is in database.
    """
    ALLOWED_ROLES = ["researcher", "admin"]
    if current_user.permission not in ALLOWED_ROLES:
        return jsonify({'message' : "You don't have the required permissions to execute this function!"})
    data = request.values
    phone = data["phone"]
    ads = Ad.query.filter_by(phone = phone).all()
    output = list()
    for ad in ads:
        ad_data = {}
        ad_data["link"] = ad.link
        ad_data["title"] = ad.title
        ad_data["phone"] = ad.phone
        output.append(ad_data)
    return jsonify({"ads": output}), 200
