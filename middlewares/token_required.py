
from flask import request, jsonify
from utils.db import db
from functools import wraps
import datetime
import jwt
from models.user import User
from dotenv import dotenv_values
config = dotenv_values(".env")
#import os
#config = os.environ


def token_required(f):
    """
    Token required middleware.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401
        try: 
            data = jwt.decode(token, config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(email=data['email']).first()
            current_user.api_calls += 1
            current_user.last_api_call_date = datetime.datetime.now()
            db.session.commit()
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated