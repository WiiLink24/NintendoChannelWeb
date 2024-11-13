from models import db, Banners
from flask import (
    url_for,
    flash,
    render_template,
    redirect,
    request,
    send_from_directory,
)
from thegateway.imageencode import banner_encode
from thegateway.operations import manage_delete_item
from thegateway import thegateway_blueprint
from thegateway.admin import oidc
from werkzeug.utils import redirect
from thegateway.form import BannerForm
import os


@thegateway_blueprint.route("/thegateway/banners/")
@oidc.require_login
def list_banners():
    # Has to be 3 banner images.
    banners = Banners.query.order_by(Banners.id.asc()).paginate(
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

    return render_template("banner_add.html", form=form)


@thegateway_blueprint.route(
    "/thegateway/banners/<banner_id>/remove", methods=["GET", "POST"]
)
@oidc.require_login
def remove_movie(banner_id):
    def drop_banner():
        banner = Banners.query.filter_by(id=banner_id).first()
        db.session.delete(banner)
        db.session.commit()
        os.remove(f"./assets/banners/{banner_id}.img")
        return redirect(url_for("list_categories"))

    return manage_delete_item(banner_id, "banner", drop_banner)


@thegateway_blueprint.route("/thegateway/banners/<banner_id>/thumbnail.jpg")
@oidc.require_login
def get_banner_thumbnail(banner_id):
    return send_from_directory("./assets/banners/", f"{banner_id}.img")
