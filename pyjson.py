import json
import os


def parse_json(s):
    return json.loads(s)


def save_json(d):
    return json.dumps(d)


class PyJson:
    """
    Class to abstract the process of reading, writing and parsing JSON files
    using Python's inbuilt json module.
    """

    def __init__(self, path, base={}):
        """
        Create the file if it does not exist and add an empty JSON object to it

        path - The path to the file to store the JSON in
        base - The root structure of the JSON document
        """

        self.path = path

        if not os.path.exists(path):
            f = open(path, 'w')
            f.write(json.dumps(base, indent=4))
            f.close()

        f = open(path, 'r')

        # parse the JSON file to a native Python dictionary object
        self.doc = json.load(f)

        f.close()

    def add(self, key, value):
        """Add a record to the Python dictionary"""

        self.doc[key] = value

    def remove(self, key):
        """Remove a record from the Python dictionary"""

        try:
            del self.doc[key]
        except KeyError:
            pass

    def save(self):
        """Save a JSON representation of the Python dictionary to the file"""

        f = open(self.path, 'w')
        f.write(json.dumps(self.doc, indent=4))
        f.close()
