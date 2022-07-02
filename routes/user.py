from flask import Blueprint, render_template, request, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from middlewares.token_required import token_required
from models.user import User
from utils.user import register_user
from templates.template import recover
from flask_mail import Message
import datetime
import jwt 

from utils.mail import mail
from utils.db import db

from dotenv import dotenv_values
config = dotenv_values(".env")
#import os
#config = os.environ


user = Blueprint("user", __name__)

@user.route('/', methods = ["GET"])
def index():
    return jsonify({"message": "USER ROUTE"})

@user.route('/login', methods = ["POST"])
def login():

    auth = None
    if request.is_json:
        auth = request.get_json()

    if auth == None: 
       auth = request.values

    if not auth or not auth["email"] or not auth["password"] or not auth["expiration"]:
        print("bad requests...")
        return make_response('Bad request', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
    user = User.query.filter_by(email=auth["email"]).first()
    if not user:
        print("user does not exist")
        return make_response('User does not exist', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth["password"]):
        minutes = max(int(auth["expiration"]), 999999)
        token = jwt.encode({'id_user' : user.id_user, "email": user.email, "permission": user.permission, "expiresIn": minutes}, config['SECRET_KEY'], algorithm = "HS256")
        return jsonify({'name': user.name, 'email': user.email, 'permission': user.permission, 'token' : token}), 200
    print("could not verified")
    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

@user.route('/register', methods = ["PUT"])
def register():
    data = request.values
    res = register_user(data)
    if res:
        return jsonify({'message' : 'New user created!'}), 200
    else: 
        return jsonify({'message' : 'There has been an error.'}), 404

@user.route("/delete_user", methods = ["PUT"])
def delete_user():
    data = request.values
    try:
        user = User.query.filter_by(email = data["email"]).first()
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message' : 'User has been deleted sucessfully.'}), 200
    except Exception as e:
        print(str(e))
        return jsonify({"message": "User not found"}), 404

@user.route('/create_user', methods = ["PUT"])
@token_required
def create_user(current_user):
    if not current_user.permission == "admin":
        return jsonify({'message' : "You don't have the required permissions to execute this function!"})
    data = request.values
    res = register_user(data)
    if res:
        return jsonify({'message' : 'New user created!'}), 200
    else: 
        return jsonify({'message' : 'There has been an error.'}), 404

@user.route('/change_password', methods = ["PUT"])
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

@user.route('/recover_password', methods = ["POST"])
def recover_password():
    data = request.values
    email = data["email"]
    link = config["TUTORIAL_API"]
    user = User.query.filter_by(email = email).first()
    token = jwt.encode({'id_user' : user.id_user, "email": user.email, "permission": user.permission, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes = 10)}, config['SECRET_KEY'], algorithm = "HS256")

    try:
        with mail.connect() as conn:
            msg = Message(subject = "Chainbreaker Password Recovery", 
                        recipients = [data["email"]], 
                        sender = config['MAIL_USERNAME'])
            template = recover(user.name, email[0: email.find("@")] + " (" + email[email.find("@"): ] + ")", token, link)
            msg.html = template
            msg.attach("chain-white.png", "image/png", open("static/images/chain-white.png", "rb").read(), disposition="inline", headers=[["Content-ID",'<chainlogo>'],]) 
            msg.attach("why-us.png", "image/png", open("static/images/why-us.png", "rb").read(), disposition="inline", headers=[["Content-ID",'<communitylogo>'],])
            conn.send(msg)
    except Exception as e: 
        return jsonify({"message": str(e)}), 404
    return jsonify({'message' : 'We have sent you a recovery e-mail to' + email + '! You have 10 minutes to change your password.'})
