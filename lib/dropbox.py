"""The Dropbox API and several methods to abstract common operations"""

import re
import simplejson as json
import httplib
import os
import pkg_resources
import socket
import ssl
import urllib
import urlparse
import oauth
import webbrowser
from lib.settings import *
from lib.message import Message


def format_path(path):
    """Normalize path for use with the Dropbox API.

    This function turns multiple adjacent slashes into single
    slashes, then ensures that there's a leading slash but
    not a trailing slash.
    """
    if not path:
        return path

    path = re.sub(r'/+', '/', path)

    if path == '/':
        return ""
    else:
        return '/' + path.strip('/')


class Dropbox:
    """Methods for interacting with the Dropbox API"""

    # we only need access to one folder in the user's Dropbox, not the entire thing.
    ACCESS_TYPE = 'app_folder'

    def __init__(self, in_user_mode=True):
        """Connect to the Dropbox servers so that files can be uploaded"""

        self.m = Message(in_user_mode=in_user_mode)

        api_details = json.load(open('lib/api.json'))['dropbox']
        session = DropboxSession(api_details['key'], api_details['secret'], self.ACCESS_TYPE)

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
        #print client.account_info()

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
        return self.client.share('/' + filename)['url']

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

        # If it fails because a folder with that name already exists
        # then increment a number, append it to the folder name
        # and call the function recursively until it works
        except ErrorResponse as e:
            if e.status == 403:
                self.create_folder(folder_name, num=num + 1)

"""
The main client API you'll be working with most often.  You'll need to
configure a dropbox.session.DropboxSession for this to work, but otherwise
it's fairly self-explanatory.
"""


