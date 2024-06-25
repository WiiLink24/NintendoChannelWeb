from flask import url_for, render_template
from thegateway import thegateway_blueprint
from flask_oidc import OpenIDConnect
from werkzeug.utils import redirect

import config

oidc = OpenIDConnect()


@thegateway_blueprint.record_once
def on_load(state):
    # Initialize OpenIDConnect with the current app context
    oidc.init_app(state.app)


@thegateway_blueprint.app_context_processor
def inject_oidc():
    return dict(oidc=oidc)


@thegateway_blueprint.route("/thegateway")
@thegateway_blueprint.route("/thegateway/")
def root():
    return redirect(url_for("thegateway.login"))


@thegateway_blueprint.route("/thegateway/login")
def login():
    if oidc.user_loggedin:
        return redirect(url_for("thegateway.admin"))

    return render_template("login.html")


@thegateway_blueprint.route("/thegateway/logout")
@oidc.require_login
def logout():
    oidc.logout()
    response = redirect(config.oidc_logout_url)
    response.set_cookie("session", expires=0)
    return response


@thegateway_blueprint.route("/thegateway/admin")
@oidc.require_login
def admin():
    return render_template("gateway.html")
