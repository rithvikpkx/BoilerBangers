# auth/models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spotify_id = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(255))
    dorm = db.Column(db.String(50))
    major = db.Column(db.String(50))
    grade = db.Column(db.String(20))
    # tokens omitted in hard-coded mode