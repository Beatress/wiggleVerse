# Copyright Beatrice Tohni 2021
""" This file is part of wiggleVerse.

    wiggleVerse is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    wiggleVerse is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with wiggleVerse.  If not, see <https://www.gnu.org/licenses/>."""

import logging
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
            self.dictionary[setting] # This will throw an exception if it fails
            if setting == 'nick' or setting == 'user':
                value = value[0]
            elif setting == 'real':
                value = ' '.join(value)
            else:
                return False
            self.dictionary[setting] = value
            self.write_settings()
            return value
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