from flask import Flask, request, redirect
import requests
import base64
from dotenv import load_dotenv
import os
import urllib.parse
load_dotenv()


endpoint = "https://api.spotify.com/v1/me"

app = Flask(__name__)

# Spotify API bilgileri

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = 'http://localhost:8888/callback'
SCOPES = 'user-read-private user-read-email'

# Spotify OAuth URLs
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'

@app.route('/')
def login():
    # Kullanıcıyı yetkilendirme ekranına yönlendir
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
        return "Authorization failed", 400

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

    # Erişim ve yenileme token'larını döndür
    return token_data

if __name__ == '__main__':
    app.run(port=8888)