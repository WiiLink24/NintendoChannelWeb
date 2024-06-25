from models import db, Videos
from flask import url_for, flash, render_template, redirect, request, send_from_directory
from thegateway import thegateway_blueprint
from thegateway.mobiclip import validate_mobiclip, save_video_data, get_mobiclip_length
from thegateway.form import VideoForm
from thegateway.admin import oidc
from werkzeug.utils import redirect

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


@thegateway_blueprint.route("/thegateway/videos/add", methods=["GET", "POST"])
@oidc.require_login
def add_video():
    form = VideoForm()
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

    return render_template("video_add.html", form=form)


@thegateway_blueprint.route("/thegateway/movies/<movie_id>/thumbnail.jpg")
@oidc.require_login
def get_video_thumbnail(movie_id):
    return send_from_directory("./assets/videos/", f"{movie_id}.img")
