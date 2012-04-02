import urllib2
import webbrowser
from pyjson import PyJson
import os
from settings import *
import json
import urllib


class Gist:
    api_root = 'https://api.github.com/gists?access_token=%s'

    oauth_root = 'https://github.com/login/oauth/%s'
    oauth_url = oauth_root % 'authorize?client_id=%s'
    oauth_token_url = oauth_root % 'access_token?client_id=%s&client_secret=%s&code=%s'

    def __init__(self):
        api_details = PyJson('dropbox/api.json').doc['github']

        self.client_id = api_details['id']
        self.client_secret = api_details['secret']

        if os.path.exists(GITHUB_TOKEN_PATH):
            self.access_token = PyJson(GITHUB_TOKEN_PATH).doc['token']
        else:
            print 'Please authorise the app and then paste in the code you see on-screen'
            webbrowser.open(self.oauth_url % self.client_id, new=2)
            code = raw_input()

            request = urllib2.Request(self.oauth_token_url % (self.client_id, self.client_secret, code))
            response = urllib2.urlopen(request).read()

            self.access_token = str(response)[response.find('=') + 1: response.find('&')]

            doc = PyJson(GITHUB_TOKEN_PATH)
            doc.add('token', self.access_token)
            doc.save()

    def upload(self):
        # convert json_dict to JSON
        json_data = urllib.urlencode({
            "public": "true",
            "files": {
                "file1.txt": {
                    "content": "String file contents"
                }
            }
        })

        # convert str to bytes (ensure encoding is OK)
        #post_data = json_data.encode('utf-8')

        # we should also say the JSON content type header
        #headers = {}
        #headers['Content-Type'] = 'application/json'

        # now do the request for a url
        #req = urllib.request.Request(url)

        # send the request
        #res = urllib.request.urlopen(req)
        url = self.api_root % self.access_token
        print url
        request = urllib2.Request(url, json_data)
        response = urllib2.urlopen(request).read()
        print response
