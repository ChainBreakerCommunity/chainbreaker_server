from flask import Flask, request, jsonify, make_response, render_template
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
#from sqlalchemy import create_engine
import os
from templates import welcome
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import random
import codecs

app = Flask(__name__, static_url_path='')
def get_resource_as_string(name, charset='utf-8'):
    with app.open_resource(name) as f:
        return f.read().decode(charset)
app.jinja_env.globals['get_resource_as_string'] = get_resource_as_string

app.config['CORS_HEADERS'] = 'Content-Type' # Set headers.
app.config["SECRET_KEY"] = "u[NDYu>N:~)93-#u"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://reader:@6c7J-y7Sf)33-W@juanchobanano.com:3306/chainbreaker?charset=utf8mb4"
db = SQLAlchemy(app)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = "alephmind.ai@gmail.com"
app.config['MAIL_PASSWORD'] = "Ns16mxIX"
app.config['MAIL_USE_TLS'] = False 
app.config['MAIL_USE_TLS'] = True 
mail = Mail(app)


# On IBM Cloud Cloud Foundry, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))

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

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401
        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["SHA256"])
            current_user = User.query.filter_by(public_id=data['id_user']).first()
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

"""
This functions recieves an email and a password
and returns an authorization token.
"""
@app.route('/api/user/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response('Bad request', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
    user = User.query.filter_by(name=auth.email).first()
    if not user:
        return make_response('User does not exist', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})
    if check_password_hash(user.password, auth.password):
        token = jwt.encode({'id_user' : user.id_user, "email": user.email, "permission": user.permission, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'])
        return jsonify({'token' : token.decode('UTF-8')})
    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

"""
This functions allows administrators to create new users.
"""
@app.route('/api/user/create_user', methods=['POST'])
#@token_required
def create_user():
    #if not current_user.permission == "admin":
    #    return jsonify({'message' : 'Cannot perform that function!'})

    password_length = 5
    possible_characters = "abcdefghijklmnopqrstuvwxyz1234567890"
    random_character_list = [random.choice(possible_characters) for i in range(password_length)]
    random_password = "".join(random_character_list)

    data = request.values
    name = data["name"]
    email = data["email"]
    permission = data["permission"]
    link = "https://chainbreaker-7e0c9.web.app/"

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
            template = render_template("welcome.html") #welcome(name, email[0: email.find("@")] + " (" + email[email.find("@"): ] + ")", random_password, link)
            msg.html = template
            msg.attach("chain-white.png", "image/png", open("static/images/chain-white.png", "rb").read(), disposition="inline", headers=[["Content-ID",'<chainlogo>'],]) 
            msg.attach("hero-img.png", "image/png", open("static/images/hero-img.png", "rb").read(), disposition="inline", headers=[["Content-ID",'<communitylogo>'],])
            #msg.attach("boostrap.min.css", "css", open("static/assets/vendor/bootstrap/css/bootstrap.min.css", "rb").read(), disposition="inline", headers=[["Content-ID",'<boostrap>'], ])
            #msg.attach("style.css", "css", open("static/assets/css/style.css", "rb").read(), disposition="inline", headers=[["Content-ID",'<styles>'], ])
            conn.send(msg)

    return jsonify({'message' : 'New user created!'})

"""
This function allows users to change their password.
"""
@app.route("/api/user/change_password", methods=["PUT"])
@token_required
def change_password(current_user):
    data = request.get_json()
    if check_password_hash(current_user.password, data["old_password"]):
        hashed_password = generate_password_hash(data['new_password'], method='sha256')
        current_user.password = hashed_password
        db.session.commit()
        return jsonify({'message' : 'Password updated!'}), 200
    return jsonify({'message' : 'Password could not be updated!'}), 400

"""
This functions allows users to get data from ChainBreaker Database.
"""
@app.route('/api/get_data', methods=['POST'])
@token_required
def get_data(current_user):
    data = request.get_json()



    return {"hello": "world"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
