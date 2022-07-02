from dotenv import dotenv_values
import os

def get_config():
    conf_debug = dotenv_values(".env.development")
    if bool(conf_debug["DEBUG"]):
        config = dotenv_values(".env")
        return config
    else:
        config = os.environ
        return config