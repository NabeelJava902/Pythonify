#!/usr/bin/env python
# coding: utf-8

# In[1]:
import json

from pythonify.variables import *
from urllib.parse import urlencode
from pythonify.backend import *


class SpotifyAPI(object):

    sv = SaveLoad()

    def __init__(self):
        self.sv.reload()
        self.spotify_object = SpotifyObject(spotify_client_id, spotify_secret)
        self.spotify_user_object = SpotifyUserObject(spotify_client_id, spotify_secret)

    def get_resource(self, lookup_id, resource_type='albums', version='v1'):
        endpoint = f"https://api.spotify.com/{version}/{resource_type}/{lookup_id}"
        headers = self.spotify_object.get_resource_header()
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()

    def parse_album_result(self, dictionary):
        url = dictionary['external_urls']['spotify']
        _id = dictionary['id']
        album_name = dictionary['name']
        artist_name = dictionary['artists'][0]['name']
        album_data = {
            'url': f"{url}",
            'id': f"{_id}",
            'album_name': f"{album_name}",
            'artist_name': f"{artist_name}"
        }
        return album_data

    def parse_artist_result(self, dictionary):
        follower_count = dictionary['followers']['total']
        url = dictionary['external_urls']['spotify']
        genres = dictionary['genres']
        _id = dictionary['id']
        name = dictionary['name']
        uri = dictionary['uri']
        artist_data = {
            'follower_count': f"{follower_count}",
            'url': f"{url}",
            'genres': f"{genres}",
            '_id': f"{_id}",
            'name': f"{name}",
            'uri': f"{uri}"
        }
        return artist_data

    def base_search(self, query_params):
        headers = self.spotify_object.get_resource_header()
        endpoint = "https://api.spotify.com/v1/search"

        lookup_url = f"{endpoint}?{query_params}"
        r = requests.get(lookup_url, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()

    def advanced_search(self, list, artist):
        target_element = 0
        artist_found = False
        for x in range(0, len(list)):
            artist_name = list[x]['album']['artists'][0]['name']
            if artist == artist_name:
                target_element = x
                artist_found = True
                break
        if not artist_found:
            raise Exception("No tracks with artist name: " + artist)
            pass
        return target_element

    def parse_track_results(self, dictionary, artist):
        if dictionary is None:
            raise Exception('A dict variable must be passed to this method')
        items = dictionary['tracks']['items']
        var = items[0]
        if artist is not None:
            var = items[self.advanced_search(items, artist)]
        song_name = var['name']  # independent
        data = var['album']['artists'][0]
        external_urls = data['external_urls']
        song_data = {
            'url': f"{external_urls['spotify']}",
            'id': f"{data['id']}",
            'name': f"{data['name']}",
            'uri': f"{data['uri']}",
            'song_name': f"{song_name}"
        }
        return song_data

    def approve(self, response):
        if response.status_code == 401:
            self.sv.did_access_token_expire = True
            raise Exception("Access token expired, re-run program")
        elif response.status_code == 400:
            raise Exception("The uri is invalid")
        else:
            print("Successful")

    def get_album(self, _id):
        dictionary = self.get_resource(_id, resource_type='albums')
        return self.parse_album_result(dictionary)

    def get_artist(self, _id):
        dictionary = self.get_resource(_id, resource_type='artists')
        return self.parse_artist_result(dictionary)

    def get_track(self, query=None, artist=None, operator=None, operator_query=None):
        if query == None:
            raise Exception("A query is required")
        if isinstance(query, dict):
            query = " ".join([f"{k}:{v}" for k, v in query.items()])
        if operator is not None and operator_query is not None:
            if operator == "or" or operator == "not":
                operator = operator.upper()
                if isinstance(operator_query, str):
                    query = f"{query} {operator} {operator_query}"
        query_params = urlencode({"q": query, "type": 'track'})
        dictionary = self.base_search(query_params)
        return self.parse_track_results(dictionary, artist)

    def create_playlist(self, name, description):
        self.sv.reload()
        request_body = json.dumps({
            "name": f"{name}",
            "description": f"{description}",
        })
        query = 'https://api.spotify.com/v1/users/{}/playlists'.format(spotify_user_id)
        response = requests.post(
            query,
            data=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.sv.user_access_token)
            }
        )
        self.approve(response)

        response_json = response.json()
        # Return playlist id
        return response_json["id"]

    def add_tracks_to_playlist(self, playlist_id=None, track_id_list=None):
        self.sv.reload()
        if playlist_id is None:
            raise Exception("No playlist_id found")
        elif track_id_list is None:
            raise Exception("No track_id_list found")

        request_body = json.dumps({
            "uris": track_id_list
        })
        query = 'https://api.spotify.com/v1/playlists/{}/tracks'.format(playlist_id)
        response = requests.post(
            query,
            data=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.sv.user_access_token)
            }
        )
        self.approve(response)
        response_json = response.json()

        return response_json['snapshot_id']
