spotify_client_id = "(Put in your auto-generated spotify client id)"
spotify_secret = "(Put in your auto-generated spotify secret)"
spotify_user_id = "(Put in your your spotify username)"

import pickle


class SaveLoad(object):
    user_access_token = None
    user_refresh_token = None
    did_access_token_expire = True

    def save_tokens(self):
        dict = {
            "access": f"{self.user_access_token}",
            "refresh": f"{self.user_refresh_token}",
            "expire": f"{self.did_access_token_expire}"
        }
        file = open('pythonify/dump.txt', 'wb')
        pickle.dump(dict, file)
        file.close()

    def reload(self):
        file = open('pythonify/dump.txt', 'rb')
        dict = None
        try:
            dict = pickle.load(file)
        except EOFError:
            self.did_access_token_expire = True
        if dict is not None:
            self.user_access_token = dict['access']
            self.user_refresh_token = dict['refresh']
            self.did_access_token_expire = dict['expire']

    def set_tokens(self, access, refresh):
        self.user_refresh_token = refresh
        self.user_access_token = access