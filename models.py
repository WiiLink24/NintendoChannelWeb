from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func

db = SQLAlchemy()
login = LoginManager()


@login.user_loader
def load_user(_id):
    return User.query.get(int(_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True, unique=True)
    username = db.Column(db.String(100))
    password_hash = db.Column(db.String)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


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
