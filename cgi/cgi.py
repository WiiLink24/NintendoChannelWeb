from models import db, TimePlayed, Recommendations
from flask import Response, request, Blueprint

cgi_blueprint = Blueprint("cgi", __name__)


@cgi_blueprint.post("/6/cgi-bin/config.cgi")
def config():
    resp = Response("0")
    return resp


@cgi_blueprint.post("/6/cgi-bin/bookmark.cgi")
def bookmark():
    resp = Response()
    resp.headers["X-RESULT"] = "0"
    return resp


@cgi_blueprint.post("/6/cgi-bin/getreview.cgi")
def get_review():
    recommendations = Recommendations.query.filter_by(serial_number=request.form.get("serialNumber")).all()

    body_string = str(len(recommendations)) + "\n"
    for rec in recommendations:
        # #OfRecs\nGameID,ConsoleType,?,Gender,Age,Percentage,Appeal,Mood,WithFriends,0...
        rec: Recommendations
        body_string += f"{rec.game_id},RVL,0,{rec.gender},{rec.age},{rec.recommendation_percent},{rec.appeal},{rec.gaming_mood},{rec.friend_or_alone},0\n"

    resp = Response(body_string)
    resp.headers["X-RESULT"] = "0"
    return resp


@cgi_blueprint.post("/6/cgi-bin/delreview.cgi")
def delete_review():
    recommendations = Recommendations.query.filter_by(serial_number=request.form.get("serialNumber")).all()
    for rec in recommendations:
        db.session.delete(rec)

    db.session.commit()

    resp = Response()
    resp.headers["X-RESULT"] = "0"
    return resp


@cgi_blueprint.post("/6/cgi-bin/accomplishment.cgi")
def store_time_played():
    """This route sends us the user's entire gameplay history."""
    # First retrieve the serial number from the payload.
    body = request.data.decode("utf-8")
    serial_number = body.split("serialNumber=")[1].split("&")[0]

    # Next we retrieve all the titles and their time data
    game_dict = {}
    for i, string in enumerate(body.split("&data=")):
        # Always the metadata
        if i == 0:
            continue

        game_id = string.split("%2C")[0]
        time_played = time_string_to_minutes(string.split("%2C")[2])

        try:
            game_dict[game_id][0] += time_played
            game_dict[game_id][1] += 1
        except KeyError:
            game_dict.update({game_id: [time_played, 1]})

    # Now we insert into the database
    for game_id, values in game_dict.items():
        queried_data = (
            TimePlayed.query.filter_by(serial_number=serial_number)
            .filter_by(game_id=game_id)
            .first()
        )

        if not queried_data:
            db_time_played = TimePlayed(
                serial_number=serial_number,
                game_id=game_id,
                times_played=values[1],
                time_played=values[0]
            )

            db.session.add(db_time_played)
        else:
            queried_data.times_played = values[1]
            queried_data.time_played = values[0]

        db.session.commit()

    resp = Response()
    resp.headers["X-RESULT"] = "0"
    return resp


def time_string_to_minutes(time_string: str) -> int:
    """Converts the awkward time string sent by us to minutes"""
    hours = int(time_string[:2]) * 60
    minutes = int(time_string[2:])

    return hours + minutes


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
    resp.headers["X-RESULT"] = "0"
    return resp

