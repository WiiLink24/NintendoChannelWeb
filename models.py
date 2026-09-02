from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import sqlalchemy.dialects.postgresql as pg_dialect

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
    name_ptbr = db.Column(db.String(102))
    length = db.Column(db.Integer)
    video_type = db.Column(db.Integer)
    date_added = db.Column(db.DateTime, nullable=False, server_default=func.now())


class TimePlayed(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    serial_number = db.Column(db.String)
    game_id = db.Column(db.String(6))
    times_played = db.Column(db.Integer())
    time_played = db.Column(db.Integer())
    last_updated = db.Column(db.DateTime, nullable=False, server_default=func.now())
    date_played = db.Column(db.Date)


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


class Banners(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    name_japanese = db.Column(db.String(102))
    name_english = db.Column(db.String(102))
    name_german = db.Column(db.String(102))
    name_french = db.Column(db.String(102))
    name_spanish = db.Column(db.String(102))
    name_italian = db.Column(db.String(102))
    name_dutch = db.Column(db.String(102))
    name_ptbr = db.Column(db.String(102))
    order = db.Column(db.Integer)
    
class Bookmarks(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    serial_number = db.Column(db.String)
    game_id = db.Column(db.String(4))

class Titles(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    game_id = db.Column(db.String(16), nullable=False)
    display_name = db.Column(db.String(512))
    title_en = db.Column(db.String(512), nullable=False)
    synopsis_en = db.Column(db.String)
    region = db.Column(db.String(64))
    languages = db.Column(db.String)
    game_type = db.Column(db.String)
    genre = db.Column(db.String)
    developer = db.Column(db.String(255))
    publisher = db.Column(db.String(255))
    release_year = db.Column(db.Integer)
    release_month = db.Column(db.Integer)
    release_day = db.Column(db.Integer)
    rating_type = db.Column(db.String(32))
    rating_value = db.Column(db.String(32))
    wifi_players = db.Column(db.Integer)
    input_players = db.Column(db.Integer)
    input_controls = db.Column(pg_dialect.JSONB)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    gamespy_id = db.Column(db.String, server_default="")
    is_featured = db.Column(db.Boolean, server_default=db.text("false::boolean"))
    wfc_observations = db.Column(pg_dialect.JSONB, server_default=db.text("'[]'::jsonb"))
    is_supported = db.Column(db.Integer, server_default=db.text("0::integer"))
