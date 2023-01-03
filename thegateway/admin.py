from models import db, User, login
import os
from flask import url_for, flash, render_template, send_from_directory
from thegateway import thegateway_blueprint
from flask_login import login_required, login_user, logout_user, current_user
from thegateway.form import LoginForm, NewUserForm, ChangePasswordForm
from werkzeug.utils import redirect


@login.unauthorized_handler
def unauthorized():
    return redirect(url_for("thegateway.root"))


@thegateway_blueprint.route("/thegateway")
@thegateway_blueprint.route("/thegateway/")
def root():
    return redirect(url_for("thegateway.login"))


@thegateway_blueprint.route("/thegateway/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("thegateway.admin"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
        else:
            login_user(user, remember=False)
            return redirect(url_for("thegateway.admin"))

    return render_template("login.html", form=form)


@thegateway_blueprint.route("/thegateway/create", methods=["GET", "POST"])
@login_required
def new_user():
    form = NewUserForm()
    if form.validate_on_submit():
        u = User(username=form.username.data)
        u.set_password(form.password1.data)
        db.session.add(u)
        db.session.commit()

        return redirect(url_for("thegateway.root"))

    return render_template("user_new.html", form=form)


@thegateway_blueprint.route("/thegateway/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        u = User.query.filter_by(username=current_user.username).first()
        u.set_password(form.new_password.data)
        db.session.add(u)
        db.session.commit()
        return redirect(url_for("thegateway.admin"))

    return render_template(
        "user_pwchange.html", form=form, username=current_user.username
    )


@thegateway_blueprint.route("/thegateway/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("thegateway.login"))


@thegateway_blueprint.route("/thegateway/admin")
@login_required
def admin():
    return render_template("gateway.html")


