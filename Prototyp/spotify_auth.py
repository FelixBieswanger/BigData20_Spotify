import json
import requests


class Spotify_Auth:
    def __init__(self):

        with open("secrets.json", "r") as file:
            secrets = json.load(file)

            CLIENT_ID = secrets["CLIENT_ID"]
            CLIENT_SECRET = secrets["CLIENT_SECRET"]

            grant_type = 'client_credentials'
            body_params = {'grant_type': grant_type}

            url = 'https://accounts.spotify.com/api/token'
            response = requests.post(url, data=body_params,
                                    auth=(CLIENT_ID, CLIENT_SECRET))

            token_raw = json.loads(response.text)
            self.token = token_raw["access_token"]


    def get(self, url, params):
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            "Authorization": "Bearer {}".format(self.token)
        }

        return requests.get(url,headers=headers,params=params)
    

