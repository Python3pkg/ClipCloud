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

# path to file in which the Oauth access token for connecting to dropbox is stored
TOKEN_PATH = os.path.join(APP_PATH, 'token.json')
GITHUB_TOKEN_PATH = os.path.join(APP_PATH, 'github_token.json')

# services to send the link to the hosted file to
SHARING_SERVICES = 'clipboard facebook twitter email stdout'.split(' ')

# default message when shared to a social network
SHARE_MESSAGE = 'I just uploaded a file to ClipCloud - check it out.'

# urls of the various services
URLS = {
    'twitter': "https://twitter.com/intent/tweet?text=%s&url=%s",
    'facebook': "http://www.facebook.com/sharer.php?u=%s&t=%s",
    'email': "mailto:?subject=%s&body=%s"
}

HELP_MESSAGE = """
ClipCloud is a program for easily sharing all kinds of stuff
You can send files and folders, or take a screenshot and send that.
You can also send the contents of your clipboard as a text snippet.
When you upload a file, a link to it will be placed in your clipboard,
or you can share it to a social network or send it by email.
"""

DEBUG = True
TIMER_ACTIVATED = True