class DropboxClient(object):
    """
    The main access point of doing REST calls on Dropbox. You should
    first create and configure a dropbox.session.DropboxSession object,
    and then pass it into DropboxClient's constructor. DropboxClient
    then does all the work of properly calling each API method
    with the correct OAuth authentication.

    You should be aware that any of these methods can raise a
    rest.ErrorResponse exception if the server returns a non-200
    or invalid HTTP response. Note that a 401 return status at any
    point indicates that the user needs to be reauthenticated.
    """

    def __init__(self, session, proxy_host=None, proxy_port=None):
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        """Initialize the DropboxClient object.

        Args:
            session: A dropbox.session.DropboxSession object to use for making requests.
        """
        self.session = session

    def request(self, target, params=None, method='POST', content_server=False):
        """Make an HTTP request to a target API method.

        This is an internal method used to properly craft the url, headers, and
        params for a Dropbox API request.  It is exposed for you in case you
        need craft other API calls not in this library or if you want to debug it.

        Args:
            target: The target URL with leading slash (e.g. '/files')
            params: A dictionary of parameters to add to the request
            method: An HTTP method (e.g. 'GET' or 'POST')
            content_server: A boolean indicating whether the request is to the
               API content server, for example to fetch the contents of a file
               rather than its metadata.

        Returns:
            A tuple of (url, params, headers) that should be used to make the request.
            OAuth authentication information will be added as needed within these fields.
        """
        assert method in ['GET','POST', 'PUT'], "Only 'GET', 'POST', and 'PUT' are allowed."
        if params is None:
            params = {}

        host = self.session.API_CONTENT_HOST if content_server else self.session.API_HOST
        base = self.session.build_url(host, target)
        headers, params = self.session.build_access_headers(method, base, params)

        if method in ('GET', 'PUT'):
            url = self.session.build_url(host, target, params)
        else:
            url = self.session.build_url(host, target)

        return url, params, headers


    def account_info(self):
        """Retrieve information about the user's account.

        Returns:
            A dictionary containing account information.

            For a detailed description of what this call returns, visit:
            https://www.dropbox.com/developers/docs#account-info
        """
        url, params, headers = self.request("/account/info", method='GET')

        return RESTClient.GET(url, headers)


    def put_file(self, full_path, file_obj, overwrite=False, parent_rev=None):
        """Upload a file.

        Args:
            full_path: The full path to upload the file to, *including the file name*.
                If the destination directory does not yet exist, it will be created.
            file_obj: A file-like object to upload. If you would like, you can pass a string as file_obj.
            overwrite: Whether to overwrite an existing file at the given path. [default False]
                If overwrite is False and a file already exists there, Dropbox
                will rename the upload to make sure it doesn't overwrite anything.
                You need to check the metadata returned for the new name.
                This field should only be True if your intent is to potentially
                clobber changes to a file that you don't know about.
            parent_rev: The rev field from the 'parent' of this upload. [optional]
                If your intent is to update the file at the given path, you should
                pass the parent_rev parameter set to the rev value from the most recent
                metadata you have of the existing file at that path. If the server
                has a more recent version of the file at the specified path, it will
                automatically rename your uploaded file, spinning off a conflict.
                Using this parameter effectively causes the overwrite parameter to be ignored.
                The file will always be overwritten if you send the most-recent parent_rev,
                and it will never be overwritten if you send a less-recent one.

        Returns:
            A dictionary containing the metadata of the newly uploaded file.

            For a detailed description of what this call returns, visit:
            https://www.dropbox.com/developers/docs#files-put

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of
               400: Bad request (may be due to many things; check e.error for details)
               503: User over quota

        Note: In Python versions below version 2.6, httplib doesn't handle file-like objects.
            In that case, this code will read the entire file into memory (!).
        """
        path = "/files_put/%s%s" % (self.session.root, format_path(full_path))

        params = {
            'overwrite': bool(overwrite),
            }

        if parent_rev is not None:
            params['parent_rev'] = parent_rev

        url, params, headers = self.request(path, params, method='PUT', content_server=True)

        return RESTClient.PUT(url, file_obj, headers)

    def get_file(self, from_path, rev=None):
        """Download a file.

        Unlike most other calls, get_file returns a raw HTTPResponse with the connection open.
        You should call .read() and perform any processing you need, then close the HTTPResponse.

        Args:
            from_path: The path to the file to be downloaded.
            rev: A previous rev value of the file to be downloaded. [optional]

        Returns:
            An httplib.HTTPResponse that is the result of the request.

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of
               400: Bad request (may be due to many things; check e.error for details)
               404: No file was found at the given path, or the file that was there was deleted.
               200: Request was okay but response was malformed in some way.
        """
        path = "/files/%s%s" % (self.session.root, format_path(from_path))

        params = {}
        if rev is not None:
            params['rev'] = rev

        url, params, headers = self.request(path, params, method='GET', content_server=True)
        return RESTClient.request("GET", url, headers=headers, raw_response=True)

    def get_file_and_metadata(self, from_path, rev=None):
        """Download a file alongwith its metadata.

        Acts as a thin wrapper around get_file() (see get_file() comments for
        more details)

        Args:
            from_path: The path to the file to be downloaded.
            rev: A previous rev value of the file to be downloaded. [optional]

        Returns:
            - An httplib.HTTPResponse that is the result of the request.
            - A dictionary containing the metadata of the file (see
              https://www.dropbox.com/developers/docs#metadata for details).

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of
               400: Bad request (may be due to many things; check e.error for details)
               404: No file was found at the given path, or the file that was there was deleted.
               200: Request was okay but response was malformed in some way.
        """
        file_res = self.get_file(from_path, rev)
        metadata = DropboxClient.__parse_metadata_as_dict(file_res)

        return file_res, metadata

    @staticmethod
    def __parse_metadata_as_dict(dropbox_raw_response):
        """Parses file metadata from a raw dropbox HTTP response, raising a
        dropbox.rest.ErrorResponse if parsing fails.
        """
        metadata = None
        for header, header_val in dropbox_raw_response.getheaders():
            if header.lower() == 'x-dropbox-metadata':
                try:
                    metadata = json.loads(header_val)
                except ValueError:
                    raise ErrorResponse(dropbox_raw_response)
        if not metadata: raise ErrorResponse(dropbox_raw_response)
        return metadata

    def file_copy(self, from_path, to_path):
        """Copy a file or folder to a new location.

        Args:
            from_path: The path to the file or folder to be copied.

            to_path: The destination path of the file or folder to be copied.
                This parameter should include the destination filename (e.g.
                from_path: '/test.txt', to_path: '/dir/test.txt'). If there's
                already a file at the to_path, this copy will be renamed to
                be unique.

        Returns:
            A dictionary containing the metadata of the new copy of the file or folder.

            For a detailed description of what this call returns, visit:
            https://www.dropbox.com/developers/docs#fileops-copy

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of:

            - 400: Bad request (may be due to many things; check e.error for details)
            - 404: No file was found at given from_path.
            - 503: User over storage quota.
        """
        params = {'root': self.session.root,
                  'from_path': format_path(from_path),
                  'to_path': format_path(to_path),
                  }

        url, params, headers = self.request("/fileops/copy", params)

        return RESTClient.POST(url, params, headers)


    def file_create_folder(self, path):
        """Create a folder.

        Args:
            path: The path of the new folder.

        Returns:
            A dictionary containing the metadata of the newly created folder.

            For a detailed description of what this call returns, visit:
            https://www.dropbox.com/developers/docs#fileops-create-folder

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of
               400: Bad request (may be due to many things; check e.error for details)
               403: A folder at that path already exists.
        """
        params = {'root': self.session.root, 'path': format_path(path)}

        url, params, headers = self.request("/fileops/create_folder", params)

        return RESTClient.POST(url, params, headers)


    def file_delete(self, path):
        """Delete a file or folder.

        Args:
            path: The path of the file or folder.

        Returns:
            A dictionary containing the metadata of the just deleted file.

            For a detailed description of what this call returns, visit:
            https://www.dropbox.com/developers/docs#fileops-delete

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of

            - 400: Bad request (may be due to many things; check e.error for details)
            - 404: No file was found at the given path.
        """
        params = {'root': self.session.root, 'path': format_path(path)}

        url, params, headers = self.request("/fileops/delete", params)

        return RESTClient.POST(url, params, headers)


    def file_move(self, from_path, to_path):
        """Move a file or folder to a new location.

        Args:
            from_path: The path to the file or folder to be moved.
            to_path: The destination path of the file or folder to be moved.
            This parameter should include the destination filename (e.g.
            from_path: '/test.txt', to_path: '/dir/test.txt'). If there's
            already a file at the to_path, this file or folder will be renamed to
            be unique.

        Returns:
            A dictionary containing the metadata of the new copy of the file or folder.

            For a detailed description of what this call returns, visit:
            https://www.dropbox.com/developers/docs#fileops-move

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of

            - 400: Bad request (may be due to many things; check e.error for details)
            - 404: No file was found at given from_path.
            - 503: User over storage quota.
        """
        params = {'root': self.session.root, 'from_path': format_path(from_path), 'to_path': format_path(to_path)}

        url, params, headers = self.request("/fileops/move", params)

        return RESTClient.POST(url, params, headers)


    def metadata(self, path, list=True, file_limit=10000, hash=None, rev=None, include_deleted=False):
        """Retrieve metadata for a file or folder.

        Args:
            path: The path to the file or folder.

            list: Whether to list all contained files (only applies when
                path refers to a folder).
            file_limit: The maximum number of file entries to return within
                a folder. If the number of files in the directory exceeds this
                limit, an exception is raised. The server will return at max
                10,000 files within a folder.
            hash: Every directory listing has a hash parameter attached that
                can then be passed back into this function later to save on\
                bandwidth. Rather than returning an unchanged folder's contents,\
                the server will instead return a 304.\
            rev: The revision of the file to retrieve the metadata for. [optional]
                This parameter only applies for files. If omitted, you'll receive
                the most recent revision metadata.

        Returns:
            A dictionary containing the metadata of the file or folder
            (and contained files if appropriate).

            For a detailed description of what this call returns, visit:
            https://www.dropbox.com/developers/docs#metadata

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of

            - 304: Current directory hash matches hash parameters, so contents are unchanged.
            - 400: Bad request (may be due to many things; check e.error for details)
            - 404: No file was found at given path.
            - 406: Too many file entries to return.
        """
        path = "/metadata/%s%s" % (self.session.root, format_path(path))

        params = {'file_limit': file_limit,
                  'list': 'true',
                  'include_deleted': include_deleted,
                  }

        if not list:
            params['list'] = 'false'
        if hash is not None:
            params['hash'] = hash
        if rev:
            params['rev'] = rev

        url, params, headers = self.request(path, params, method='GET')

        return RESTClient.GET(url, headers)

    def thumbnail(self, from_path, size='large', format='JPEG'):
        """Download a thumbnail for an image.

        Unlike most other calls, thumbnail returns a raw HTTPResponse with the connection open.
        You should call .read() and perform any processing you need, then close the HTTPResponse.

        Args:
            from_path: The path to the file to be thumbnailed.
            size: A string describing the desired thumbnail size.
               At this time, 'small', 'medium', and 'large' are
               officially supported sizes (32x32, 64x64, and 128x128
               respectively), though others may be available. Check
               https://www.dropbox.com/developers/docs#thumbnails for
               more details.

        Returns:
            An httplib.HTTPResponse that is the result of the request.

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of

            - 400: Bad request (may be due to many things; check e.error for details)
            - 404: No file was found at the given from_path, or files of that type cannot be thumbnailed.
            - 415: Image is invalid and cannot be thumbnailed.
        """
        assert format in ['JPEG', 'PNG'], "expected a thumbnail format of 'JPEG' or 'PNG', got %s" % format

        path = "/thumbnails/%s%s" % (self.session.root, format_path(from_path))

        url, params, headers = self.request(path, {'size': size}, method='GET', content_server=True)
        return RESTClient.request("GET", url, headers=headers, raw_response=True)

    def thumbnail_and_metadata(self, from_path, size='large', format='JPEG'):
        """Download a thumbnail for an image alongwith its metadata.

        Acts as a thin wrapper around thumbnail() (see thumbnail() comments for
        more details)

        Args:
            from_path: The path to the file to be thumbnailed.
            size: A string describing the desired thumbnail size. See thumbnail()
               for details.

        Returns:
            - An httplib.HTTPResponse that is the result of the request.
            - A dictionary containing the metadata of the file whose thumbnail
              was downloaded (see https://www.dropbox.com/developers/docs#metadata
              for details).

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of

            - 400: Bad request (may be due to many things; check e.error for details)
            - 404: No file was found at the given from_path, or files of that type cannot be thumbnailed.
            - 415: Image is invalid and cannot be thumbnailed.
            - 200: Request was okay but response was malformed in some way.
        """
        thumbnail_res = self.thumbnail(from_path, size, format)
        metadata = DropboxClient.__parse_metadata_as_dict(thumbnail_res)

        return thumbnail_res, metadata

    def search(self, path, query, file_limit=1000, include_deleted=False):
        """Search directory for filenames matching query.

        Args:
            path: The directory to search within.

            query: The query to search on (minimum 3 characters).

            file_limit: The maximum number of file entries to return within a folder.
               The server will return at max 1,000 files.

            include_deleted: Whether to include deleted files in search results.

        Returns:
            A list of the metadata of all matching files (up to
            file_limit entries).  For a detailed description of what
            this call returns, visit:
            https://www.dropbox.com/developers/docs#search

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of
            400: Bad request (may be due to many things; check e.error
            for details)
        """
        path = "/search/%s%s" % (self.session.root, format_path(path))

        params = {
            'query': query,
            'file_limit': file_limit,
            'include_deleted': include_deleted,
            }

        url, params, headers = self.request(path, params)

        return RESTClient.POST(url, params, headers)

    def revisions(self, path, rev_limit=1000):
        """Retrieve revisions of a file.

        Args:
            path: The file to fetch revisions for. Note that revisions
                are not available for folders.
            rev_limit: The maximum number of file entries to return within
                a folder. The server will return at max 1,000 revisions.

        Returns:
            A list of the metadata of all matching files (up to rev_limit entries).

            For a detailed description of what this call returns, visit:
            https://www.dropbox.com/developers/docs#revisions

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of

            - 400: Bad request (may be due to many things; check e.error for details)
            - 404: No revisions were found at the given path.
        """
        path = "/revisions/%s%s" % (self.session.root, format_path(path))

        params = {
            'rev_limit': rev_limit,
            }

        url, params, headers = self.request(path, params, method='GET')

        return RESTClient.GET(url, headers)

    def restore(self, path, rev):
        """Restore a file to a previous revision.

        Args:
            path: The file to restore. Note that folders can't be restored.
            rev: A previous rev value of the file to be restored to.

        Returns:
            A dictionary containing the metadata of the newly restored file.

            For a detailed description of what this call returns, visit:
            https://www.dropbox.com/developers/docs#restore

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of

            - 400: Bad request (may be due to many things; check e.error for details)
            - 404: Unable to find the file at the given revision.
        """
        path = "/restore/%s%s" % (self.session.root, format_path(path))

        params = {
            'rev': rev,
            }

        url, params, headers = self.request(path, params)

        return RESTClient.POST(url, params, headers)

    def media(self, path):
        """Get a temporary unauthenticated URL for a media file.

        All of Dropbox's API methods require OAuth, which may cause problems in
        situations where an application expects to be able to hit a URL multiple times
        (for example, a media player seeking around a video file). This method
        creates a time-limited URL that can be accessed without any authentication,
        and returns that to you, along with an expiration time.

        Args:
            path: The file to return a URL for. Folders are not supported.

        Returns:
            A dictionary that looks like the following example:

            ``{'url': 'https://dl.dropbox.com/0/view/wvxv1fw6on24qw7/file.mov', 'expires': 'Thu, 16 Sep 2011 01:01:25 +0000'}``

            For a detailed description of what this call returns, visit:
            https://www.dropbox.com/developers/docs#media

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of

            - 400: Bad request (may be due to many things; check e.error for details)
            - 404: Unable to find the file at the given path.
        """
        path = "/media/%s%s" % (self.session.root, format_path(path))

        url, params, headers = self.request(path, method='GET')

        return RESTClient.GET(url, headers)

    def share(self, path):
        """Create a shareable link to a file or folder.

        Shareable links created on Dropbox are time-limited, but don't require any
        authentication, so they can be given out freely. The time limit should allow
        at least a day of shareability, though users have the ability to disable
        a link from their account if they like.

        Args:
            path: The file or folder to share.

        Returns:
            A dictionary that looks like the following example:

            ``{'url': 'http://www.dropbox.com/s/m/a2mbDa2', 'expires': 'Thu, 16 Sep 2011 01:01:25 +0000'}``

            For a detailed description of what this call returns, visit:
            https://www.dropbox.com/developers/docs#share

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of

            - 400: Bad request (may be due to many things; check e.error for details)
            - 404: Unable to find the file at the given path.
        """
        path = "/shares/%s%s" % (self.session.root, format_path(path))

        url, params, headers = self.request(path, method='GET')

        return RESTClient.GET(url, headers)


