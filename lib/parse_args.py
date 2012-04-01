import os
import json
from subprocess import Popen
import webbrowser

from history import History
from screenshot import capture
from settings import *


def parse_args(args, obj, share_to='clipboard'):
    """
    Parse arguments passed to the program
    Arguments:
        args: the array of arguments passed to the program
        function: the function to run when
    Returns:
    """

    # make sure we have some arguments to parse
    if len(args) <= 1:
        print "No arguments specified.\nType 'clipcloud help' for help."
        return

    if args[1] == 'screenshot':
        """
        Take a screenshot and upload it to Dropbox.
        """
        arg = None

        if len(args) > 5:
            x = args[2]
            y = args[3]
            width = args[4]
            height = args[5]
            arg = (x, y, width, height)

        filename = capture(arg)
        path = os.path.join(SCREENSHOT_PATH, filename)

        obj.handle_file(path, filename, share_to)

    elif args[1] == 'file':
        """
        Upload a file to Dropbox
        """
        if len(args) > 2:
            path = args[2]

        else:
            print 'You must specify a file'
            return

        obj.handle_file(path, path, share_to)

    elif args[1] == 'history':
        """
        Display the history of previously uploaded file
        """
        direction = 'd'  # descending
        limit = 10

        if len(args) > 2:
            limit = int(args[2])

            if len(args) > 3 and args[3] in 'ad':
                direction = args[3]

        History().display(limit, direction)

    elif args[1] == 'record':
        """
        Perform operations on previously uploaded files such as
        reuploading or viewing
        """
        if len(args) <= 3:
            print 'please specify the ID number of a file and an operation to perform'
            return

        operation = args[2]

        try:
            id = int(args[3])
        except:
            print 'id must be a positive integer'
            return

        history = json.load(open(HISTORY_PATH))['history']

        if id < len(history):
            record = history[id]
        else:
            print 'No record with that ID exists'
            print 'Highest ID is %d' % len(history)
            print 'Type clipcloud history to see what files you have saved'
            return

        if operation == 'reupload':
            self.handle_file(record['path'], 'a', 'clipboard')

        elif operation == 'open_local':
            Popen(r'explorer /select,"%s"' % record['path'])

        elif operation == 'open_remote':
            webbrowser.open(record['url'], new=2)

    elif args[1] == 'help':
        """Show the help file"""
        print HELP_MESSAGE
