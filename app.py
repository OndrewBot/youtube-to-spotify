import time
from googletrans import Translator
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect

from access_token import get_token, client_id, client_secret, app_secret
from spotify_playlist_generator_v2 import *

app = Flask(__name__)

app.config['SESSION_COOKIE_NAME'] = 'Trackify Cookie'
app.secret_key = app_secret
TOKEN_INFO = 'token_info'

@app.route('/')
def login():
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    session.clear()
    code = request.args.get('code')
    token_info = create_spotify_oauth().get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('create_playlist', _external = True))

@app.route('/createPlaylist')
def create_playlist():

    try:
        token_info = get_token()
    except:
        print("User not logged in.")
        return redirect('/')
    
    sp = spotipy.Spotify(auth=token_info['access_token'])
    user_id = sp.current_user()['id']

    url = input('Enter the YouTube URL: ')
    playlist = CreatePlaylist(url)
    playlist.get_songs_youtube()
    playlist_name = playlist.get_title()
    tracklist = playlist.get_tracklist()

    # create new playlist
    new_playlist = sp.user_playlist_create(user_id, playlist_name, True)
    new_playlist_id = new_playlist['id']
    tracklist_uris = []
    not_found_tracklist = []

    # search for song and add uri to list
    for track in tracklist:
        # search top 5 for each track
        # collect data from each: uri and artist
        # reverse search to confirm match
        # if not found then add to not-found-list and skip
        track = track.lower()
        track_result = sp.search(q=track, limit=5, type="track")
        if track_result['tracks']['total'] > 0:
            success_flag = 1        # 0 is success, 1 is failure
            for song in track_result['tracks']['items']:
                # check if artist name matches
                artist_name = song['artists'][0]['name']
                # if characters are not English/alphanumeric
                try:
                    artist_name.encode(encoding='utf-8').decode('ascii')
                except:
                    translator = Translator(service_urls=['translate.googleapis.com'])
                    artist_name = translator.translate(artist_name, dest='en').text  # English
                artist_name = artist_name.lower().split()       
                name_flag = 0       # 0 is success, 1 is failure
                song_name_parsed = track.split()
                artist_matches = len(artist_name)

                # checks if Spotify's artist is in Youtube Tracklist
                for name in artist_name:
                    if name not in track:
                        name_flag = 1
                    else:
                        song_name_parsed.remove(name)

                # Spotify may overdefine artist. Checks if 50% match
                if name_flag == 1:
                    for name in artist_name:
                        if name not in track:
                            artist_matches -= 1

                    if artist_matches / len(artist_name) >= .5:
                        name_flag = 0

                if name_flag == 0:
                    # check if song name matches >=80%
                    track_name = song['name']
                    try:
                        track_name.encode(encoding='utf-8').decode('ascii')
                    except:
                        translator = Translator(service_urls=['translate.googleapis.com'])
                        track_name = translator.translate(track_name, dest='en').text

                    # check if Spotify's track name is in the Youtube tracklist    
                    track_name = track_name.lower().split()
                    track_matches = len(track_name)
                    for name in track_name:
                        if name not in track:
                            track_matches -= 1

                    if track_matches / len(track_name) >= .8:
                        success_flag = 0   
                        tracklist_uris.append(song['uri'])
                        break       # break out to next track in tracklist

                    else:
                        # check if the Youtube parsed song name is in the Spotify track name
                        track_name = ' '.join(track_name)
                        track_matches = len(song_name_parsed)
                        for name in song_name_parsed:
                            if name not in track_name:
                                track_matches -= 1

                        if track_matches / len(song_name_parsed) >= .8:
                            success_flag = 0   
                            tracklist_uris.append(song['uri'])
                            break       # break out to next track in tracklist

            # Top 5 results have been seached and there was no tracklist match, go to next track
            if success_flag == 1:
                not_found_tracklist.append(track)
                continue     
        # No results were found and no tracklist match, go to next track
        else:
            not_found_tracklist.append(track)
            continue
    
    if len(not_found_tracklist) == len(tracklist):
        return('Failure. No tracks found.')
    elif len(not_found_tracklist) > 0:
        sp.user_playlist_add_tracks(user_id, new_playlist_id, tracklist_uris)
        return(f'Partial success - some tracks added to new playlist. Tracks not found: {not_found_tracklist}')
    else:
        sp.user_playlist_add_tracks(user_id, new_playlist_id, tracklist_uris)
        return('Success - all tracks added to new playlist.')


def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        redirect(url_for('login', _external= False))

    now = int(time.time())

    is_expired = token_info['expires_at'] - now < 60
    if(is_expired):
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id= client_id,
        client_secret= client_secret,
        redirect_uri= url_for('redirect_page', _external= True),
        scope='user-library-read playlist-modify-public'
    )

app.run(debug=True)