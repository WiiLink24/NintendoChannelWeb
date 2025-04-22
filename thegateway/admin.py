from flask import url_for, render_template, session
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


# Error handling
@thegateway_blueprint.errorhandler(404)
def page_not_found(e):
    return render_template('errors/error.html', 
                          error_code=404,
                          error_title="Page Not Found",
                          error_message="The page you're looking for doesn't exist or has been moved.",
                          error_details=str(e)), 404

@thegateway_blueprint.errorhandler(500)
def server_error(e):
    return render_template('errors/error.html',
                          error_code=500,
                          error_title="Server Error",
                          error_message="Something went wrong on our end. Please contact a developer.",
                          error_details=str(e)), 500

@thegateway_blueprint.errorhandler(401)
def unauthorized(e):
    return render_template('errors/error.html',
                          error_code=401,
                          error_title="Unauthorized",
                          error_message="You need to be authenticated to access this resource.",
                          error_details=str(e)), 401

@thegateway_blueprint.errorhandler(403)
def forbidden(e):
    return render_template('errors/error.html',
                          error_code=403,
                          error_title="Forbidden",
                          error_message="You don't have permission to access this resource.",
                          error_details=str(e)), 403

@thegateway_blueprint.errorhandler(Exception)
def handle_exception(e):
    if hasattr(e, 'code') and 400 <= e.code < 600:
        return e
    
    if "MismatchingStateError" in str(e) or "invalid_request" in str(e):
        session.clear()
        return render_template('errors/error.html',
                              error_code="Auth",
                              error_title="Authentication Error",
                              error_message="There was a problem with your authentication session. Please try logging in again.",
                              error_details=str(e),
                              auto_redirect=True), 400
    
    return render_template('errors/error.html',
                          error_code=500,
                          error_title="Server Error",
                          error_message="An unexpected error occurred.",
                          error_details=str(e)), 500