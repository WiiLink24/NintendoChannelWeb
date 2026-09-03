import cgi.consts
import datetime
from models import db, TimePlayed, Recommendations, Bookmarks
from flask import Response, request, Blueprint
from urllib.parse import parse_qs


cgi_blueprint = Blueprint("cgi", __name__)


@cgi_blueprint.post("/6/cgi-bin/config.cgi")
def config():
    resp = Response("0")
    return resp


@cgi_blueprint.post("/6/cgi-bin/bookmark.cgi")
def bookmark():
    body = parse_qs(request.data.decode("utf-8"))
    serial_number = body.get("serialNumber", [None])[0]
    
    changed = False
    for encoded_data in body.get("data", []):
        _, game_id, _, action = encoded_data.split(",") # Don't care about timestamp or platform
        
        if action.strip() == "1":
            changed |= db.session.query(Bookmarks).filter_by(
                serial_number=serial_number,
                game_id=game_id,
            ).delete() > 0
        else:
            if not db.session.query(Bookmarks).filter_by(
                serial_number=serial_number,
                game_id=game_id,
            ).first():
                db.session.add(Bookmarks(serial_number=serial_number, game_id=game_id))
                changed = True
    
    if changed:
        db.session.commit()

    resp = Response()
    resp.headers["X-FJHIEK"] = "0"
    resp.headers["X-RESULT"] = "0"
    return resp


@cgi_blueprint.post("/6/cgi-bin/getreview.cgi")
def get_review():
    recommendations = Recommendations.query.filter_by(
        serial_number=request.form.get("serialNumber")
    ).all()

    body_string = str(len(recommendations)) + "\n"
    for rec in recommendations:
        # #OfRecs\nGameID,ConsoleType,?,Gender,Age,Percentage,Appeal,Mood,WithFriends,0...
        rec: Recommendations
        body_string += f"{rec.game_id},RVL,0,{rec.gender},{rec.age},{rec.recommendation_percent},{rec.appeal},{rec.gaming_mood},{rec.friend_or_alone},0"

    resp = Response(body_string)
    resp.headers["X-FJHIEK"] = "0"
    resp.headers["X-RESULT"] = "0"
    return resp


@cgi_blueprint.post("/6/cgi-bin/delreview.cgi")
def delete_review():
    recommendations = Recommendations.query.filter_by(
        serial_number=request.form.get("serialNumber")
    ).all()
    for rec in recommendations:
        db.session.delete(rec)

    db.session.commit()

    resp = Response()
    resp.headers["X-FJHIEK"] = "0"
    resp.headers["X-RESULT"] = "0"
    return resp


@cgi_blueprint.post("/6/cgi-bin/accomplishment.cgi")
def store_time_played():
    """This route sends us the user's entire gameplay history."""
    # First retrieve the serial number from the payload.
    body = parse_qs(request.data.decode("utf-8"))
    serial_number = body.get("serialNumber", [None])[0]
    data = body.get("data", [])

    # Do simple validation of the request
    if (
        len(serial_number) != 24
        or request.headers.get("User-Agent") != serial_number
        or body.get("version") != ["0600"]
        or body.get("dataCount") != [str(len(data))]
        or body.get("platform") != ["RVL"]
    ):
        resp = Response()
        resp.status_code = 400
        return resp
    
    # Next we retrieve all the titles and their time data
    game_dict = {}
    for string in data:
        game_id = string.split(",")[0]
        # Check if game_id is valid (4 character alphanumeric, not a dev title)
        if (
            game_id in cgi.consts.ignore_ids
            or not len(game_id) == 4
            or not game_id.isalnum()
        ):
            continue

        date_played = date_string_to_date(string.split(",")[1])
        time_played = time_string_to_minutes(string.split(",")[2])

        try:
            game_dict[game_id].append(
                {
                    "time_played": time_played,
                    "date_played": date_played
                }
            )
        except KeyError:
            game_dict.update({game_id: [
                {
                    "time_played": time_played,
                    "date_played": date_played
                }
            ]})

    # Now we insert into the database
    for game_id, values in game_dict.items():
        for date in values:
            queried_data = (
                TimePlayed.query.filter_by(serial_number=serial_number)
                .filter_by(game_id=game_id)
                .filter_by(date_played=date["date_played"])
                .first()
            )

            if queried_data:
                # Should never happen; Nintendo Channel only sends us data for each date once.
                # However, people may use Dolphin Emulator with outdated NAND dumps. We should
                # account for this and save the bigger playtime.
                if date["time_played"] > queried_data.time_played:
                    queried_data.time_played = date["time_played"]
                    queried_data.last_updated = datetime.datetime.now()

            else:
                db_time_played = TimePlayed(
                    serial_number=serial_number,
                    game_id=game_id,
                    times_played=1,
                    time_played=date["time_played"],
                    date_played=date["date_played"]
                )

                db.session.add(db_time_played)

        db.session.commit()

    resp = Response()
    resp.headers["X-FJHIEK"] = "0"
    resp.headers["X-RESULT"] = "0"
    return resp


def time_string_to_minutes(time_string: str) -> int:
    """Converts the awkward time string sent by us to minutes"""
    hours = int(time_string[:2]) * 60
    minutes = int(time_string[2:])

    return hours + minutes

def date_string_to_date(date_string: str) -> datetime.date:
    """Converts the awkward date string sent by us to a date"""
    # We only get the last 2 digits of the year, this will be an issue eventually
    # Hopefully, I won't be around to deal with it
    year = int(date_string[:2]) + 2000
    month = int(date_string[2:4]) + 1
    day = int(date_string[4:6])

    return datetime.date(year, month, day)

@cgi_blueprint.post("/6/cgi-bin/review.cgi")
def review():
    # Store recommendation database
    serial_number = request.form.get("serialNumber")
    game_id = request.form.get("initialcode")
    # Male is 1 and Female is 2
    gender = request.form.get("q1")
    age = request.form.get("q2")
    recommend_percentage = request.form.get("q3")
    appeal = request.form.get("q4")
    gaming_mood = request.form.get("q5")
    friend_or_alone = request.form.get("q6")

    db_recommendation = Recommendations(
        serial_number=serial_number,
        game_id=game_id,
        gender=gender,
        age=age,
        recommendation_percent=recommend_percentage,
        appeal=appeal,
        gaming_mood=gaming_mood,
        friend_or_alone=friend_or_alone,
    )

    db.session.add(db_recommendation)
    db.session.commit()

    resp = Response()
    resp.headers["X-FJHIEK"] = "0"
    resp.headers["X-RESULT"] = "0"
    return resp
