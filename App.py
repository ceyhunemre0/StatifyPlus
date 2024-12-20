from flask import Flask, request, redirect, session, jsonify, render_template
import requests
import base64
from dotenv import load_dotenv
import os
import urllib.parse

# .env dosyasını yükle
load_dotenv()

# Spotify API bilgileri
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
SECRET_KEY = os.getenv('SECRET_KEY')  # .env dosyasından SECRET_KEY alınıyor
REDIRECT_URI = 'http://localhost:8888/callback'
SCOPES = 'user-top-read user-read-private user-read-email'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
endpoint = "https://api.spotify.com/v1/me"

# Flask uygulamasını oluştur
app = Flask(__name__)
app.secret_key = SECRET_KEY  # Flask uygulamasına secret_key atanıyor


@app.template_filter('format_duration')
def format_duration(ms):
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    return f"{minutes}:{seconds:02d}"


@app.route('/')
def home():
    # home.html dosyasını aç ve içeriğini oku
    try:
        with open('templates/home.html', 'r') as file:
            html_content = file.read()
        return html_content
    except FileNotFoundError:
        return "Home page not found", 404

@app.route('/login')
def login():
    # Kullanıcıyı Spotify yetkilendirme ekranına yönlendir
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
    # Yetkilendirme kodunu al
    code = request.args.get('code')
    if not code:
        return render_template('callback.html', success=False)

    # Token almak için POST isteği gönder
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

    # Token'ı session'a kaydet
    if response.status_code == 200:
        session['access_token'] = token_data['access_token']
        session['refresh_token'] = token_data.get('refresh_token')
        return render_template('callback.html', success=True)
    else:
        return render_template('callback.html', success=False)


@app.route('/top-tracks')
def top_tracks():
    # Token'ı session'dan al
    access_token = session.get('access_token')
    if not access_token:
        return "Token not found. Please log in first.", 400

    time_range = request.args.get('timeRange', 'short_term')  # default short_term
    limit = int(request.args.get('limit', 10))  # default limit 10
    offset = int(request.args.get('offset', 0))  # default offset 0

    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    # Spotify API'ye top tracks isteği gönder
    response = requests.get(
        f"https://api.spotify.com/v1/me/top/tracks?time_range={time_range}&limit={limit}&offset={offset}",
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        tracks = data['items']  # Spotify'dan gelen şarkılar
        # Şablona verileri gönder
        print(tracks) 
        return render_template('top_tracks.html', tracks=tracks, time_range=time_range, limit=limit, offset=offset)
    else:
        return f"Failed to fetch top tracks: {response.text}", response.status_code




if __name__ == '__main__':
    app.run(port=8888)
