
from flask import Blueprint, jsonify, request
from middlewares.token_required import token_required
from sqlalchemy import inspect
from models.ad import Ad
from models.comment import Comment
from utils.db import db
from utils.auxiliar_functions import format_string
import utils.neo4j

#from dotenv import dotenv_values
#config = dotenv_values(".env")
import os
config = os.environ


scraper = Blueprint("scraper", __name__)

@scraper.route("/does_ad_exists", methods = ["POST"])
@token_required
def does_ad_exists(current_user):
    """
    Get if ad exists.
    """
    ALLOWED_ROLES = ["scraper", "reseacher", "admin"]
    if current_user.permission not in ALLOWED_ROLES:
        return jsonify({'message' : "You don't have the required permissions to execute this function!"})

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
    return jsonify({"does_ad_exist": does_ad_exist})

@scraper.route('/expected_fields', methods=["GET"])
@token_required
def expected_fields(current_user):
    """
    This function returns the fields expected by the scraper.
    """
    ALLOWED_ROLES = ["scraper", "researcher", "admin"]
    if current_user.permission not in ALLOWED_ROLES:
        return jsonify({'message' : "You don't have the required permissions to execute this function!"}), 400
    inst = inspect(Ad)
    attr_names = [c_attr.key for c_attr in inst.mapper.column_attrs]
    return jsonify({"fields": attr_names}), 200

@scraper.route('/insert_ad', methods=['POST', "GET"])
@token_required
def insert_ad(current_user):
    """
    This function allow writers to add new advertisments to ChainBreaker DB.
    """
    ALLOWED_ROLES = ["scraper", "researcher", "admin"]
    if current_user.permission not in ALLOWED_ROLES:
        return jsonify({'message' : "You don't have the required permissions to execute this function!"})
    data = request.values

    print("Data received!")
    #print(data)
    print("Data keys: ")
    print(data.keys())
    print(data.values)

    # Ad data.
    data_version = config["DATA_VERSION"]
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
    phone = data["phone"] if data["phone"] != "" else None

    # Location.
    country = data["country"]
    region = data["region"]
    city = data["city"] if data["city"] != "" else None
    place = data["place"] if data["place"] != "" else None
    latitude = float(data["latitude"]) if data["latitude"] != "" else 0
    longitude = float(data["longitude"]) if data["longitude"] != "" else 0
    zoom = 0

    # Format string values.
    country = format_string(country)
    region = format_string(region)
    city = format_string(region)
    place = format_string(place)

    # Optional parameters.
    ethnicity = data["ethnicity"] if data["ethnicity"] != "" else None
    nationality = data["nationality"] if data["nationality"] != "" else None
    age = int(data["age"]) if data["age"] != "" else None

    # Format nationality.
    ethnicity = format_string(ethnicity)
    nationality = format_string(nationality)

    # Optional fields.
    email = data["email"] if data["email"] != "" else None
    verified_ad = int(data["verified_ad"]) if data["verified_ad"] != "" else None
    prepayment = int(data["prepayment"]) if data["prepayment"] != "" else None
    promoted_ad = int(data["promoted_ad"]) if data["promoted_ad"] != "" else None
    external_website = data["external_website"] if data["external_website"] != "" else None
    reviews_website = data["reviews_website"] if data["reviews_website"] != "" else None

    # Risk Score.
    risk_score = None

    if(email == None and phone == None):
        return jsonify({"message": "Phone and email can not be null at the same time!"}), 400

    # Create Ad in MySQL.
    new_ad = Ad(data_version, author, language, link, id_page, title, text, category, first_post_date,
                extract_date, website, phone, country, region, city, place, latitude, longitude, zoom, 
                email, verified_ad, prepayment, promoted_ad, external_website, reviews_website, ethnicity, nationality, age, 
                risk_score)

    # Add to DB.
    db.session.add(new_ad)
    db.session.flush()
    # Get last Ad id.
    #id_ad = int(Ad.query.filter_by(id_page = id_page).first().id_ad)

    # Create Ad in Neo4j and correspoding relationships.
    neo4j_data = data.to_dict(flat = True)
    neo4j_data["id_ad"] = new_ad.id_ad
    graph, tx = utils.neo4j.create_ad(neo4j_data)

    # Upload comments.
    comments = data.getlist("comments")
    for comment in comments: 
        new_comment = Comment(new_ad.id_ad, comment)
        db.session.add(new_comment)

    # Commit both databases.
    db.session.commit()
    graph.commit(tx)

    return jsonify({"message": "Ad successfully uploaded!"}), 200   