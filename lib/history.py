from lib.settings import HISTORY_PATH
from time import time
from datetime import date
from pyjson import PyJson


class History:
    """
    Defines methods for interacting with the file that stores
    a history of the files that the user has uploaded to the service
    """
    def __init__(self):
        self.history = PyJson(HISTORY_PATH, base={'history': []})

    def display(self, limit, sort_by, direction):
        """
        Load the history and print out a number of records to the screen.
        Arguments:
            - limit: the number of items to show
            - direction: the order to sort the files in to, (ascending or descending)
            - sort_by: the value to sort by (id, path, url or date)
        """

        history = sorted(self.history.doc['history'], key=lambda k: k[sort_by])

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
        history = self.history.doc['history']

        id = 0 if len(history) == 0 else history[-1]['id'] + 1

        history.append({
            'id': id,
            'path': path,
            'url': url,
            'timestamp': time()
        })

        self.history.save()