###########################################################################################




"""
A simple JSON REST request abstraction layer that is used by the
dropbox.client and dropbox.session modules. You shouldn't need to use this.
"""



SDK_VERSION = "1.3"

class RESTClient(object):
    """
    An class with all static methods to perform JSON REST requests that is used internally
    by the Dropbox Client API. It provides just enough gear to make requests
    and get responses as JSON data (when applicable). All requests happen over SSL.
    """

    @staticmethod
    def request(method, url, post_params=None, body=None, headers=None, raw_response=False, proxy_host=None, proxy_port=None):
        """Perform a REST request and parse the response.

        Args:
            method: An HTTP method (e.g. 'GET' or 'POST').
            url: The URL to make a request to.
            post_params: A dictionary of parameters to put in the body of the request.
                This option may not be used if the body parameter is given.
            body: The body of the request. Typically, this value will be a string.
                It may also be a file-like object in Python 2.6 and above. The body
                parameter may not be used with the post_params parameter.
            headers: A dictionary of headers to send with the request.
            raw_response: Whether to return the raw httplib.HTTPReponse object. [default False]
                It's best enabled for requests that return large amounts of data that you
                would want to .read() incrementally rather than loading into memory. Also
                use this for calls where you need to read metadata like status or headers,
                or if the body is not JSON.

        Returns:
            The JSON-decoded data from the server, unless raw_response is
            specified, in which case an httplib.HTTPReponse object is returned instead.

        Raises:
            dropbox.rest.ErrorResponse: The returned HTTP status is not 200, or the body was
                not parsed from JSON successfully.
            dropbox.rest.RESTSocketError: A socket.error was raised while contacting Dropbox.
        """
        post_params = post_params or {}
        headers = headers or {}
        headers['User-Agent'] = 'OfficialDropboxPythonSDK/' + SDK_VERSION

        if post_params:
            if body:
                raise ValueError("body parameter cannot be used with post_params parameter")
            body = urllib.urlencode(post_params)
            headers["Content-type"] = "application/x-www-form-urlencoded"

        host = urlparse.urlparse(url).hostname
        conn = ProperHTTPSConnection(host, 443, proxy_host=proxy_host, proxy_port=proxy_port)

        try:

            # This code is here because httplib in pre-2.6 Pythons
            # doesn't handle file-like objects as HTTP bodies and
            # thus requires manual buffering
            if not hasattr(body, 'read'):
                conn.request(method, url, body, headers)
            else:

                #We need to get the size of what we're about to send for the Content-Length
                #Must support len() or have a len or fileno(), otherwise we go back to what we were doing!
                clen = None

                try:
                    clen = len(body)
                except (TypeError, AttributeError):
                    try:
                        clen = body.len
                    except AttributeError:
                        try:
                            clen = os.fstat(body.fileno()).st_size
                        except AttributeError:
                            # fine, lets do this the hard way
                            # load the whole file at once using readlines if we can, otherwise
                            # just turn it into a string
                            if hasattr(body, 'readlines'):
                                body = body.readlines()
                            conn.request(method, url, str(body), headers)

                if clen != None:  #clen == 0 is perfectly valid. Must explicitly check for None
                    clen = str(clen)
                    headers["Content-Length"] = clen
                    conn.request(method, url, "", headers)
                    BLOCKSIZE = 4096 #4MB buffering just because

                    data=body.read(BLOCKSIZE)
                    while data:
                        conn.send(data)
                        data=body.read(BLOCKSIZE)

        except socket.error, e:
            raise RESTSocketError(host, e)
        except CertificateError, e:
            raise RESTSocketError(host, "SSL certificate error: " + e)

        r = conn.getresponse()
        if r.status != 200:
            raise ErrorResponse(r)

        if raw_response:
            return r
        else:
            try:
                resp = json.loads(r.read())
            except ValueError:
                raise ErrorResponse(r)
            finally:
                conn.close()

        return resp

    @classmethod
    def GET(cls, url, headers=None, raw_response=False):
        """Perform a GET request using RESTClient.request"""
        assert type(raw_response) == bool
        return cls.request("GET", url, headers=headers, raw_response=raw_response)

    @classmethod
    def POST(cls, url, params=None, headers=None, raw_response=False):
        """Perform a POST request using RESTClient.request"""
        assert type(raw_response) == bool
        if params is None:
            params = {}

        return cls.request("POST", url, post_params=params, headers=headers, raw_response=raw_response)

    @classmethod
    def PUT(cls, url, body, headers=None, raw_response=False):
        """Perform a PUT request using RESTClient.request"""
        assert type(raw_response) == bool
        return cls.request("PUT", url, body=body, headers=headers, raw_response=raw_response)

