"""
import tekore as tk
from flask import Flask, redirect, request, session, url_for

CLIENT_ID = 'd380605693ec4359a4b7d2b529135431'
CLIENT_SECRET = 'e851bb1a152042fe8602e1bcbe25a281'
REDIRECT_URI = 'http://127.0.0.1:5000/callback/'

app = Flask(__name__)
app.secret_key = 'OjasPlease'

# ✅ Create credentials and auth object
cred = tk.Credentials(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
spotify_auth = tk.UserAuth(cred, scope='user-top-read')

@app.route('/')
def index():
    return '<a href="/login">Login with Spotify</a>'


# @app.route('/login')
# def login():
#     url, state = spotify_auth.request_url()
#     session['state'] = state  # ✅ Save state in session
#     return redirect(url)

# @app.route('/login')
# def login():
#     return redirect(spotify_auth.url)

import secrets

@app.route('/login')
def login():
    state = secrets.token_urlsafe(16)  # ✅ Generate secure random state
    session['spotify_state'] = state   # ✅ Store in session

    url = spotify_auth.url + f"&state={state}"  # ✅ Inject state manually
    return redirect(url)

# @app.route('/callback/')
# def callback():
#     code = request.args.get('code')
#     if not code:
#         return 'Authorization failed or denied.', 400
#     token = spotify_auth.request_token(code)
#     session['refresh_token'] = token.refresh_token
#     return redirect(url_for('top_tracks'))

# @app.route('/callback/')
# def callback():
#     code = request.args.get('code')
#     state = request.args.get('state')

#     if not code or not state:
#         return 'Authorization failed or denied.', 400

#     expected_state = session.get('state')
#     if state != expected_state:
#         return 'State mismatch. Possible CSRF attack.', 400

#     token = spotify_auth.request_token(code, state)
#     session['refresh_token'] = token.refresh_token
#     return redirect(url_for('top_tracks'))

# @app.route('/callback/')
# def callback():
#     code = request.args.get('code')
#     if not code:
#         return 'Authorization failed or denied.', 400

#     # ✅ No need to pass or check state
#     token = spotify_auth.request_token(code)
#     session['refresh_token'] = token.refresh_token
#     return redirect(url_for('top_tracks'))

@app.route('/callback/')
def callback():
    code = request.args.get('code')
    returned_state = request.args.get('state')
    expected_state = session.get('spotify_state')

    if not code or not returned_state or returned_state != expected_state:
        return 'State mismatch. Possible CSRF attack.', 400

    token = spotify_auth.request_token(code, returned_state)  # ✅ Pass state explicitly
    session['refresh_token'] = token.refresh_token
    return redirect(url_for('top_tracks'))

@app.route('/top_tracks')
def top_tracks():
    refresh_token = session.get('refresh_token')
    if not refresh_token:
        return redirect(url_for('login'))

    # ✅ Refresh token manually
    token = cred.refresh_user_token(refresh_token)
    spotify = tk.Spotify(token)
    user = spotify.current_user()
    tracks = spotify.current_user_top_tracks()
    if not tracks.items:
        return f'Hi {user.display_name}, no top tracks found.'
    top_track = tracks.items[0].name
    return f'Hi {user.display_name}, your top track is "{top_track}".'

if __name__ == '__main__':
    app.run(debug=True)

    """


import tekore as tk
from flask import Flask, redirect, request, session, url_for

CLIENT_ID = 'd380605693ec4359a4b7d2b529135431'
CLIENT_SECRET = 'e851bb1a152042fe8602e1bcbe25a281'
REDIRECT_URI = 'http://127.0.0.1:5000/callback/'

app = Flask(__name__)
app.secret_key = 'OjasPlease'

# ✅ Create credentials and auth object ONCE
cred = tk.Credentials(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
spotify_auth = tk.UserAuth(cred, scope='user-top-read')

@app.route('/')
def index():
    return '<a href="/login">Login with Spotify</a>'

@app.route('/login')
def login():
    # ✅ Generate login URL and store Tekore's internal state
    url = spotify_auth.url
    session['spotify_state'] = spotify_auth.state
    return redirect(url)

@app.route('/callback/')
def callback():
    code = request.args.get('code')
    returned_state = request.args.get('state')
    expected_state = session.get('spotify_state')

    if not code or not returned_state or returned_state != expected_state:
        return 'State mismatch. Possible CSRF attack.', 400

    # ✅ Pass the stored state back to Tekore
    token = spotify_auth.request_token(code, returned_state)
    session['refresh_token'] = token.refresh_token
    return redirect(url_for('top_tracks'))

@app.route('/top_tracks')
def top_tracks():
    refresh_token = session.get('refresh_token')
    if not refresh_token:
        return redirect(url_for('login'))

    token = cred.refresh_user_token(refresh_token)
    spotify = tk.Spotify(token)
    user = spotify.current_user()
    tracks = spotify.current_user_top_tracks()
    if not tracks.items:
        return f'Hi {user.display_name}, no top tracks found.'
    top_track = tracks.items[0].name
    return f'Hi {user.display_name}, your top track is "{top_track}".'

if __name__ == '__main__':
    app.run(debug=True)