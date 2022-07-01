import unittest
import requests 
from dotenv import dotenv_values
config = dotenv_values(".env.test")

class DataTesting(unittest.TestCase):

    ENDPOINT = "http://localhost:" + config["PORT"] + "/data/"

    def setUp(self):
        route = "login"
        data = {"email": config["EMAIL"], "password": config["PASSWORD"], "expiration": "0"}
        url = "http://localhost:" + config["PORT"] + "/user/" + route
        res = requests.post(url = url, data = data)
        data = res.json()
        token = data["token"]
        self.headers = {"x-access-token": token}

    def test_get_sexual_ads(self):

        # Get sexual ads.
        route = "get_sexual_ads"
        data = {"language": "english", "website": "leolist", "start_date": "0001-01-01", "end_date": "9999-01-01"}
        url = DataTesting.ENDPOINT + route + "?from_id=0" 
        res = requests.post(url = url, data = data, headers = self.headers)
        #print(res.text)
        self.assertEqual(res.status_code, 200)

    def test_get_sexual_ads_by_id(self):

        # Get sexual ads by id.
        route = "get_sexual_ads_by_id"
        data = {"ads_ids": [0, 1, 2, 3], "reduced_version": "0"}
        url = DataTesting.ENDPOINT + route
        res = requests.post(url = url, data = data, headers = self.headers)
        #print(res.text)
        self.assertEqual(res.status_code, 200)

    def test_get_glossary(self):
        route = "get_glossary"
        data = {"domain": "general"}
        url = DataTesting.ENDPOINT + route
        res = requests.post(url = url, data = data, headers = self.headers)
        #print(res.text)
        self.assertEqual(res.status_code, 200)

    def test_get_keywords(self):
        route = "get_keywords"
        data = {"language": "english"}
        url = DataTesting.ENDPOINT + route
        res = requests.post(url = url, data = data, headers =self.headers)
        #print(res.text)
        self.assertEqual(res.status_code, 200)

    def test_search_phone(self):
        route = "search_phone"
        data = {"phone": config["PHONE"]}
        url = DataTesting.ENDPOINT + route
        res = requests.post(url = url, data = data, headers = self.headers)
        #print(res.text)
        self.assertEqual(res.status_code, 200)

    def test_get_phone_score_risk(self):
        route = "get_phone_score_risk"
        data = {"phone": config["PHONE"]}
        url = DataTesting.ENDPOINT + route
        res = requests.post(url = url, data = data, headers = self.headers)
        #print(res.text)
        self.assertEqual(res.status_code, 200)

if __name__ == "__main__":
    unittest.main()