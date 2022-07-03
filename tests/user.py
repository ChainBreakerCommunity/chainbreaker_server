import unittest
import requests 
from dotenv import dotenv_values
config = dotenv_values(".env.test")

class UserTesting(unittest.TestCase):

    ENDPOINT = "http://localhost:" + config["PORT"] + "/user/"
        
    def test_user_api(self):

        # Register user.
        route = "register"
        data = {"name": config["NAME"], "email": config["TEST_EMAIL"], "password": config["PASSWORD"]}
        url = UserTesting.ENDPOINT + route
        res = requests.put(url = url, data = data)
        data = res.json()
        self.assertEqual(res.status_code, 200)

        # Log user.
        route = "login"
        data = {"email": config["TEST_EMAIL"], "password": config["PASSWORD"], "expiration": "0"}
        #print(data)
        url = UserTesting.ENDPOINT + route
        res = requests.post(url = url, data = data)
        #print(res.text)
        data = res.json()
        token = data["token"]
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["email"], config["TEST_EMAIL"])
        self.assertEqual(list(data.keys()), ["email", "name", "permission", "token"])

        # Change password.
        route = "change_password"
        data = {"recover_password": "False", "old_password": config["PASSWORD"], "new_password": config["PASSWORD"]}
        url = UserTesting.ENDPOINT + route
        res = requests.put(url = url, data = data, headers={"x-access-token": token})
        data = res.json()
        self.assertEqual(res.status_code, 200)
    
        # Delete user.
        route = "delete_user"
        data = {"email": config["TEST_EMAIL"]}
        url = UserTesting.ENDPOINT + route
        res = requests.put(url = url, data = data)
        data = res.json()
        self.assertEqual(res.status_code, 200)

    def test_delete_user(self):
        return
        route = "delete_user"
        data = {"email": config["TEST_EMAIL"]}
        url = UserTesting.ENDPOINT + route
        res = requests.put(url = url, data = data)
        data = res.json()
        self.assertEqual(res.status_code, 200)

if __name__ == "__main__":
    unittest.main()