class RESTSocketError(socket.error):
    """
    A light wrapper for socket.errors raised by dropbox.rest.RESTClient.request
    that adds more information to the socket.error.
    """

    def __init__(self, host, e):
        msg = "Error connecting to \"%s\": %s" % (host, str(e))
        socket.error.__init__(self, msg)

class ErrorResponse(Exception):
    """
    Raised by dropbox.rest.RESTClient.request for requests that:
    - Return a non-200 HTTP response, or
    - Have a non-JSON response body, or
    - Have a malformed/missing header in the response.

    Most errors that Dropbox returns will have a error field that is unpacked and
    placed on the ErrorResponse exception. In some situations, a user_error field
    will also come back. Messages under user_error are worth showing to an end-user
    of your app, while other errors are likely only useful for you as the developer.
    """

    def __init__(self, http_resp):
        self.status = http_resp.status
        self.reason = http_resp.reason
        self.body = http_resp.read()
        self.headers = http_resp.getheaders()

        try:
            body = json.loads(self.body)
            self.error_msg = body.get('error')
            self.user_error_msg = body.get('user_error')
        except ValueError:
            self.error_msg = None
            self.user_error_msg = None

    def __str__(self):
        if self.user_error_msg and self.user_error_msg != self.error_msg:
            # one is translated and the other is English
            msg = "%s (%s)" % (self.user_error_msg, self.error_msg)
        elif self.error_msg:
            msg = self.error_msg
        elif not self.body:
            msg = self.reason
        else:
            msg = "Error parsing response body or headers: " +\
                  "Body - %s Headers - %s" % (self.body, self.headers)

        return "[%d] %s" % (self.status, repr(msg))

