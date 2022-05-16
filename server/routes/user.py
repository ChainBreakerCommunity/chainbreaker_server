from server import app, db, mail
from flask import request, jsonify, make_response
from models import User
from middleware import token_required
import random 
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from templates import welcome, recover
from flask_mail import Message
import datetime 

@app.route('/api/user/login', methods = ["POST"])
def login():
    """
    This functions recieves an email and a password
    and returns an authorization token.
    """
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

@app.route('/api/user/create_user', methods=['PUT'])
@token_required
def create_user(current_user):
    """
    This functions allows administrators to create new users.
    """
    if not current_user.permission == "admin":
        return jsonify({'message' : "You don't have the required permissions to execute this function!"})

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

@app.route("/api/user/change_password", methods=["PUT"])
@token_required
def change_password(current_user):
    """
    This function allows users to change their password.
    """
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

@app.route('/api/user/recover_password', methods=['POST'])
def recover_password():
    """
    This functions allows administrators to create new users.
    """
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