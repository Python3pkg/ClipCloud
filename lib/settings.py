import os
from platform import system

PLATFORM = system()

# name of the app.
APP_NAME = "ClipCloud"

# root folder in AppData for storing data
if PLATFORM == 'Darwin':
    APP_PATH = os.path.join(os.path.expanduser('~'), 'Library/Application Support/' + APP_NAME)
else:
    APP_PATH = os.path.join(os.environ['APPDATA'], APP_NAME)

# folder for storing screenshots
SCREENSHOT_PATH = os.path.join(APP_PATH, 'img')

# folder for temporary files
TMP_PATH = os.path.join(APP_PATH, 'tmp')

# file to store history in
HISTORY_PATH = os.path.join(APP_PATH, 'history.json')

# path to c# utility script
UTILS_SCRIPT = os.path.join(os.path.dirname(__file__), '../clipcloud.exe')
SNIPPING_TOOL = os.path.join(os.path.dirname(__file__), '../snip.exe')

# path to file in which the Oauth access token for connecting to dropbox is stored
TOKEN_PATH = os.path.join(APP_PATH, 'token.json')
GITHUB_TOKEN_PATH = os.path.join(APP_PATH, 'github_token.json')

# services to send the link to the hosted file to
SHARING_SERVICES = 'clipboard facebook twitter email'.split(' ')

# default message when shared to a social network
SHARE_MESSAGE = 'I just uploaded a file to ClipCloud - check it out.'

# urls of the various services
URLS = {
    'twitter': "https://twitter.com/intent/tweet?text=%s&url=%s",
    'facebook': "http://www.facebook.com/sharer.php?u=%s&t=%s",
    'email': "mailto:?subject=%s&body=%s"
}

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