TRUSTED_CERT_FILE = pkg_resources.resource_filename(__name__, 'trusted-certs.crt')

class ProperHTTPSConnection(httplib.HTTPConnection):
    """
    httplib.HTTPSConnection is broken because it doesn't do server certificate
    validation.  This class does certificate validation by ensuring:
       1. The certificate sent down by the server has a signature chain to one of
          the certs in our 'trusted-certs.crt' (this is mostly handled by the 'ssl'
          module).
       2. The hostname in the certificate matches the hostname we're connecting to.
    """

    def __init__(self, host, port, proxy_host=None, proxy_port=None):
        con = httplib.HTTPConnection.__init__(self, host, port)
        if proxy_host and proxy_port:
            con.set_tunnel(proxy_host, proxy_port)

        self.ca_certs = TRUSTED_CERT_FILE
        self.cert_reqs = ssl.CERT_REQUIRED

    def connect(self):
        sock = create_connection((self.host, self.port))
        self.sock = ssl.wrap_socket(sock, cert_reqs=self.cert_reqs, ca_certs=self.ca_certs)
        cert = self.sock.getpeercert()
        hostname = self.host.split(':', 0)[0]
        match_hostname(cert, hostname)

class CertificateError(ValueError):
    pass

def _dnsname_to_pat(dn):
    pats = []
    for frag in dn.split(r'.'):
        if frag == '*':
            # When '*' is a fragment by itself, it matches a non-empty dotless
            # fragment.
            pats.append('[^.]+')
        else:
            # Otherwise, '*' matches any dotless fragment.
            frag = re.escape(frag)
            pats.append(frag.replace(r'\*', '[^.]*'))
    return re.compile(r'\A' + r'\.'.join(pats) + r'\Z', re.IGNORECASE)

