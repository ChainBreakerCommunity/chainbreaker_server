from dotenv import dotenv_values
import os

def get_config():
    debug = dotenv_values(".env.development")
    if debug["DEBUG"] == "TRUE":
        config = dotenv_values(".env")
        return config
    else:
        config = os.environ
        return config