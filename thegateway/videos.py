from time import sleep

from models import db, Videos
from flask import (
    url_for,
    flash,
    render_template,
    redirect,
    request,
    send_from_directory,
    jsonify,
)
from thegateway import thegateway_blueprint
from thegateway.mobiclip import validate_mobiclip, save_video_data, get_mobiclip_length
from thegateway.form import VideoForm
from thegateway.admin import oidc
from werkzeug.utils import redirect
import threading
import subprocess
from werkzeug import exceptions
from flask_wtf.file import FileRequired


generate_status = {
    "completed": False,
    'message': "",
    "in_progress": False,
}


@thegateway_blueprint.route("/thegateway/videos/")
@oidc.require_login
def list_videos():
    # Get our current page, or start from scratch.
    page_num = request.args.get("page", default=1, type=int)

    # We want at most 20 movies per page.
    videos = Videos.query.order_by(Videos.id.asc()).paginate(
        page=page_num, per_page=20, error_out=False
    )

    return render_template(
        "video_list.html",
        videos=videos,
        type_length=videos.total,
    )


@thegateway_blueprint.route("/thegateway/videos/<movie_id>/edit", methods=["GET", "POST"])
@oidc.require_login
def edit_video(movie_id):
    form = VideoForm()
    form.upload.label.text = "Edit Video"

    movie = Videos.query.filter_by(id=movie_id).first()
    if not movie:
        return exceptions.NotFound()

    if form.validate_on_submit():
        thumbnail_data = None
        video_data = None
        if form.video.data:
            video_data = form.video.data.read()
            if validate_mobiclip(video_data):
                length = get_mobiclip_length(video_data)
                movie.length = length
            else:
                flash("Invalid movie")
                return render_template("video_action.html", form=form, action="Edit")

        if form.thumbnail.data:
            thumbnail_data = form.thumbnail.data.read()

        save_video_data(movie.id, thumbnail_data, video_data)

        movie.name_japanese = form.title_jpn.data
        movie.name_english = form.title_en.data
        movie.name_german = form.title_de.data
        movie.name_french = form.title_fr.data
        movie.name_spanish = form.title_es.data
        movie.name_italian = form.title_it.data
        movie.name_dutch = form.title_dutch.data
        movie.video_type = form.video_type.data
        db.session.commit()

        return redirect(url_for("thegateway.list_videos"))
    else:
        form.title_jpn.data = movie.name_japanese
        form.title_en.data = movie.name_english
        form.title_de.data = movie.name_german
        form.title_fr.data = movie.name_french
        form.title_es.data = movie.name_spanish
        form.title_it.data = movie.name_italian
        form.title_dutch.data = movie.name_dutch
        form.video_type.data = movie.video_type

    return render_template("video_action.html", form=form, action="Edit")


@thegateway_blueprint.route("/thegateway/videos/add", methods=["GET", "POST"])
@oidc.require_login
def add_video():
    form = VideoForm()
    form.video_type.validators = [FileRequired()]
    form.thumbnail.validators = [FileRequired()]

    if form.validate_on_submit():
        video = form.video.data
        thumbnail = form.thumbnail.data
        if video and thumbnail:
            video_data = video.read()
            thumbnail_data = thumbnail.read()

            if validate_mobiclip(video_data):
                # Get the Mobiclip's length from header.
                length = get_mobiclip_length(video_data)

                db_video = Videos(
                    name_japanese=form.title_jpn.data,
                    name_english=form.title_en.data,
                    name_german=form.title_de.data,
                    name_french=form.title_fr.data,
                    name_spanish=form.title_es.data,
                    name_italian=form.title_it.data,
                    name_dutch=form.title_dutch.data,
                    length=length,
                    video_type=form.video_type.data,
                )

                db.session.add(db_video)
                db.session.commit()

                save_video_data(db_video.id, thumbnail_data, video_data)

                return redirect(url_for("thegateway.list_videos"))
            else:
                flash("Invalid video!")
        else:
            flash("Error uploading video!")

    return render_template("video_action.html", form=form, action="Add")


@thegateway_blueprint.route("/thegateway/movies/<movie_id>/thumbnail.jpg")
@oidc.require_login
def get_video_thumbnail(movie_id):
    return send_from_directory("./assets/videos/", f"{movie_id}.img")


@thegateway_blueprint.post("/thegateway/generate")
@oidc.require_login
def generate_videos():
    def actually_generate_videos():
        message = "Successfully generated thumbnails and videos!"
        # Sleep for a second to give the web app time to process the fact that another user isn't generating.
        sleep(1)
        generate_status["in_progress"] = True

        # Generate videos first
        if subprocess.run(["./cli", "2"]).returncode != 0:
            message = "Error generating videos."
        else:
            # Now thumbnails
            if subprocess.run(["./cli", "3"]).returncode != 0:
                message = "Error generating thumbnails."

        generate_status["completed"] = True
        generate_status["message"] = message
        generate_status["in_progress"] = False

    if not generate_status["in_progress"]:
        threading.Thread(target=actually_generate_videos, daemon=True).start()

    return jsonify(generate_status)


@thegateway_blueprint.route("/thegateway/check_status")
def check_status():
    """Endpoint to check the current process status"""
    return jsonify(generate_status)
