from lib.settings import HISTORY_PATH
from time import time
from datetime import date
from pyjson import PyJson
from gridformat import format_grid


class History:
    """
    Defines methods for interacting with the file that stores
    a history of the files that the user has uploaded to the service
    """

    def __init__(self):
        self.history = PyJson(HISTORY_PATH, base={'history': []})

    def display(self, limit, sort_by, direction, start):
        """
        Load the history and print out a number of records to the screen.

        Arguments:
        - limit: The number of items to show
        - direction: The order to sort the files in to, (ascending or descending)
        - sort_by: The value to sort by (id, path, url or date)
        - start: The record number to start at
        """

        history = sorted(self.history.doc['history'], key=lambda k: k[sort_by], reverse=direction == 'd')
        grid = [['Id', 'URL', 'Local File', 'Date Created']]

        # iterate through the array of records, parse them and create a new 2d array of the formatted values
        for record in history[start - 1:]:
            if limit == 0:
                break

            id_ = str(record['id'])
            url = record['url']
            path = record['path']
            date_ = date.fromtimestamp(record['timestamp']).strftime('%d/%m/%Y')

            row = [id_, url, path, date_]

            grid.append(row)

            limit -= 1

        print format_grid(grid, divider_positions=[1], truncatable_column=2)

    def add(self, path, url, filename=None):
        """
        Write a new record to the history

        Arguments:
        - path: The path to the local copy of the file that was uploaded
        - url: The shortened URL that points to the copy of the file hosted on the user's Dropbox account
        """

        history = self.history.doc['history']

        if filename is None:
            filename = path
        id_ = 1 if len(history) == 0 else history[-1]['id'] + 1
        record = {
            'id': id_,
            'path': path,
            'filename': filename,
            'url': url,
            'timestamp': time()
        }

        history.append(record)
        self.history.save()
