""""""

import os
from subprocess import Popen, call
import webbrowser
from time import time

from history import History
from settings import *
from pyjson import PyJson
from clipboard import Clipboard
from dbox import Dropbox


def save_link(link, paths, share_to):
    """
    Save the details of an uploaded file to the history file and send the link to its destination

    Arguments:
    - link: The link to the uploaded file
    - paths: An array of paths to all the files and folders that were uploaded
    - share_to: A string representing the destination of the link - clipboard, social network or stdout
    """
    if not link:
        return

    # save a record of it to the history,
    for path in paths:
        History().add(path, link)

    # and then send the link to its destination, be that clipboard or social network.
    if share_to == 'clipboard':
        Clipboard().set(link)
    elif share_to == 'stdout':
        import sys
        sys.stdout.write(link)
    else:
        url = URLS[share_to] % (SHARE_MESSAGE, link)
        webbrowser.open(url, new=2)


def handle_files(paths, filenames, share_to):
    """
    Respond to the user attempting to upload one or more files or a folders

    Arguments:
    - paths: An array of paths that can point to files or folders
    - filenames: An array of filenames without the full path to them, that corresponds to the files in paths
    - share_to: The service to send the link to the uploaded files to
    """
    in_user_mode = share_to != 'stdout'
    d = Dropbox(in_user_mode=in_user_mode)

    # Start by sorting the paths into two separate arrays for files and folders
    files = []
    folders = []
    non_existent = []

    for path in paths:
        if os.path.exists(path):
            if os.path.isdir(path):
                folders.append(path)
            else:
                files.append(path)
        else:
            non_existent.append(path)

    if len(non_existent) > 0:
        print "Some files or folders you tried to upload don't exist"
        print "They are: %s" % ', '.join(non_existent)
        return

    num_files = len(files)
    num_folders = len(folders)

    # There's a special case if there's one file and no folders,
    # It can be uploaded on its own.
    if num_files == 1 and num_folders == 0:
        file_ = files[0]
        d.upload(file_, filepath=filenames[0])
        link = d.get_link('/' + filenames[0])
        local_paths = [os.path.abspath(file_)]

    # Otherwise it's more complicated.
    # We could have multiple files, one folder, multiple folders, or a mix of files and folders

    # If there's one folder only, we can upload it using its current name
    elif num_folders == 1 and num_files == 0:
        folder = folders[0]
        d.upload_folder(folder)
        link = d.get_link('/' + folder)
        local_paths = [os.path.abspath(folder)]

    # If we've got to here, we have multiple files and folders
    else:
        # create a root folder with a unique name to hold everything we upload
        code = str(int(time()))
        folder_name = 'group_upload_' + code
        d.create_folder(folder_name)

        # Upload all the files to the root folder
        i = 0
        for file_ in files:
            filename = folder_name + '/' + filenames[i]
            d.upload(file_, filepath=filename)
            i += 1

        # Then recursively upload all the folders and their contents to the root folder
        for folder in folders:
            d.upload_folder(folder_name)

        link = d.get_link('/' + d.final_folder_name)
        local_paths = [os.path.abspath(file_) for file_ in files]

    save_link(link, local_paths, share_to)


def screenshot(args):
    """Take a screenshot and upload it to Dropbox."""

    from screenshot import Screenshot

    path, filename = Screenshot().capture(args.mode)
    handle_files([path], [filename], args.share)


def upload(args):
    """Upload the files and folders from the list the user passed in to Dropbox"""

    handle_files(args.filepaths, args.filepaths, args.share)


def snippet(args):
    """Upload the contents of the user's clipboard as a text file"""

    # gist functionality on hold - dropbox works fine for now
    # from gist import Gist

    clipboard = Clipboard().get()
    if clipboard is None:
        return

    filename = 'text_snippet_%d.%s' % (time(), args.extension)
    path = os.path.join(TMP_PATH, filename)

    if args.text == 'dropbox':
        f = open(path, 'w')
        f.write(clipboard)
        f.close()

        handle_files([path], [filename], args.share)

    #elif args.text == 'gist':
    #    Gist().upload(filename, clipboard)


def history(args):
    """Display the history of previously uploaded file"""

    History().display(args.limit, args.sort_by, args.direction, args.start)


def revisit(args):
    """Perform operations on previously uploaded files such as reuploading or viewing"""

    history = PyJson(HISTORY_PATH).doc['history']

    if args.id <= len(history):
        record = history[args.id - 1]
    else:
        print 'No record with that ID exists'
        print 'Highest ID is %d' % len(history)
        print 'Type clipcloud history to see what files you have saved'
        return

    path = record['path']

    if args.operation == 'reupload':
        handle_files([path], [record['filename']], 'clipboard')

    elif args.operation == 'open_local':
        if PLATFORM == 'Windows':
            Popen(r'explorer /select,"%s"' % path)
        elif PLATFORM == 'Darwin':
            call(['open', '-R', path])

    elif args.operation == 'open_remote':
        webbrowser.open(record['url'], new=2)
