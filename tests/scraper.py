import unittest
import requests 
import json 
from dotenv import dotenv_values
config = dotenv_values(".env.test")

class ScrapingTesting(unittest.TestCase):

    ENDPOINT = "http://localhost:" + config["PORT"] + "/scraper/"

    @classmethod
    def setUpClass(cls):
        route = "login"
        data = {"email": config["EMAIL"], "password": config["PASSWORD"], "expiration": "0"}
        url = "http://localhost:" + config["PORT"] + "/user/" + route
        res = requests.post(url = url, data = data)
        data = res.json()
        token = data["token"]
        cls.headers = {"x-access-token": token}

    def test_does_ad_exists(self):
        route = "does_ad_exists"
        data = {"id_page": config["ID_PAGE"], "website": config["WEBSITE"], "country": config["COUNTRY"]}
        url = ScrapingTesting.ENDPOINT + route
        res = requests.post(url = url, data = data, headers = self.headers)
        self.assertEqual(res.status_code, 200)
        res = res.json()["does_ad_exist"]
        self.assertEqual(res, 0)

    def test_expected_fields(self):
        route = "expected_fields"
        url = ScrapingTesting.ENDPOINT + route
        res = requests.get(url = url, headers = self.headers)
        self.assertEqual(res.status_code, 200)
        res = res.json()
        print(res["fields"])
        
    def test_insert_ad(self):
        route = "insert_ad"
        f = open("ad.json")
        data = json.load(f)
        print(data)
        url = ScrapingTesting.ENDPOINT + route
        res = requests.post(url = url, data = data, headers = self.headers)
        self.assertEqual(res.status_code, 200)

if __name__ == "__main__":
    unittest.main()