def match_hostname(cert, hostname):
    """Verify that *cert* (in decoded format as returned by
    SSLSocket.getpeercert()) matches the *hostname*.  RFC 2818 rules
    are mostly followed, but IP addresses are not accepted for *hostname*.

    CertificateError is raised on failure. On success, the function
    returns nothing.
    """
    if not cert:
        raise ValueError("empty or no certificate")
    dnsnames = []
    san = cert.get('subjectAltName', ())
    for key, value in san:
        if key == 'DNS':
            if _dnsname_to_pat(value).match(hostname):
                return
            dnsnames.append(value)
    if not san:
        # The subject is only checked when subjectAltName is empty
        for sub in cert.get('subject', ()):
            for key, value in sub:
                # XXX according to RFC 2818, the most specific Common Name
                # must be used.
                if key == 'commonName':
                    if _dnsname_to_pat(value).match(hostname):
                        return
                    dnsnames.append(value)
    if len(dnsnames) > 1:
        raise CertificateError("hostname %r doesn't match either of %s" % (hostname, ', '.join(map(repr, dnsnames))))
    elif len(dnsnames) == 1:
        raise CertificateError("hostname %r doesn't match %r" % (hostname, dnsnames[0]))
    else:
        raise CertificateError("no appropriate commonName or subjectAltName fields were found")

