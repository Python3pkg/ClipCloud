import os
from platform import system

PLATFORM = system()

# Name of the app
APP_NAME = "ClipCloud"

# Root directory for storing application data
if PLATFORM == 'Darwin':
    APP_PATH = os.path.join(os.path.expanduser('~'), 'Library/Application Support/' + APP_NAME)
elif PLATFORM == 'Windows':
    APP_PATH = os.path.join(os.environ['APPDATA'], APP_NAME)
elif PLATFORM == 'Linux':
    APP_PATH = os.path.expanduser(os.path.join('~', '.' + APP_NAME))

# Directory for storing screenshots
SCREENSHOT_PATH = os.path.join(APP_PATH, 'img')

# Directory for storing temporary files
TMP_PATH = os.path.join(APP_PATH, 'tmp')

# File to write history data to
HISTORY_PATH = os.path.join(APP_PATH, 'history.json')

# Path to file in which the OAuth access token for connecting to Dropbox is stored
TOKEN_PATH = os.path.join(APP_PATH, 'token.json')
GITHUB_TOKEN_PATH = os.path.join(APP_PATH, 'github_token.json')

API_KEY = "rvml2qyo081dvmn"
API_SECRET = "toe9kimrkhd4bx7"

# Services to send the link to the hosted file to
SHARING_SERVICES = ['clipboard', 'facebook', 'twitter', 'email', 'stdout']

# Default message when shared to a social network
SHARE_MESSAGE = 'I just uploaded a file to ClipCloud - check it out.'

# URLs of the various sharing services
URLS = {
    'twitter': "https://twitter.com/intent/tweet?text=%s&url=%s",
    'facebook': "http://www.facebook.com/sharer.php?u=%s&t=%s",
    'email': "mailto:?subject=%s&body=%s"
}

HELP_MESSAGE = '''ClipCloud is a program for easily sharing all kinds of stuff.
You can send files and folders, or take a screenshot and send that.
You can also send the contents of your clipboard as a text snippet.
When you upload a file, a link to it will be placed in your clipboard, or you can share it to a social network or send it by email.'''

DEBUG = True
