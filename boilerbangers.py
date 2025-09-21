import tekore as tk
from flask import Flask, redirect, request, session, url_for, render_template
from dotenv import load_dotenv
import os
import sqlite3

load_dotenv()

app = Flask(__name__)

CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
app.secret_key = os.getenv('FLASK_SECRET_KEY')

cred = tk.Credentials(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)
spotify_auth = tk.UserAuth(cred, scope='user-top-read')

# -------------------- ROUTES --------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
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
    user_id = user.id

    # Connect to DB and create tables if needed
    conn = sqlite3.connect('boilerbangers.db')
    cursor = conn.cursor()
    # cursor.execute("DELETE FROM top_tracks") # Use to wipe database clean before

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS top_tracks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song_name TEXT,
            artists TEXT,
            points INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY
        )
    ''')

    # cursor.execute("DELETE FROM users") # Use to wipe database clean 
    # Check if user already processed
    cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
    already_processed = cursor.fetchone()

    if already_processed:
        conn.close()
        return redirect(url_for('dashboard'))

    # Mark user as processed
    cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))

    # Fetch top tracks and insert/update global leaderboard
    tracks = spotify.current_user_top_tracks(time_range='short_term', limit=50)
    points = 50

    for track in tracks.items:
        song_name = track.name
        artists = ', '.join(artist.name for artist in track.artists)

        # Check if track already exists
        cursor.execute(
            "SELECT points FROM top_tracks WHERE song_name = ? AND artists = ?",
            (song_name, artists)
        )
        existing = cursor.fetchone()

        if existing:
            new_points = existing[0] + points
            cursor.execute(
                "UPDATE top_tracks SET points = ? WHERE song_name = ? AND artists = ?",
                (new_points, song_name, artists)
            )
        else:
            cursor.execute(
                "INSERT INTO top_tracks (song_name, artists, points) VALUES (?, ?, ?)",
                (song_name, artists, points)
            )

        points -= 1
        if points < 1:
            break

    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

# @app.route('/api/top10')
# def api_top10():
#     conn = sqlite3.connect('boilerbangers.db')
#     cursor = conn.cursor()
#     cursor.execute('SELECT song_name, artists, points FROM top_tracks ORDER BY points DESC')
#     rows = cursor.fetchall()
#     conn.close()
#     data = [{'song_name': row[0], 'artists': row[1], 'points': row[2]} for row in rows]
#     return {'tracks': data}

@app.route('/api/top10')
def api_top10():
    conn = sqlite3.connect('boilerbangers.db')
    cursor = conn.cursor()
    cursor.execute('SELECT song_name, artists, points FROM top_tracks ORDER BY points DESC LIMIT 10')
    rows = cursor.fetchall()
    conn.close()

    # Use Tekore to fetch album covers
    refresh_token = session.get('refresh_token')
    token = cred.refresh_user_token(refresh_token)
    spotify = tk.Spotify(token)

    data = []
    for row in rows:
        song_name, artists, _ = row
        # search = spotify.search(f"{song_name} {artists}", types=('track',), limit=1)
        # if search.tracks.items:
        #     album_cover = search.tracks.items[0].album.images[0].url
        # else:
        #     album_cover = ''  # fallback

        search_results, = spotify.search(f"{song_name} {artists}", types=('track',), limit=1)
        if search_results.items:
            album_cover = search_results.items[0].album.images[0].url
        else:
            album_cover = ''

        data.append({
            'song_name': song_name,
            'artists': artists,
            'album_cover': album_cover
        })

    return {'tracks': data}

@app.route('/dashboard')
def dashboard():
    if 'refresh_token' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)