from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()


class Videos(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    name_japanese = db.Column(db.String(102))
    name_english = db.Column(db.String(102))
    name_german = db.Column(db.String(102))
    name_french = db.Column(db.String(102))
    name_spanish = db.Column(db.String(102))
    name_italian = db.Column(db.String(102))
    name_dutch = db.Column(db.String(102))
    length = db.Column(db.Integer)
    video_type = db.Column(db.Integer)
    date_added = db.Column(db.DateTime, nullable=False, server_default=func.now())


class TimePlayed(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    serial_number = db.Column(db.String)
    game_id = db.Column(db.String(6))
    times_played = db.Column(db.Integer())
    time_played = db.Column(db.Integer())


class Recommendations(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    serial_number = db.Column(db.String)
    game_id = db.Column(db.String(6))
    gender = db.Column(db.Integer)
    age = db.Column(db.Integer)
    recommendation_percent = db.Column(db.Integer)
    appeal = db.Column(db.Integer)
    gaming_mood = db.Column(db.Integer)
    friend_or_alone = db.Column(db.Integer)
