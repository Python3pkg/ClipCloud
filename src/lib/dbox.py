import webbrowser
import json

from dropbox.session import DropboxSession
from dropbox.client import DropboxClient

from lib.settings import *
from lib.apikeys import *
from lib.message import Message


class Dropbox:
    """Methods for interacting with the Dropbox API"""

    # we only need access to one folder in the user's Dropbox, not the entire thing.
    ACCESS_TYPE = 'app_folder'

    def __init__(self, in_user_mode=True):
        """Connect to the Dropbox servers so that files can be uploaded"""

        self.m = Message(in_user_mode=in_user_mode)

        session = DropboxSession(API_KEY, API_SECRET, self.ACCESS_TYPE)

        # if there is a token saved, that can be used to connect with dropbox
        if os.path.exists(TOKEN_PATH):
            # read the token and authenticate the session with it
            token = json.load(open(TOKEN_PATH))
            session.set_token(token['key'], token['secret'])

        # otherwise we need to authenticate for the first time
        else:
            # request an access token
            request_token = session.obtain_request_token()
            url = session.build_authorize_url(request_token)

            # open the auth page in the user's browser and wait for them to accept
            webbrowser.open(url, new=2)

            print "Press enter once you have authorised the app in your browser"
            raw_input()

            # get a new access token from the authenticated session
            # This will fail if the user didn't visit the above URL and press 'Allow'
            try:
                access_token = session.obtain_access_token(request_token)
            # except RESTSocketError:
            #     if RESTSocketError.ERRNO == 10061:
            #         print "Could not connect to the Dropbox servers \
            #             because your network's proxy blocked it."
            except Exception as error:
                if DEBUG:
                    print error
                print "You didn't authorise the app, or something else went wrong"
                print "Either way we can't continue"
                return

            # save the access token to a file so that next time we don't have to authenticate
            f = open(TOKEN_PATH, 'w+')
            f.write(json.dumps({'key': access_token.key, 'secret': access_token.secret}))
            f.close()

        # create a client from the finished session
        client = DropboxClient(session)

        self.client = client

    def upload(self, path, filepath=None):
        """
        Upload a file to the Dropbox servers

        Arguments:
        - path: The path to the local copy of the file to be uploaded
        - filename: The path, including the filename given to the remote copy of the file
            once it is uploaded to Dropbox. If omitted it defaults to being the same as path
        """

        if self.client is None:
            print 'Please authenticate with Dropbox before trying to upload.'
            return

        if filepath is None:
            filepath = path
        filepath = '/' + filepath

        try:
            self.m.message('Uploading...')
            # Open the file located at path and upload it to the dropbox servers
            response = self.client.put_file(filepath, open(path, 'rb'))
            self.m.message('Upload finished')
        except Exception as error:
            self.m.message('Upload failed')
            if DEBUG:
                print error
            return

        if DEBUG:
            self.m.message(path)
            self.m.message(response)

    def upload_folder(self, folder):
        """
        Upload a folder to the Dropbox servers

        Arguments:
        - folder: A string representing the path to the folder to be uploaded
        """

        # Create a folder in the user's Dropbox with the same name as the local folder
        self.create_folder(folder)

        # Recursively iterate through the contents of the folder
        for dirname, dirnames, filenames in os.walk(folder):
            # Create subfolders on Dropbox for each local subfolder
            for subdirname in dirnames:
                f = dirname + '/' + subdirname
                self.create_folder(f)

            # Upload each local file
            for filename in filenames:
                self.upload(dirname + '/' + filename, filepath=self.final_folder_name + '/' + filename)

    def get_link(self, filename):
        """
        Get the URL of the copy of a file or folder hosted on Dropbox

        Arguments:
        - filename: The path to the file or folder within the user's Dropbox to get the URL of

        Returns: A string containing the URL, in the format http://db.tt/xxxxxxxx
        """
        return self.client.share(filename)['url']

    def create_folder(self, folder_name, num=1):
        """
        Create a folder in the user's Dropbox

        Arguments:
        - folder_name: The name of the folder to create
        - num: The number to append to the folder name if a folder with the specified name already exists
        """

        new_folder_name = folder_name

        # Try to create a folder with the given name
        try:
            if num > 1:
                new_folder_name += '_(' + str(num) + ')'

            self.client.file_create_folder('/' + new_folder_name)

            if num > 1:
                print 'Warning: a folder with that name already exists. Renaming to ' + new_folder_name

            self.final_folder_name = new_folder_name

        except ErrorResponse as e:
            if e.status == 403:
                # It failed because a folder with that name already exists
                # Increment a number and append it to the folder name
                # then call the function recursively until it works
                self.create_folder(folder_name, num=num + 1)
