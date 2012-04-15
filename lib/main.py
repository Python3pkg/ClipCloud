import os
from subprocess import Popen, call
import webbrowser
from time import time

from history import History
from settings import *
from pyjson import PyJson
from clipboard import Clipboard

# for uploading to Dropbox
from dropbox import Dropbox


def save_link(link, paths, share_to):
    if not link:
        return

    # save a record of it to the history,
    for path in paths:
        History().add(path, link)

    # and then send the link to its destination, be that clipboard or social network.
    if share_to == 'clipboard':
        Clipboard().set(link)
    else:
        url = URLS[share_to] % (SHARE_MESSAGE, link)
        webbrowser.open(url, new=2)


def handle_files(paths, filenames, share_to):
    """
    Respond to the user attempting to upload one or more files or a folders
    Arguments:
    - paths: An array of paths that can point to files or folders
    - share_to: The service to send the link to the uploaded files to
    """
    d = Dropbox()

    # Start by sorting the paths into two separate arrays for files and folders
    files = []
    folders = []
    for path in paths:
        if os.path.isdir(path):
            folders.append(path)
        else:
            files.append(path)
    num_files = len(files)
    num_folders = len(folders)

    # There's a special case if there's one file and no folders,
    # It can be uploaded on its own.
    if num_files == 1 and num_folders == 0:
        _file = files[0]
        d.upload(_file, filepath=filenames[0])
        link = d.get_link('/' + filenames[0])
        local_paths = [_file]

    # Otherwise it's more complicated.
    # We could have multiple files, one folder, multiple folders, or a mix of files and folders

    # If there's one folder only, we can upload it using its current name
    elif num_folders == 1 and num_files == 0:
        folder = folders[0]
        d.upload_folder(folder)
        link = d.get_link('/' + folder)
        local_paths = [folder]

    # If we've got to here, we have multiple files and folders
    else:
        # create a root folder with a unique name to hold everything we upload
        code = str(int(time()))
        folder_name = 'group_upload_' + code
        d.create_folder(folder_name)

        # Upload all the files to the root folder
        i = 0
        for _file in files:
            filename = folder_name + '/' + filenames[i]
            d.upload(_file, filepath=filename)
            i += 1

        # Then recursively upload all the folders and their contents to the root folder
        for folder in folders:
            d.upload_folder(folder_name)

        link = d.get_link('/' + d.final_folder_name)
        local_paths = files

    save_link(link, local_paths, share_to)


def main(args, share_to='clipboard'):
    """
    Parse arguments passed to the program and act upon the results

    Arguments:
    - args: the array of arguments passed to the program
    - share_to: string representing the service to share the file to
    """

    # make sure we have some arguments to parse
    if len(args) <= 1:
        print "No arguments specified.\nType 'clipcloud help' for help."
        return

    if args[1] == 'snap':
        """
        Take a screenshot and upload it to Dropbox.
        """
        from screenshot import Screenshot
        mode = 'screen'
        if len(args) > 2 and args[2] in ['screen', 'draw']:
            mode = args[2]

        path, filename = Screenshot().capture(mode)
        print path, filename

        handle_files([path], [filename], share_to)

    elif args[1] == 'up':
        # Upload the files and folders from the list the user passed in to Dropbox
        if len(args) > 2:
            paths = args[2:]
            handle_files(paths, paths, share_to)
        else:
            print 'You must specify one or more files or folders'

    elif args[1] == 'text':
        # gist functionality on hold - dropbox works fine for now
        # from gist import Gist
        # Upload some the contents of the user's clipboard to Dropbox as a text file
        service = 'dropbox'
        extension = 'txt'  # The Dropbox file viewer has inbuilt syntax highlighting so the file extension is relevant

        if len(args) > 2:
            extension = args[2]

        clipboard = Clipboard().get()

        filename = 'text_snippet_%d.%s' % (time(), extension)
        path = os.path.join(TMP_PATH, filename)

        if service == 'dropbox':
            f = open(path, 'w')
            f.write(clipboard)
            f.close()

            handle_files([path], [filename], share_to)

        #elif service == 'gist':
        #    Gist().upload(filename, clipboard)

        else:
            print 'Not a valid service. Your choices are Dropbox and Github Gists.'

    elif args[1] == 'history':
        # Display the history of previously uploaded file
        direction = 'a'  # ascending
        limit = 10
        sort_by = 'id'
        start = 1

        if len(args) > 2:
            try:
                limit = int(args[2])
            except:
                print 'Limit must be a positive integer'
            if len(args) > 3 and args[3] in 'ad':
                direction = args[3]

                if len(args) > 4 and args[4] in ['id', 'url', 'path', 'timestamp']:
                    sort_by = args[4]

                    if len(args) > 5:
                        try:
                            start = int(args[5])
                        except:
                            print 'Start must be a positive integer'

        History().display(limit, sort_by, direction, start)

    # Do something with a previous file
    elif args[1] == 'revisit':
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
            handle_file([record['path']], [record['path']], 'clipboard')

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
