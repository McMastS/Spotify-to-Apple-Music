import spotipy
import applemusicpy
import requests
import json
import sys
from spotipy import util

class MyAppleMusic(applemusicpy.AppleMusic):
    def __init__(self, secret_key, key_id, team_id, proxies=None,
                 requests_session=True, max_retries=10, requests_timeout=None, session_length=12, user_access_token=None):
        super().__init__(secret_key, key_id, team_id, proxies,
                 requests_session, max_retries, requests_timeout, session_length)
        self.user_access_token = user_access_token

    def _auth_headers(self):
        """
        Get header for API request

        :return: header in dictionary format
        """
        headers = {}
        if self.token_str:
            headers = {'Authorization': 'Bearer {}'.format(self.token_str)}
        if self.user_access_token:
            headers['Music-User-Token'] = self.user_access_token
        return headers
    
    def _build_track(self, track_id, track_type='songs'):
        return {
            'id': str(track_id),
            'type': 'songs',
        }

    def _build_tracks(self, track_ids, track_type='songs'):
        return list(map(lambda track_id: self._build_track(track_id, track_type),
                   track_ids))

    def _post(self, url, params, payload):
        headers = self._auth_headers()
        headers['Content-Type'] = 'application/json'
        response = requests.post(url, headers=headers, params=params, data=json.dumps(payload), timeout=30)
        response.raise_for_status()
        return response.json()
    
    def create_playlist(self, name, description=None, track_ids=None, include=None):
        # https://developer.apple.com/documentation/applemusicapi/create_a_new_library_playlist
        url = self.root + 'me/library/playlists'
        params = None
        payload = {'attributes': {'name': name}}
        if description:
            payload['attributes']['description'] = description
        
        if track_ids:
            tracks = self._build_tracks(track_ids)
            payload['relationships'] = {'tracks': {'data': tracks}}

        if include:
            params = {'include': include}

        return self._post(url, params, payload)

class PortPlaylist():
    def __init__(self, s_client_id, s_client_secret, a_team_id, a_secret, a_key_id):
        self.s_client_id = s_client_id
        self.s_client_secret = s_client_secret
        self.a_team_id = a_team_id
        self.a_secret = a_secret
        self.a_key_id = a_key_id

        self.refresh_dev_tokens()
    
    def _get_spotify_playlist(self, playlist_url):
        playlist_id_idx = playlist_url.find('playlist/') + 9
        user_idx = playlist_url.find('user/') + 0
        # 'playlist/' wasn't found
        if playlist_id_idx == -1:
            return 'Invalid playlist url.'

        user_id = ''
        if user_idx != -1:
            user_id = playlist_url[user_idx:]
        playlist_id = playlist_url[playlist_id_idx:]
        playlist = self.spotify.user_playlist_tracks(user_id, playlist_id, fields=None, limit=100)

        return playlist

    def _get_track_ids(self, playlist):
        track_ids = []
        not_found = []
        for i in range(playlist['total']):
            name = playlist['items'][i]['track']['name']
            artist = playlist['items'][i]['track']['artists'][0]['name']
            album = playlist['items'][i]['track']['album']['name']

            track = self.am.search(name, types=['songs'], limit=5)
            try:
                # for song 
                id =  track['results']['songs']['data'][0]['id']
                track_ids.append(id)
            except KeyError as e:
                not_found.append(name)
        return (track_ids, not_found)

    def _create_apple_playlist(self, name, description=None, track_ids=None, include=None):
        return self.am.create_playlist(name, description, track_ids, include)

    def port_playlist(self, playlist_url, name, description=None):
        playlist = self._get_spotify_playlist(playlist_url)
        track_ids, not_found = self._get_track_ids(playlist)

        resp = self._create_apple_playlist(name, description=description, track_ids=track_ids)
        return (resp, not_found)

    def set_a_user_token(self, token):
        self.am.user_access_token = token

    def refresh_dev_tokens(self):
        client_credentials_manager = util.oauth2.SpotifyClientCredentials(client_id=self.s_client_id, client_secret=self.s_client_secret)
        token = client_credentials_manager.get_access_token()
        self.spotify = spotipy.Spotify(token)

        self.am = MyAppleMusic(self.a_secret, self.a_key_id, self.a_team_id)
        self.a_dev_token = self.am.token_str
