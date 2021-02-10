import random
import json
import os.path

class Settings:
    def __init__(self):
        # Check if settings file exists
        if os.path.isfile('settings.json'):
            with open('settings.json', 'r') as f:
                self.dictionary = json.load(f)
        else:
            self.dictionary = {
                'nick': 'Wiggler' + str(random.randint(111,999)),
                'user': 'wiggler',
                'real': 'A Very Cool Wiggler!'
            }
            self.write_settings()
        
    def put(self, setting, value):
        self.dictionary[setting] = value
        write_settings()

    def get(self, setting):
        try:
            return self.dictionary[setting]
        except KeyError:
            return False

    def write_settings(self):
        with open('settings.json', 'w') as f:
            json.dump(self.dictionary, f)