def create_connection(address):
    host, port = address
    err = None
    for res in socket.getaddrinfo(host, port, 0, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        sock = None
        try:
            sock = socket.socket(af, socktype, proto)
            sock.connect(sa)
            return sock

        except socket.error, _:
            err = _
            if sock is not None:
                sock.close()

    if err is not None:
        raise err
    else:
        raise socket.error("getaddrinfo returns an empty list")




###########################################################################################


"""
dropbox.session.DropboxSession is responsible for holding OAuth authentication info
(app key/secret, request key/secret,  access key/secret) as well as configuration information for your app
('app_folder' or 'dropbox' access type, optional locale preference). It knows how to
use all of this information to craft properly constructed requests to Dropbox.

A DropboxSession object must be passed to a dropbox.client.DropboxClient object upon
initialization.
"""

class DropboxSession(object):
    API_VERSION = 1

    API_HOST = "api.dropbox.com"
    WEB_HOST = "www.dropbox.com"
    API_CONTENT_HOST = "api-content.dropbox.com"

    def __init__(self, consumer_key, consumer_secret, access_type, locale=None):
        """Initialize a DropboxSession object.

        Your consumer key and secret are available
        at https://www.dropbox.com/developers/apps

        Args:
            access_type: Either 'dropbox' or 'app_folder'. All path-based operations
                will occur relative to either the user's Dropbox root directory
                or your application's app folder.
            locale: A locale string ('en', 'pt_PT', etc.) [optional]
                The locale setting will be used to translate any user-facing error
                messages that the server generates. At this time Dropbox supports
                'en', 'es', 'fr', 'de', and 'ja', though we will be supporting more
                languages in the future. If you send a language the server doesn't
                support, messages will remain in English. Look for these translated
                messages in rest.ErrorResponse exceptions as e.user_error_msg.
        """
        assert access_type in ['dropbox', 'app_folder'], "expected access_type of 'dropbox' or 'app_folder'"
        self.consumer = oauth.OAuthConsumer(consumer_key, consumer_secret)
        self.token = None
        self.request_token = None
        self.signature_method = oauth.OAuthSignatureMethod_PLAINTEXT()
        self.root = 'sandbox' if access_type == 'app_folder' else 'dropbox'
        self.locale = locale

    def is_linked(self):
        """Return whether the DropboxSession has an access token attached."""
        return bool(self.token)

    def unlink(self):
        """Remove any attached access token from the DropboxSession."""
        self.token = None

    def set_token(self, access_token, access_token_secret):
        """Attach an access token to the DropboxSession.

        Note that the access 'token' is made up of both a token string
        and a secret string.
        """
        self.token = oauth.OAuthToken(access_token, access_token_secret)

    def set_request_token(self, request_token, request_token_secret):
        """Attach an request token to the DropboxSession.

        Note that the reuest 'token' is made up of both a token string
        and a secret string.
        """
        self.token = oauth.OAuthToken(request_token, request_token_secret)

    def build_path(self, target, params=None):
        """Build the path component for an API URL.

        This method urlencodes the parameters, adds them
        to the end of the target url, and puts a marker for the API
        version in front.

        Args:
            target: A target url (e.g. '/files') to build upon.
            params: A dictionary of parameters (name to value). [optional]

        Returns:
            The path and parameters components of an API URL.
        """
        if type(target) == unicode:
            target = target.encode("utf8")

        target_path = urllib.quote(target)
        params = params or {}
        params = params.copy()

        if self.locale:
            params['locale'] = self.locale

        if params:
            return "/%d%s?%s" % (self.API_VERSION, target_path, urllib.urlencode(params))
        else:
            return "/%d%s" % (self.API_VERSION, target_path)

    def build_url(self, host, target, params=None):
        """Build an API URL.

        This method adds scheme and hostname to the path
        returned from build_path.

        Args:
            target: A target url (e.g. '/files') to build upon.
            params: A dictionary of parameters (name to value). [optional]

        Returns:
            The full API URL.
        """
        return "https://%s%s" % (host, self.build_path(target, params))

    def build_authorize_url(self, request_token, oauth_callback=None):
        """Build a request token authorization URL.

        After obtaining a request token, you'll need to send the user to
        the URL returned from this function so that they can confirm that
        they want to connect their account to your app.

        Args:
            request_token: A request token from obtain_request_token.
            oauth_callback: A url to redirect back to with the authorized
                request token.

        Returns:
            An authorization for the given request token.
        """
        params = {'oauth_token': request_token.key,
                  }

        if oauth_callback:
            params['oauth_callback'] = oauth_callback

        return self.build_url(self.WEB_HOST, '/oauth/authorize', params)

    def obtain_request_token(self):
        """Obtain a request token from the Dropbox API.

        This is your first step in the OAuth process.  You call this to get a
        request_token from the Dropbox server that you can then use with
        DropboxSession.build_authorize_url() to get the user to authorize it.
        After it's authorized you use this token with
        DropboxSession.obtain_access_token() to get an access token.

        NOTE:  You should only need to do this once for each user, and then you
        can store the access token for that user for later operations.

        Returns:
            An oauth.OAuthToken representing the request token Dropbox assigned
            to this app. Also attaches the request token as self.request_token.
        """
        self.token = None # clear any token currently on the request
        url = self.build_url(self.API_HOST, '/oauth/request_token')
        headers, params = self.build_access_headers('POST', url)

        response = RESTClient.POST(url, headers=headers, params=params, raw_response=True)
        self.request_token = oauth.OAuthToken.from_string(response.read())
        return self.request_token

    def obtain_access_token(self, request_token=None):
        """Obtain an access token for a user.

        After you get a request token, and then send the user to the authorize
        URL, you can use the authorized request token with this method to get the
        access token to use for future operations. The access token is stored on
        the session object.

        Args:
            request_token: A request token from obtain_request_token. [optional]
                The request_token should have been authorized via the
                authorization url from build_authorize_url. If you don't pass
                a request_token, the fallback is self.request_token, which
                will exist if you previously called obtain_request_token on this
                DropboxSession instance.

        Returns:
            An oauth.OAuthToken representing the access token Dropbox assigned
            to this app and user. Also attaches the access token as self.token.
        """
        request_token = request_token or self.request_token
        assert request_token, "No request_token available on the session. Please pass one."
        url = self.build_url(self.API_HOST, '/oauth/access_token')
        headers, params = self.build_access_headers('POST', url, request_token=request_token)

        response = RESTClient.POST(url, headers=headers, params=params, raw_response=True)
        self.token = oauth.OAuthToken.from_string(response.read())
        return self.token

    def build_access_headers(self, method, resource_url, params=None, request_token=None):
        """Build OAuth access headers for a future request.

        Args:
            method: The HTTP method being used (e.g. 'GET' or 'POST').
            resource_url: The full url the request will be made to.
            params: A dictionary of parameters to add to what's already on the url.
                Typically, this would consist of POST parameters.

        Returns:
            A tuple of (header_dict, params) where header_dict is a dictionary
            of header names and values appropriate for passing into dropbox.rest.RESTClient
            and params is a dictionary like the one that was passed in, but augmented with
            oauth-related parameters as appropriate.
        """
        if params is None:
            params = {}
        else:
            params = params.copy()

        oauth_params = {
            'oauth_consumer_key': self.consumer.key,
            'oauth_timestamp': oauth.generate_timestamp(),
            'oauth_nonce': oauth.generate_nonce(),
            'oauth_version': oauth.OAuthRequest.version,
        }

        token = request_token if request_token else self.token

        if token:
            oauth_params['oauth_token'] = token.key

        params.update(oauth_params)

        oauth_request = oauth.OAuthRequest.from_request(method, resource_url, parameters=params)
        oauth_request.sign_request(self.signature_method, self.consumer, token)

        return oauth_request.to_header(), params
