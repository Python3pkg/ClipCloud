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

DEBUG = True
