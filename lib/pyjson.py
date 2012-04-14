import json
import os


def parse_json(s):
    return json.loads(s)


def save_json(d):
    return json.dumps(d)


class PyJson:
    """
    Class to abstract the process of reading, writing and parsing json files,
    using Python's json module.
    """
    def __init__(self, path, base={}):
        """
        Create the file if it does not exist and add an empty json object to it
        """
        self.path = path

        if not os.path.exists(path):
            f = open(path, 'w')
            f.write(json.dumps(base, sort_keys=True, indent=4))
            f.close()

        f = open(path, 'r')

        # parse the json file in to a native Python dictionary object
        self.doc = json.load(f)

        f.close()

    def add(self, key, value):
        """Add a record to the python dictionary"""
        self.doc[key] = value

    def remove(self, key):
        """Remove a record from the python dictionary"""
        self.doc[key] = None

    def save(self):
        """Save a json representation of the python dictionary to the file"""
        f = open(self.path, 'w')
        f.write(json.dumps(self.doc, sort_keys=True, indent=4))
        f.close()
