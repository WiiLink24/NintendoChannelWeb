from models import db, Banners
from flask import (
    url_for,
    flash,
    render_template,
    redirect,
    request,
    send_from_directory,
    jsonify,
)
from thegateway.imageencode import banner_encode
from thegateway.operations import manage_delete_item
from thegateway import thegateway_blueprint
from thegateway.admin import oidc
from werkzeug.utils import redirect
from thegateway.form import BannerForm
from sqlalchemy import between
from time import sleep
import threading
import subprocess
import os
from werkzeug import exceptions


banner_generate_status = {
    "completed": False,
    "message": "",
    "in_progress": False,
}


def save_banner_data(banner_id: int, thumbnail_data: bytes):
    thumbnail_data = banner_encode(thumbnail_data)
    thumbnail = open(f"./assets/banners/{banner_id}.img", "wb")
    thumbnail.write(thumbnail_data)
    thumbnail.close()


@thegateway_blueprint.route("/thegateway/banners/")
@oidc.require_login
def list_banners():
    # Has to be 3 banner images.
    banners = Banners.query.order_by(Banners.order.asc()).paginate(
        per_page=3, error_out=False
    )

    return render_template(
        "banner_list.html",
        banners=banners,
        type_length=banners.total,
    )


@thegateway_blueprint.route("/thegateway/banners/add", methods=["GET", "POST"])
@oidc.require_login
def add_banner():
    form = BannerForm()
    if form.validate_on_submit():
        thumbnail = form.thumbnail.data
        if thumbnail:
            thumbnail_data = thumbnail.read()
            db_banner = Banners(
                name_japanese=form.title_jpn.data,
                name_english=form.title_en.data,
                name_german=form.title_de.data,
                name_french=form.title_fr.data,
                name_spanish=form.title_es.data,
                name_italian=form.title_it.data,
                name_dutch=form.title_dutch.data,
                order=Banners.query.count() + 1,
            )

            db.session.add(db_banner)
            db.session.commit()

            # Resize and upload banner
            banner = banner_encode(thumbnail_data)
            if not os.path.isdir("./assets/banners"):
                os.makedirs("./assets/banners")

            with open(f"./assets/banners/{db_banner.id}.img", "wb") as f:
                f.write(banner)

            return redirect(url_for("thegateway.list_banners"))
        else:
            flash("Error uploading image!")

    return render_template("banner_action.html", form=form, action="Upload New")


@thegateway_blueprint.route("/thegateway/banners/<banner_id>/edit", methods=["GET", "POST"])
@oidc.require_login
def edit_banner(banner_id):
    form = BannerForm()
    form.upload.label.text = "Edit Banner"

    banner = Banners.query.filter_by(id=banner_id).first()
    if not banner:
        return exceptions.NotFound()

    if form.validate_on_submit():
        thumbnail_data = None
        if form.thumbnail.data:
            thumbnail_data = form.thumbnail.data.read()
        else:
            flash("Invalid banner")
            return render_template("banner_action.html", form=form, action="Edit")

        save_banner_data(banner_id, thumbnail_data)

        banner.name_japanese = form.title_jpn.data
        banner.name_english = form.title_en.data
        banner.name_german = form.title_de.data
        banner.name_french = form.title_fr.data
        banner.name_spanish = form.title_es.data
        banner.name_italian = form.title_it.data
        banner.name_dutch = form.title_dutch.data
        db.session.commit()

        return redirect(url_for("thegateway.list_banners"))
    else:
        form.title_jpn.data = banner.name_japanese
        form.title_en.data = banner.name_english
        form.title_de.data = banner.name_german
        form.title_fr.data = banner.name_french
        form.title_es.data = banner.name_spanish
        form.title_it.data = banner.name_italian
        form.title_dutch.data = banner.name_dutch

    return render_template("banner_action.html", form=form, action="Edit")


@thegateway_blueprint.route(
    "/thegateway/banners/<banner_id>/remove", methods=["GET", "POST"]
)
@oidc.require_login
def remove_banner(banner_id):
    def drop_banner():
        banner = Banners.query.filter_by(id=banner_id).first()
        db.session.delete(banner)
        db.session.commit()
        os.remove(f"./assets/banners/{banner_id}.img")
        return redirect(url_for("thegateway.list_banners"))

    return manage_delete_item(banner_id, "banner", drop_banner)


@thegateway_blueprint.route("/thegateway/banners/move/<order>/<direction>")
@oidc.require_login
def move_banner(order, direction):
    order = int(order)
    if direction == "up":
        # We require the current banner and the one before it.
        banners = (
            Banners.query.filter(Banners.order.between(order - 1, order))
            .order_by(Banners.order.asc())
            .all()
        )
        banners[0].order += 1
        banners[1].order -= 1
    elif direction == "down":
        # We require the current banner and the one after it.
        banners = (
            Banners.query.filter(Banners.order.between(order, order + 1))
            .order_by(Banners.order.asc())
            .all()
        )
        banners[0].order += 1
        banners[1].order -= 1

    db.session.commit()
    return redirect(url_for("thegateway.list_banners"))


@thegateway_blueprint.route("/thegateway/banners/<banner_id>/thumbnail.jpg")
@oidc.require_login
def get_banner_thumbnail(banner_id):
    return send_from_directory("./assets/banners/", f"{banner_id}.img")


@thegateway_blueprint.post("/thegateway/banners/generate")
@oidc.require_login
def generate_banners():
    def actually_generate_banners():
        message = "Successfully generated banners!"
        # Sleep for a second to give the web app time to process the fact that another user isn't generating.
        sleep(1)
        banner_generate_status["in_progress"] = True

        # Generate videos first
        if subprocess.run(["./cli", "4"]).returncode != 0:
            message = "Error generating banners."

        banner_generate_status["completed"] = True
        banner_generate_status["message"] = message
        banner_generate_status["in_progress"] = False

    if not banner_generate_status["in_progress"]:
        threading.Thread(target=actually_generate_banners, daemon=True).start()

    return jsonify(banner_generate_status)


@thegateway_blueprint.route("/thegateway/banners/check_status")
def check_banner_status():
    """Endpoint to check the current process status"""
    return jsonify(banner_generate_status)
