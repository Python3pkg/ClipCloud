import os
from subprocess import Popen
import webbrowser
from Tkinter import Tk
from time import time

from history import History
from screenshot import capture
from settings import *
from pyjson import PyJson
from gist import Gist


def parse_args(args, obj, share_to='clipboard'):
    """
    Parse arguments passed to the program
    Arguments:
        obj: the instance of the ClipCloud class that called this function
        args: the array of arguments passed to the program
        share_to: the service to share the file to
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

    elif args[1] == 'text':
        service = 'dropbox'

        if service == 'dropbox':
            clipboard = Tk().clipboard_get()
            filename = 'text_snippet_%d.txt' % time()
            path = os.path.join(TMP_PATH, filename)

            f = open(path, 'w')
            f.write(clipboard)
            f.close()

            obj.handle_file(path, filename, share_to)

        elif service == 'gist':
            Gist().upload()

        else:
            print 'Not a valid service. Your choices are Dropbox and Github Gists.'

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

        history = PyJson(HISTORY_PATH).doc['history']

        if id <= len(history):
            record = history[id - 1]
        else:
            print 'No record with that ID exists'
            print 'Highest ID is %d' % len(history)
            print 'Type clipcloud history to see what files you have saved'
            return

        if operation == 'reupload':
            obj.handle_file(record['path'], 'a', 'clipboard')

        elif operation == 'open_local':
            Popen(r'explorer /select,"%s"' % record['path'])

        elif operation == 'open_remote':
            webbrowser.open(record['url'], new=2)

    elif args[1] == 'help':
        """Show the help file"""
        print HELP_MESSAGE

    else:
        print "Not a valid argument. Type clipcloud help to see what's available"
