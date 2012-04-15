from lib.settings import HISTORY_PATH
from time import time
from datetime import date
from pyjson import PyJson
import subprocess


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
        - limit: the number of items to show
        - direction: the order to sort the files in to, (ascending or descending)
        - sort_by: the value to sort by (id, path, url or date)
        - start: the record number to start at
        """

        history = sorted(self.history.doc['history'], key=lambda k: k[sort_by], reverse=direction == 'd')

        header = ['Id', 'URL', 'Local File', 'Date Created']
        widths = [len(thing) for thing in header]
        grid = [header]

        # iterate through the array of records, parse them and create a new 2d array of the formatted values
        for record in history[start - 1:]:
            if limit == 0:
                break

            _id = str(record['id'])
            url = record['url']
            path = record['path']
            _date = date.fromtimestamp(record['timestamp']).strftime('%d/%m/%Y')

            row = [_id, url, path, _date]

            # find the longest cell in the column so the minimum width is known
            # python's zip() function would be a cleaner way to do this than incrementing a variable
            # but for some reason it didn't work as expected
            i = 0
            for thing in row:
                length = len(thing)
                if length > widths[i]:
                    widths[i] = length
                i += 1

            grid.append(row)

            limit -= 1

        gridstring = '\n'
        total = sum(widths)

        # try to determine the width of the user's terminal window in characters
        # so the rows can be truncated if they are too long
        try:
            terminal_width = int(subprocess.check_output('stty size').split()[1])
        except:
            print 'The size of your terminal window could not be determined'
            print 'The layout of the grid below may be broken due to text wrapping'
            terminal_width = 80  # default width for a lot of systems

        # if the grid is wider than the terminal window work out the difference between them
        # this is the amount to truncate the grid by
        needs_truncating = False
        if total > terminal_width:
            terminal_diff = terminal_width - total - 12  # 12 is the number of dividers and spaces added
            needs_truncating = True
            widths[2] += terminal_diff  # reduce the width of the column by the difference

        for row in grid:
            i = 0
            rowstring = ''

            for cell in row:
                # truncate this column if the table would be wider than the terminal window
                # id, url and date don't vary much in width, only the local path is worth truncating
                if i == 2 and needs_truncating and len(cell) > widths[2]:
                    cell = cell[:terminal_diff - 3] + '...'

                # pad with spaces so all cells in the column are the same width
                diff = widths[i] - len(cell)
                padding = ' ' * diff
                cell = ' ' + cell + padding

                rowstring += cell + ' |'  # add a divider between columns

                i += 1

            rowstring = rowstring[:-2]  # trim the last space and divider
            gridstring += rowstring + '\n'  # add the row to the final grid

            # add a horizontal divider only below the header
            if row == header:
                gridstring += '-' * len(rowstring) + '\n'

        print gridstring[:-1]  # trim the last line break

    def add(self, path, url):
        """
        Write a new record to the history
        Arguments:
        - path: the path to the local copy of the file that was uploaded
        - url: the shortened URl that points to the copy of the file hosted on the users dropbox acount
        """
        history = self.history.doc['history']

        id = 1 if len(history) == 0 else history[-1]['id'] + 1

        history.append({
            'id': id,
            'path': path,
            'url': url,
            'timestamp': time()
        })

        self.history.save()
