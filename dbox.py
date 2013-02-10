import webbrowser

from dropbox.session import DropboxSession
from dropbox.client import DropboxClient

from settings import *
from message import Message
from pyjson import PyJson


class Dropbox:
    """Methods for interacting with the Dropbox API"""

    # Access is only needed to one folder in the user's Dropbox
    ACCESS_TYPE = 'app_folder'

    def __init__(self, in_user_mode=True):
        """Connect to the Dropbox servers so that files can be uploaded"""

        self.m = Message(in_user_mode=in_user_mode)

        session = DropboxSession(API_KEY, API_SECRET, self.ACCESS_TYPE)

        token_file = PyJson(TOKEN_PATH)
        token = token_file.doc

        # If there is a token saved, that can be used to connect with Dropbox
        if 'key' in token and 'secret' in token:
            # Read the token and authenticate the session with it
            session.set_token(token['key'], token['secret'])

        # Otherwise it is necessary to authenticate for the first time
        else:
            # Request an access token
            request_token = session.obtain_request_token()
            url = session.build_authorize_url(request_token)

            # Open the authentication page in the user's browser and wait for them to accept
            webbrowser.open(url, new=2)

            print "Press enter once you have authorised the app in your browser"
            raw_input()

            # Get a new access token from the authenticated session
            # This will fail if the user didn't visit the above URL and press 'Allow'
            try:
                access_token = session.obtain_access_token(request_token)

            except Exception as error:
                if DEBUG:
                    print error
                print "You didn't authorise the app, or something else went wrong"
                exit(1)

            # Save the access token to a file so that authentication is not needed next time the app is run
            token_file.add('key', access_token.key)
            token_file.add('secret', access_token.secret)
            token_file.save()

        # Create a Dropbox client from the session
        client = DropboxClient(session)

        self.client = client

    def upload(self, path, filepath=None):
        """
        Upload a file to the Dropbox servers

        path - The path to the local copy of the file to be uploaded
        filepath - The path, including the filename given to the remote copy of the file
                   once it is uploaded to Dropbox. If omitted it defaults to be the same as path
        """

        if self.client is None:
            print 'Please authenticate with Dropbox before trying to upload.'
            return

        if filepath is None:
            filepath = path
        filepath = '/' + filepath

        try:
            self.m.message('Uploading...')
            # Open the file located at path and upload it to the Dropbox servers
            response = self.client.put_file(filepath, open(path, 'rb'))
            self.m.message('Upload finished')

        except Exception as error:
            self.m.message('Upload failed', 2)
            if DEBUG:
                self.m.message(error, 2)
            return

        if DEBUG:
            self.m.message(path)
            self.m.message(response)

    def upload_folder(self, folder):
        """
        Upload a folder to the Dropbox servers

        folder - A string representing the path to the folder to be uploaded
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
        Get the URL of the Dropbox-hosted copy of a file or folder

        filename - The path to the file or folder within the user's Dropbox

        Returns the URL as a string in the format http://db.tt/xxxxxxxx
        """
        return self.client.share(filename)['url']

    def create_folder(self, folder_name, num=1):
        """
        Create a folder in the user's Dropbox

        folder_name - The name of the folder to create
        num - The number to append to the folder name if a folder with the specified name already exists
        """

        new_folder_name = folder_name

        if num > 1:
            new_folder_name += '_(%s)' % num
        # Try to create a folder with the given name
        try:
            self.client.file_create_folder('/' + new_folder_name)

            if num > 1:
                print 'Warning: a folder with that name already exists. Renaming to ' + new_folder_name

            self.final_folder_name = new_folder_name

        except ErrorResponse as e:
            if e.status == 403:
                # It failed because a folder with that name already exists
                # Increment a number to be appended to the folder name
                # then call the function recursively until it works
                num += 1
                self.create_folder(folder_name, num=num)
