from flask import Blueprint

thegateway_blueprint = Blueprint("thegateway", __name__)

from . import admin, videos, banner
