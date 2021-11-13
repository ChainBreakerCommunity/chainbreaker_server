from server import app, db, graph
from flask import request, jsonify
from middleware import token_required
from models import Ad, Comment
import neo4j
import geolocation

@app.route("/api/scraper/get_soup", methods = ["POST", "GET"])
@token_required
def get_soup(current_user):
    """
    Get soup given an url.
    """
    ALLOWED_ROLES = ["scraper", "researcher", "admin"]
    if current_user.permission not in ALLOWED_ROLES:
        return jsonify({'message' : "You don't have the required permissions to execute this function!"})
    data = request.values
    url = data["url"]
    return jsonify({"result": "Service not currently available"}), 400

@app.route("/api/scraper/does_ad_exists", methods = ["POST", "GET"])
@token_required
def does_ad_exists(current_user):
    """
    Get if ad exists.
    """
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
        id_ad = int(ads.id_ad)
        if website in WEBSITE_WITH_ADS_REPETEAD:
            neo4j.create_new_date_for_ad(graph, id_ad)

    return jsonify({"does_ad_exist": does_ad_exist})

@app.route('/api/scraper/insert_ad', methods=['POST', "GET"])
@token_required
def insert_ad(current_user):
    """
    This function allow writers to add new advertisments to ChainBreaker DB.
    """
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
    if latitude == 0 and longitude == 0:
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
    neo4j_data = data.to_dict(flat = True)
    neo4j_data["id_ad"] = id_ad

    # Create Ad in Neo4j and correspoding relationships.
    neo4j.create_ad(graph, neo4j_data)

    # Upload comments.
    comments = data.getlist("comments")
    for comment in comments: 
        new_comment = Comment(id_ad, comment)
        db.session.add(new_comment)

    return jsonify({"message": "Ad successfully uploaded!"}), 200
    
@app.route("/api/scraper/get_phone_info", methods = ["POST", "GET"])
@token_required
def get_phone_info(current_user):
    """
    This function recieves a phonumber and return different variables related with it.
    """
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