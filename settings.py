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
        try:
            self.dictionary[setting] = value
            self.write_settings()
        except KeyError:
            return False

    def get(self, setting):
        try:
            return self.dictionary[setting]
        except KeyError:
            return False

    def get_all(self):
        strings = []
        for key in self.dictionary:
            strings.append(f'{key}: {self.dictionary[key]}')
        return strings
    
    def write_settings(self):
        with open('settings.json', 'w') as f:
            json.dump(self.dictionary, f)