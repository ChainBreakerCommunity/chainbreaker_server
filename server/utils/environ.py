import json 
class Environment:
    def __init__(self, filepath):
        with open(filepath) as json_file: 
            self.data = json.load(json_file)
    def get(self, key):
        return self.data[key]