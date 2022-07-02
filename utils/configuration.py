from utils.env import get_config
config = get_config()

def configure_app(app):
    app.config['CORS_HEADERS'] = 'Content-Type' # Set headers.
    app.config["SECRET_KEY"] = config["SECRET_KEY"]
    app.config['SQLALCHEMY_DATABASE_URI'] = config["SQLALCHEMY_DATABASE_URI"]
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_POOL_SIZE"] = int(config["SQLALCHEMY_POOL_SIZE"])
    app.config['SQLALCHEMY_MAX_OVERFLOW'] = int(config["SQLALCHEMY_MAX_OVERFLOW"])
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USERNAME'] = config["MAIL_USERNAME"]
    app.config['MAIL_PASSWORD'] = config["MAIL_PASSWORD"]
    app.config['MAIL_USE_SSL'] = False 
    app.config['MAIL_USE_TLS'] = True 
    app.config["FREE_TRIAL"] = config["FREE_TRIAL"]
    app.config["DATA_VERSION"] = config["DATA_VERSION"]
    app.config["MAX_ADS_PER_REQUEST"] = config["MAX_ADS_PER_REQUEST"]
    app.config["PORT"] = config["PORT"]
    return app