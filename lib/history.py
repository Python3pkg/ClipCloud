from lib.settings import *
import json
from time import time


class History():
    """
    Defines methods for interacting with the file that stores
    a history of the files that the user has uploaded to the service
    """

    def load(self):
        """
        Private method
        Loads the JSON file that holds the history
        Returns: A dictionary representing it
        """

        raw_history = open(HISTORY_PATH, 'r')
        history = json.load(raw_history)
        return history

    def display(self, limit, direction):
        """
        Load the history and print out a number of records to the screen.
        Arguments:
            - limit: the number of items to show
            - direction: the order to sort the files in to, (ascending or descending)
            - sort_by: the value to sort by (id, path, url or date)
        """

        history = self.load()['history']
        print "Id, URL, Local File, Date Created"
        for record in history:
            if limit == 0:
                return

            id = record['id']
            url = record['url']
            path = record['path']
            _date = date.fromtimestamp(record['timestamp']).strftime('%d/%m/%Y')

            print id, url, path, _date

            limit -= 1

    def add(self, path, url):
        """
        Write a new record to the history
        Arguments:
            - path: the path to the local copy of the file that was uploaded
            - url: the shortened URl that points to the
                copy of the file hosted on the users dropbox acount
        """
        doc = self.load()
        history = doc['history']

        id = 0 if len(history) == 0 else history[-1]['id'] + 1

        history.append({
            'id': id,
            'path': path,
            'url': url,
            'timestamp': time()
        })

        raw = open(HISTORY_PATH, 'w')
        raw.write(json.dumps(doc, sort_keys=True, indent=4))
        raw.close()
