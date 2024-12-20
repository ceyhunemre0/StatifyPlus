from flask import Flask, request, redirect
import requests
import base64
import urllib.parse


endpoint = "https://api.spotify.com/v1/me"

app = Flask(__name__)

# Spotify API bilgileri
CLIENT_ID = '3b24f28c383e4c4284db0f96a5e2d4bc'
CLIENT_SECRET = '6da311f8a43843ebadea23cb925f50d4'
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