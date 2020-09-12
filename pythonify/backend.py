import base64

import requests
import datetime
import time

from pythonify.variables import SaveLoad


class SpotifyObject(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = client_id
        self.client_secret = client_secret

    def get_client_credentials(self):
        """
        Returns a base64 encoded string
        """
        client_id = self.client_id
        client_secret = self.client_secret
        if client_secret is None or client_id is None:
            raise Exception("You must set client_id and client_secret")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def get_token_headers(self):
        client_creds_b64 = self.get_client_credentials()
        return {
            "Authorization": f"Basic {client_creds_b64}"
        }

    def get_token_data(self):
        return {
            "grant_type": "client_credentials"
        }

    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()
        r = requests.post(token_url, data=token_data, headers=token_headers)
        if r.status_code not in range(200, 299):
            raise Exception("Could not authenticate client")
        data = r.json()
        now = datetime.datetime.now()
        access_token = data['access_token']
        expires_in = data['expires_in']  # seconds
        expires = now + datetime.timedelta(seconds=expires_in)
        self.access_token = access_token
        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True

    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires < now:
            self.perform_auth()
            return self.get_access_token()
        elif token is None:
            self.perform_auth()
            return self.get_access_token()
        return token

    def get_resource_header(self):
        access_token = self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        return headers


class SpotifyUserObject(object):
    access_token = None
    refresh_token = None
    authorize_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = False
    client_id = None
    client_secret = None
    sv = SaveLoad()
    authorize_url = "https://accounts.spotify.com/authorize"
    token_url = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id, client_secret, *args, **kwargs):
        self.sv.reload()
        self.client_id = client_id
        self.client_secret = client_secret
        self.req_access()

    def get_client_credentials(self):
        client_id = self.client_id
        client_secret = self.client_secret
        if client_id is None or client_secret is None:
            raise Exception("Must put in credentials")
        client_creds = f"{client_id}:{client_secret}"
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def get_payload(self):
        return {
            "client_id": f"{self.client_id}",
            "response_type": "code",
            "redirect_uri": "https://open.spotify.com/",
            "scope": "playlist-modify-public"
        }

    def get_token_data(self):
        return {
            "grant_type": "authorization_code",
            "code": f"{self.authorize_token}",
            "redirect_uri": "https://open.spotify.com/"
        }

    def get_token_headers(self):
        return {
            "Authorization": f"Basic {self.get_client_credentials()}"
        }

    def get_refresh_token_data(self):
        return {
            "grant_type": "refresh_token",
            "refresh_token": f"{SaveLoad.user_refresh_token}",
        }

    def perform_auth(self, _data, _headers):
        if self.authorize_token is not None:
            token_url = self.token_url
            r = requests.post(url=token_url, data=_data, headers=_headers)
            if r.status_code not in range(200, 299):
                raise Exception("The authorization token may have been incorrect")
            data = r.json()
            self.sv.set_tokens(access=data['access_token'], refresh=data['refresh_token'])
            self.sv.did_access_token_expire = False
            self.sv.save_tokens()

    def req_access(self):
        if self.sv.did_access_token_expire:
            if self.sv.user_refresh_token is None:
                authorize_url = self.authorize_url
                r = requests.get(url=authorize_url, params=self.get_payload())
                if r.status_code == 200:
                    print("authorizing...")
                    time.sleep(2)
                elif r.status_code == 404:
                    print("authorization failure")
                    pass
                print("Go to this url: " + r.url)
                new_url = input("Paste everything from the url of the new webpage ")
                self.authorize_token = new_url[31:len(new_url)]
                self.perform_auth(self.get_token_data(), self.get_token_headers())
            else:
                self.authorization_token = self.refresh_token  # Use refresh token instead
                self.perform_auth(self.get_refresh_token_data(), self.get_token_headers())