# auth/routes.py
from flask import Blueprint, jsonify, session, url_for, redirect
from .models import db, User
from aggregator import aggregate_tracks

auth_bp = Blueprint('auth', __name__)

# ---------- Hard-coded users and events (development mode) ----------
# Two users with dorm/major/grade
HARDCODE_USERS = [
    dict(spotify_id='u1', email='a@purdue.edu', dorm='Earhart', major='CS', grade='Sophomore'),
    dict(spotify_id='u2', email='b@purdue.edu', dorm='Windsor', major='ME', grade='Junior'),
]

# Simulated recently played events across users
HARDCODE_EVENTS = [
    # u1 plays
    {'spotify_id':'u1','track_id':'t1','title':'Track One','artist':'Artist A','dorm':'Earhart','major':'CS','grade':'Sophomore'},
    {'spotify_id':'u1','track_id':'t2','title':'Track Two','artist':'Artist B','dorm':'Earhart','major':'CS','grade':'Sophomore'},
    {'spotify_id':'u1','track_id':'t1','title':'Track One','artist':'Artist A','dorm':'Earhart','major':'CS','grade':'Sophomore'},
    # u2 plays
    {'spotify_id':'u2','track_id':'t1','title':'Track One','artist':'Artist A','dorm':'Windsor','major':'ME','grade':'Junior'},
    {'spotify_id':'u2','track_id':'t3','title':'Track Three','artist':'Artist C','dorm':'Windsor','major':'ME','grade':'Junior'},
    {'spotify_id':'u2','track_id':'t3','title':'Track Three','artist':'Artist C','dorm':'Windsor','major':'ME','grade':'Junior'},
]

# Populate in-memory DB on startup for demonstration
def seed_db():
    existing = User.query.first()
    if existing:
        return
    for u in HARDCODE_USERS:
        user = User(spotify_id=u['spotify_id'], email=u['email'],
                    dorm=u['dorm'], major=u['major'], grade=u['grade'])
        db.session.add(user)
    db.session.commit()

@auth_bp.route('/seed')
def seed_route():
    seed_db()
    return jsonify({'message':'seeded users'})

# Endpoint that prints aggregated output to console and returns the chart JSON
@auth_bp.route('/charts')
def charts():
    # optional query params: dorm, major, grade
    from flask import request
    dorm = request.args.get('dorm')
    major = request.args.get('major')
    grade = request.args.get('grade')

    ranked = aggregate_tracks(HARDCODE_EVENTS, dorm=dorm, major=major, grade=grade, top_n=20)

    # Print to console for debugging
    print('--- Aggregated chart (dorm=%s major=%s grade=%s) ---' % (dorm, major, grade))
    for item in ranked:
        print(f"{item['track']}: {item['plays']}")

    return jsonify(ranked)