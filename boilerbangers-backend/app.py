# app.py
import os
from dotenv import load_dotenv
from flask import Flask
from auth.models import db
from auth.routes import auth_bp, seed_db

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev_secret')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    app.register_blueprint(auth_bp)

    with app.app_context():
        db.create_all()
        # seed DB users for demo
        seed_db()
    return app

if __name__ == '__main__':
    create_app().run(debug=True)