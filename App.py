import csv
import random
from flask import Flask, jsonify, request, redirect, session, render_template, url_for, abort
import requests
import base64
from dotenv import load_dotenv
import os
import urllib.parse
from datetime import timedelta
import logging

# .env dosyasını yükle
load_dotenv()

# Spotify API bilgileri
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
SECRET_KEY = os.getenv('SECRET_KEY')
REDIRECT_URI = 'http://localhost:8888/callback'
SCOPES = 'user-top-read user-read-private user-read-email user-read-playback-state user-modify-playback-state user-read-currently-playing user-read-playback-state user-read-currently-playing'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
endpoint = "https://api.spotify.com/v1/me"

# Flask uygulamasını oluştur
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)

def clear_session():
    session.pop('access_token', None)
    session.pop('refresh_token', None)
    session.pop('user', None)

@app.before_request
def before_request_func():
    if 'access_token' not in session and request.endpoint not in ('login', 'callback', 'welcome'):
        return redirect(url_for('welcome'))
    elif 'access_token' in session and request.endpoint == 'welcome':
        return redirect(url_for('home'))


@app.template_filter('format_duration')
def format_duration(ms):
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    return f"{minutes}:{seconds:02d}"

@app.route('/')
def home():
    user = session.get('user')
    access_token = session.get('access_token')

    if access_token:
        headers = {'Authorization': f'Bearer {access_token}'}

        # Top Tracks
        tracks_response = requests.get("https://api.spotify.com/v1/me/top/tracks?limit=3", headers=headers)
        if tracks_response.status_code == 200:
            tracks_data = tracks_response.json()
            top_tracks = [{
                'name': track['name'],
                'image': track['album']['images'][0]['url'],
                'url': track['external_urls']['spotify']
            } for track in tracks_data['items']]
        else:
            top_tracks = []

        # Top Artists
        artists_response = requests.get("https://api.spotify.com/v1/me/top/artists?limit=3", headers=headers)
        if artists_response.status_code == 200:
            artists_data = artists_response.json()
            top_artists = [{
                'name': artist['name'],
                'image': artist['images'][0]['url'] if artist['images'] else '',
                'url': artist['external_urls']['spotify']
            } for artist in artists_data['items']]
        else:
            top_artists = []
    else:
        top_tracks = []
        top_artists = []

    return render_template('main.html', user=user, top_tracks=top_tracks, top_artists=top_artists, access_token=access_token)

@app.route('/welcome')
def welcome():
    return render_template('welcome.html') 


@app.route('/login')
def login():
    query_params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'scope': SCOPES,
        'redirect_uri': REDIRECT_URI
    }
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(query_params)}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code:
        return render_template('callback.html', success=False)

    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    token_data = response.json()

    if response.status_code == 200:
        session.permanent = True
        session['access_token'] = token_data['access_token']
        session['refresh_token'] = token_data.get('refresh_token')

        user_headers = {'Authorization': f"Bearer {session['access_token']}"}
        user_response = requests.get(endpoint, headers=user_headers)
        if user_response.status_code == 200:
            user_data = user_response.json()
            session['user'] = {
                'display_name': user_data['display_name'],
                'profile_image': user_data['images'][0]['url'] if user_data['images'] else None
            }
        return render_template('callback.html', success=True, user=session['user'])
    else:
        return render_template('callback.html', success=False)

@app.route('/top-tracks')
def top_tracks():
    access_token = session.get('access_token')
    user = session.get('user')
    if not access_token:
        return redirect(url_for('welcome'))

    time_range = request.args.get('timeRange', 'short_term')
    limit = 20  # Limit her zaman 20

    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(
        f"https://api.spotify.com/v1/me/top/tracks?time_range={time_range}&limit={limit}",
        headers=headers
    )

    if response.status_code == 401:  # Unauthorized
        clear_session()
        return redirect(url_for(''))

    if response.status_code == 200:
        data = response.json()
        tracks = data['items']
        return render_template('top_tracks.html', tracks=tracks, user=user, time_range=time_range)
    else:
        return f"Failed to fetch top tracks: {response.text}", response.status_code

@app.route('/top-artists')
def top_artists():
    access_token = session.get('access_token')
    user = session.get('user')
    current_language = session.get('current_language', 'en')

    if not access_token:
        return redirect(url_for('welcome'))

    time_range = request.args.get('timeRange', 'short_term')
    limit = 20  # Limit her zaman 20

    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(
        f"https://api.spotify.com/v1/me/top/artists?time_range={time_range}&limit={limit}",
        headers=headers
    )

    if response.status_code == 401:  # Unauthorized
        clear_session()
        return redirect(url_for(''))

    if response.status_code == 200:
        data = response.json()
        artists = data['items']
        return render_template('top_artists.html', artists=artists, user=user, time_range=time_range)
    else:
        return f"Failed to fetch top artists: {response.text}", response.status_code
    

