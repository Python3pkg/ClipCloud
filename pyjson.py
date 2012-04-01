import json
import os


class PyJson:
    def __init__(self, path):
        self.path = path

        if not os.path.exists(path):
            f = open(path, 'w')
            f.write(json.dumps({}, sort_keys=True, indent=4))
        else:
            f = open(path, 'r')

        self.doc = json.load(f)

        f.close()

    def add(self, key, value):
        self.doc[key] = value

    def remove(self, key):
        self.doc[key] = None

    def save(self):
        f = open(self.path, 'w')
        f.write(json.dumps(self.doc, sort_keys=True, indent=4))
        f.close()
