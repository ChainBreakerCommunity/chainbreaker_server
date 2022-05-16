from server import app, db
from models import Ad
from flask import request, jsonify
from flask_sqlalchemy import func
from middleware import token_required

@app.route("/api/machine_learning/get_phone_score_risk", methods = ["POST"])
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

    if first_ad == None:
        return jsonify({"message": "Phone not in database."}), 404
    else:
        score_risk = first_ad.score_risk
        avg = db.session.query(func.avg(Ad.score_risk)) \
            .filter(Ad.country == "colombia").first()[0]
        std = db.session.query(func.std(Ad.score_risk)) \
            .filter(Ad.country == "colombia").first()[0]
        standard_score = (score_risk - avg) / std
        def sigmoid_function(x):
            import math
            return 1 / (1 + math.exp(-x))
        sigmoid_value = round(sigmoid_function(standard_score), 4)
        return jsonify({"score_risk": sigmoid_value}), 200


"""
This function recieves an image and returns the coordinates where there are faces.
"""
@app.route("/api/machine_learning/get_image_faces", methods = ["POST", "GET"])
@token_required
def get_image_faces(current_user):
    #return requests.post(app.config["ML_SERVICE_ENDPOINT"], data = request.data)
    return jsonify({"message": "Service currently unavailable."})
    