@app.route('/api/playlist_tracks')
def get_playlist_tracks():
    tracks = []
    with open('static/playlist_tracks.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            tracks.append({
                'trackName': row['Track Name'],
                'artist': row['Artist'],
                'album': row['Album'],
                'imageUrl': row['Image URL'],
                'spotifyUrl': row['Spotify URL']
            })
    return jsonify(tracks)

"""@app.route('/api/random_track')
def get_random_track():
    tracks = []
    with open('static/playlist_tracks.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        required_columns = {'Track Name', 'Artist', 'Album', 'Image URL', 'Spotify URL', 'Context URI'}
        if not required_columns.issubset(reader.fieldnames):
            logging.error('CSV file is missing required columns')
            return jsonify({'error': 'CSV file format is invalid'}), 400
        for row in reader:
            tracks.append({
                'trackName': row['Track Name'],
                'artist': row['Artist'],
                'album': row['Album'],
                'imageUrl': row['Image URL'],
                'spotifyUrl': row['Spotify URL'],
                'contextUri': row['Context URI']
            })
    random_track = random.choice(tracks)

    access_token = session.get('access_token')
    if not access_token:
        logging.error('Access token not found')
        return jsonify({'error': 'Access token not found'}), 401

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    if not random_track.get('contextUri'):
        logging.error('Context URI is missing for the selected track')
        return jsonify({'error': 'Context URI is missing'}), 400

    # Check active Spotify device
    device_response = requests.get('https://api.spotify.com/v1/me/player/devices', headers=headers)
    if device_response.status_code == 200:
        device_info = device_response.json()['devices'][0]['id']
        if not device_info.get('device'):
            return jsonify({'error': 'No active Spotify device found'}), 400
    else:
        logging.error('Failed to fetch Spotify player details')
        return jsonify({'error': 'Failed to fetch player details', 'details': device_response.json()}), device_response.status_code

    data = {
        "context_uri": random_track['contextUri'],
        "offset": {
            "position": 0
        },
        "position_ms": 0
    }
    response = requests.put(f'https://api.spotify.com/v1/me/player/play{device_info}', headers=headers, json=data)

    if response.status_code != 204:
        try:
            error_details = response.json()
        except ValueError:
            error_details = {'message': 'Unknown error occurred'}
        logging.error(f'Failed to start playback: {error_details}')
        return jsonify({'error': 'Failed to start playback', 'details': error_details}), response.status_code

    logging.info('Playback started successfully')
    return jsonify(random_track)"""


@app.route('/logout')
def logout():
    clear_session()
    return redirect(url_for('welcome'))

@app.errorhandler(404)
def not_found_error(error):
    user = session.get('user')
    return render_template('not_found_404.html', user = user), 404

# Yakalanmayan yolları 404'e yönlendirme
@app.route('/<path:unknown_path>')
def catch_all(unknown_path):
    abort(404)
"""                          -----İLGİLİ  PLAYLİSTİ CSV DOSYASINA YAZDIRIR-----  http://localhost:8888/playlist    endpointe istek at
@app.route('/playlist')
def get_playlist():
    playlist_id = '3E5X6JXhY97W56uCBUe3Sw'  # Çalma listesi ID'sini buraya girin
    access_token = session.get('access_token')
    if not access_token:
        return redirect(url_for('welcome'))

    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f"https://api.spotify.com/v1/playlists/{playlist_id}", headers=headers)

    if response.status_code == 401:  # Unauthorized
        clear_session()
        return redirect(url_for('welcome'))

    if response.status_code == 200:
        playlist_data = response.json()
        write_tracks_to_csv(playlist_data['tracks']['items'], 'static/playlist_tracks.csv')
        return jsonify(playlist_data)
    else:
        return f"Failed to fetch playlist: {response.text}", response.status_code

def write_tracks_to_csv(tracks, filename):

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # CSV başlık satırı
        writer.writerow(['Track Name', 'Artist', 'Album', 'Image URL', 'Spotify URL', 'Context URI'])
        
        for item in tracks:
            track = item['track']
            track_name = track['name']  # Parça adı
            artist_name = track['artists'][0]['name']  # İlk sanatçı adı
            album_name = track['album']['name']  # Albüm adı
            context_uri = track['album']['uri']  # Albüm URI'si
            image_url = track['album']['images'][0]['url']  # Albüm görsel URL'si
            spotify_url = track['external_urls'].get('spotify', 'N/A')  # Spotify URL'si

            # CSV'ye yaz
            writer.writerow([track_name, artist_name, album_name, image_url, spotify_url, context_uri])
"""

if __name__ == '__main__':
    app.run(port=8888)