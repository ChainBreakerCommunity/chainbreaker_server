import os
import requests
import time

# Link: https://realpython.com/python-testing/
ENDPOINT = "http://localhost:8000"
LOGIN_DATA = {"email": "jecepedab@unal.edu.co", "password": "xxnh12lq", "expiration": "0"}
CHANGE_DATA =  {"recover_password": "False", "old_password": "xxnh12lq", "new_password": "xxnh12lq"}
ADS_DATA =  {"language": "", "website" : "", "filter_phones": "", "filter_location": ""}
GLOSSARY_DATA = {"domain": ""}
KEYWORDS_DATA = {"language": ""}

# Run assets.
def test_status():
    assert requests.get(ENDPOINT + "/api/status").status_code == 200
    res = requests.post(ENDPOINT + "/api/user/login", data = LOGIN_DATA)
    assert res.status_code == 200
    token = res.json()["token"]
    headers = {"x-access-token": token}
    assert requests.put(ENDPOINT + "/api/user/change_password", data = CHANGE_DATA, headers = headers)
    assert requests.post(ENDPOINT + "/api/data/get_ads", data = ADS_DATA, headers = headers).status_code == 200
    assert requests.post(ENDPOINT + "/api/data/get_glossary", data = GLOSSARY_DATA, headers = headers).status_code == 200
    assert requests.post(ENDPOINT + "/api/data/get_keywords", data = KEYWORDS_DATA, headers = headers).status_code == 200
    
print("Testing...")
test_status()
print("Everything passed")