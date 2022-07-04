import unittest
import requests 
from dotenv import dotenv_values
import joblib
config = dotenv_values(".env.test")

class GraphTesting(unittest.TestCase):

    ENDPOINT = "http://localhost:" + config["PORT"] + "/graph/"

    def test_get_labels_count(self):
        route = "get_labels_count"
        url = GraphTesting.ENDPOINT + route
        res = requests.get(url = url)
        self.assertEqual(res.status_code, 200)
        res = res.json()["labels_count"]
        #for r in res:
        #    print(r["label"], r["count"])

    def test_get_communities(self):
        return
        route = "get_communities"
        url = GraphTesting.ENDPOINT + route
        data = {"country": "canada"}
        res = requests.post(url = url, data = data)
        self.assertEqual(res.status_code, 200)
        res = res.json()["communities"]
        self.assertGreater(len(res), 1)
        joblib.dump(res, "communities.pkl")

    def test_delete_graph(self):
        return
        route = "delete_graph"
        url = GraphTesting.ENDPOINT + route
        res = requests.get(url = url)
        self.assertEqual(res.status_code, 200)
        
    def test_get_node_info(self):
        return
        route = "get_node_info"
        url = GraphTesting.ENDPOINT + route
        data = {"label": "Ad", "id_ad": "46407"}
        res = requests.post(url = url, data = data)
        self.assertEqual(res.status_code, 200)
        res = res.json()
        print(res)

    def test_get_last_node(self):
        route = "get_last_ad"
        url = GraphTesting.ENDPOINT + route
        res = requests.get(url = url)
        print(res.text)
        self.assertEqual(res.status_code, 200)
        res = res.json()["node"]
        

if __name__ == "__main__":
    unittest.main()
