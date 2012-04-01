import os

# name of the app.
APP_NAME = "ClipCloud"
# root folder in AppData for storing data
APP_PATH = os.path.join(os.environ['APPDATA'], APP_NAME)
# folder for storing screenshots
SCREENSHOT_PATH = os.path.join(APP_PATH, 'img')
# file to store history in
HISTORY_PATH = os.path.join(APP_PATH, 'history.json')
# path to c# utility script
UTILS_SCRIPT = os.path.join(os.path.dirname(__file__), '../clipcloud.exe')
# path to file in which the Oauth access token for connecting to dropbox is stored
TOKEN_PATH = os.path.join(APP_PATH, 'token.json')

HELP_MESSAGE = """
ClipCloud is a program for easily sending files to your friends
You can send an existing file, or take a screenshot and send that.
When you upload a file, a link to it will be placed in your clipboard

Options:
    help: display this help file.
    file /path/to/file: upload the specified file
    screenshot [top, left, width, height]: take a screenshot and upload it.
        If no arguments are specified, the enitre primary screen is used.
    history [number_of_items]: show a history of the files you've uploaded previously.
        defaults to the last 10 records.
    record operation id: Do something with a previously uploaded file.
        ID specifies which file to upload
        operation can be either reupload, open_remote or open_local
"""

DEBUG = True
