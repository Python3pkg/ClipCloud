import webbrowser
from pyjson import PyJson
import os
from settings import *
import json
import requests


class Gist:
    api_root = 'https://api.github.com/gists'

    oauth_root = 'https://github.com/login/oauth/%s'
    oauth_url = oauth_root % 'authorize?client_id=%s'
    oauth_token_url = oauth_root % 'access_token'

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

            data = json.dumps({
                client_id: self.client_id,
                client_secret: self.client_secret,
                code: code
            })

            r = requests.get(self.oauth_token_url, data=data).text

            self.access_token = r[r.find('=') + 1: r.find('&')]

            doc = PyJson(GITHUB_TOKEN_PATH)
            doc.add('token', self.access_token)
            doc.save()

    def upload(self, filename, text):
        data = json.dumps({
            "public": False,
            "files": {
                filename: {
                    "content": text
                }
            }
        })

        url = self.api_root
        r = requests.post(url, data=data)
        print r.text
