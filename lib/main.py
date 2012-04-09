import os
from subprocess import Popen, call
import webbrowser
from time import time

from history import History
from screenshot import capture
from settings import *
from pyjson import PyJson
# gist functionality on hold - dropbox works fine for now
# from gist import Gist
from clipboard import Clipboard

# for uploading to Dropbox
from dropbox.dropbox import Dropbox


def handle_file(path, filename, share_to):
    """
    Respond to the event of the user attempting to upload a file,
    be it a screenshot, text snippet or generic file.
    """
    # upload the file,
    link = Dropbox().upload(path, filename)

    if not link:
        return

    # save a record of it to the history,
    History().add(path, link)

    # and then send the link to its destination, be that clipboard or social network.
    if share_to == 'clipboard':
        Clipboard().set(link)
        return

    url = URLS[share_to] % (SHARE_MESSAGE, link)

    webbrowser.open(url, new=2)


def main(args, share_to='clipboard'):
    """
    Parse arguments passed to the program and act upon the results
    Arguments:
        args: the array of arguments passed to the program
        share_to: string representing the service to share the file to
    """

    # make sure we have some arguments to parse
    if len(args) <= 1:
        print "No arguments specified.\nType 'clipcloud help' for help."
        return

        # Take a screenshot
    if args[1] == 'screenshot':
        """
        Take a screenshot and upload it to Dropbox.
        """
        if len(args) > 2 and args[2] in ['screen', 'draw']:
            mode = args[2]
        else:
            mode = 'screen'

        if mode == 'screen':
            filename = capture()
            path = os.path.join(SCREENSHOT_PATH, filename)
        elif mode == 'draw':
            call('C:/Windows/system32/SnippingTool.exe')

        handle_file(path, filename, share_to)

    # Upload a file
    elif args[1] == 'file':
        """
        Upload a file to Dropbox
        """
        if len(args) > 2:
            path = args[2]

        else:
            print 'You must specify a file'
            return

        handle_file(path, path, share_to)

    # Upload some text
    elif args[1] == 'text':
        service = 'dropbox'
        extension = 'txt'

        if len(args) > 2:
            extension = args[2]

        clipboard = Clipboard().get()

        filename = 'text_snippet_%d.%s' % (time(), extension)
        path = os.path.join(TMP_PATH, filename)

        if service == 'dropbox':
            f = open(path, 'w')
            f.write(clipboard)
            f.close()

            handle_file(path, filename, share_to)

        #elif service == 'gist':
        #    Gist().upload(filename, clipboard)

        else:
            print 'Not a valid service. Your choices are Dropbox and Github Gists.'

    # Display the history
    elif args[1] == 'history':
        """
        Display the history of previously uploaded file
        """
        direction = 'a'  # ascending
        limit = 10
        sort_by = 'id'

        if len(args) > 2:
            limit = int(args[2])

            if len(args) > 3 and args[3] in 'ad':
                direction = args[3]

                if len(args) > 4 and args[4] in ['id', 'url', 'path', 'timestamp']:
                    sort_by = args[4]

        print sort_by
        History().display(limit, sort_by, direction)

    # Do something with a previous file
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
            handle_file(record['path'], 'a', 'clipboard')

        elif operation == 'open_local':
            if PLATFORM == 'Windows':
                Popen(r'explorer /select,"%s"' % record['path'])
            elif PLATFORM == 'Darwin':
                call(["open", "-R", record['path']])

        elif operation == 'open_remote':
            webbrowser.open(record['url'], new=2)

    # Show help
    elif args[1] == 'help':
        """Show the help file"""
        print HELP_MESSAGE

    else:
        print "Not a valid argument. Type clipcloud help to see what's available"
