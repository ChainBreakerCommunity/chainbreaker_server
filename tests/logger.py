import unittest
import requests 
from dotenv import dotenv_values
import joblib
config = dotenv_values(".env.test")

class LoggerTesting(unittest.TestCase):

    ENDPOINT = "http://localhost:" + config["PORT"] + "/get_logging"

    def test_get_labels_count(self):
        url = LoggerTesting.ENDPOINT
        data = {"route": "routes.user"}
        res = requests.post(url = url, data = data)
        print(res.text)
        self.assertEqual(res.status_code, 200)

if __name__ == "__main__":
    unittest.main()