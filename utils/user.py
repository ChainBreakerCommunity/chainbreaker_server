from flask import request
from flask_mail import Message
import random
from utils.db import db
from utils.mail import mail
from models.user import User
from werkzeug.security import generate_password_hash
from templates.template import welcome
from dotenv import dotenv_values
config = dotenv_values(".env")
#import os
#config = os.environ

def register_user(data: dict) -> bool:

    password_length = 5
    possible_characters = "abcdefghijklmnopqrstuvwxyz1234567890"
    random_character_list = [random.choice(possible_characters) for i in range(password_length)]
    random_password = "".join(random_character_list)

    data = request.values
    name = data["name"]
    email = data["email"]
    password = data["password"]

    user = User.query.filter_by(email=email).first()
    if user != None:
        return True

    permission = "reader"
    link = config["TUTORIAL_API"]

    hashed_password = generate_password_hash(password, method="sha256")#generate_password_hash(random_password, method='sha256')
    new_user = User(name = name,
                    email = email, 
                    password = hashed_password, 
                    permission = permission)
    db.session.add(new_user)
    db.session.commit()
    return True
    
    try:
        with mail.connect() as conn:
            msg = Message(subject = "Welcome to ChainBreaker Community!", 
                        recipients = [data["email"]], 
                        sender = config['MAIL_USERNAME'])
            #render_template("welcome.html")
            template = welcome(name, email[0: email.find("@")] + " (" + email[email.find("@"):  ] + ")", random_password, link)
            msg.html = template
            msg.attach("chain-white.png", "image/png", open("static/images/chain-white.png", "rb").read(), disposition="inline", headers=[["Content-ID",'<chainlogo>'],]) 
            msg.attach("hero-img.png", "image/png", open("static/images/hero-img.png", "rb").read(), disposition="inline", headers=[["Content-ID",'<communitylogo>'],])
            conn.send(msg)
    except Exception as e: 
        print(str(e))
        return False
    return True