import json
import math
import requests
import spotipy
import applemusicpy
from spotipy import util

class MyAppleMusic(applemusicpy.AppleMusic):
    def __init__(self, secret_key, key_id, team_id, proxies=None,
                 requests_session=True, max_retries=10, requests_timeout=None,
                 session_length=12, user_access_token=None):
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
            'type': track_type,
        }

    def _build_tracks(self, track_ids, track_type='songs'):
        return list(map(lambda track_id: self._build_track(track_id, track_type),
                        track_ids))

    def _post(self, url, params, payload):
        headers = self._auth_headers()
        headers['Content-Type'] = 'application/json'
        response = requests.post(url, headers=headers, params=params,
                                 data=json.dumps(payload), timeout=30)
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
        # TODO: add some security for malicious links
        playlist_id_idx = playlist_url.find('playlist/')
        user_idx = playlist_url.find('user/')

        # 'playlist/' wasn't found in the url
        if playlist_id_idx == -1:
            return 'Invalid playlist url.'

        playlist_id = playlist_url[playlist_id_idx + 9:]

        if user_idx == -1:
            user_id = ''
        else:
            user_id = playlist_url[user_idx:]

        playlist = self.spotify.user_playlist_tracks(user_id, playlist_id, fields=None, limit=100)

        return playlist

    def _get_track_ids(self, playlist):
        track_ids = []
        isrcs = []

        # Apples songs by isrc endpoint only accepts 25 isrcs at a time
        # so break them up into seperate lists of max 25
        num_tracks = playlist['total']
        offset = 0
        for i in range(math.ceil(num_tracks/25)):
            temp = []
            for j in range(25):
                try:
                    isrc = playlist['items'][j + offset]['track']['external_ids']['isrc']
                    temp.append(isrc)
                except IndexError:
                    break
            isrcs.append(temp)
            offset += 25

        # Keep track of which songs have been added to the track list
        included = set()
        for isrc_list in isrcs:
            tracks = self.am.songs_by_isrc(isrc_list)
            for track in tracks['data']:
                # Don't check for album name because of Greatest Hits albums and similar compilation albums,
                # but keep the artist check to ensure only one of each song is chosen
                track_info = "%s %s" % (track['attributes']['name'], track['attributes']['artistName'])
                if track_info not in included:
                    included.add(track_info)
                    track_ids.append(track['id'])

        return track_ids

    def _create_apple_playlist(self, name, description=None, track_ids=None, include=None):
        return self.am.create_playlist(name, description, track_ids, include)

    def port_playlist(self, playlist_url, name, description=None):
        playlist = self._get_spotify_playlist(playlist_url)
        track_ids = self._get_track_ids(playlist)

        resp = self._create_apple_playlist(name, description=description, track_ids=track_ids)
        return resp

    def set_a_user_token(self, token):
        self.am.user_access_token = token

    def refresh_dev_tokens(self):
        credentials = util.oauth2.SpotifyClientCredentials(client_id=self.s_client_id,
                                                           client_secret=self.s_client_secret)
        token = credentials.get_access_token()
        self.spotify = spotipy.Spotify(token)

        self.am = MyAppleMusic(self.a_secret, self.a_key_id, self.a_team_id)
        self.a_dev_token = self.am.token_str
