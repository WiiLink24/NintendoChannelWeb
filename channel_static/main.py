from flask import Blueprint, send_from_directory
from config import debug

country_code_to_asset_dir = {
    "JP": 0,
    "AI": 2,
    "AG": 2,
    "AW": 2,
    "BS": 2,
    "BB": 2,
    "BZ": 2,
    "BO": 2,
    "BR": 2,
    "VG": 2,
    "CA": 2,
    "KY": 2,
    "CL": 2,
    "CO": 2,
    "CR": 2,
    "DM": 2,
    "DO": 2,
    "EC": 2,
    "SV": 2,
    "GF": 2,
    "GD": 2,
    "GP": 2,
    "GT": 2,
    "GY": 2,
    "HT": 2,
    "HN": 2,
    "JM": 2,
    "MQ": 2,
    "MX": 2,
    "MS": 2,
    "AN": 2,
    "NI": 2,
    "PA": 2,
    "PY": 2,
    "PE": 2,
    "KN": 2,
    "LC": 2,
    "VC": 2,
    "SR": 2,
    "TT": 2,
    "TC": 2,
    "US": 2,
    "UY": 2,
    "VI": 2,
    "VE": 2,
}

language_code_to_asset_dir = {
    "ja": 0,
    "en": 1,
    "de": 2,
    "fr": 3,
    "es": 4,
    "it": 5,
    "nl": 6,
}

channel_static_blueprint = Blueprint("static_channel", __name__)

if debug:

    @channel_static_blueprint.route(
        "/f/248/49125/1h/entus.wapp.wii.com/6/VHFQ3VjDqKlZDIWAyCY0S38zIoGAoTEqvJjr8OVua0G8UwHqixKklOBAHVw9UaZmTHqOxqSaiDd5bjhSQS6hk6nkYJVdioanD5Lc8mOHkobUkblWf8KxczDUZwY84FIV/list/<country>/<language>/434968891.LZ"
    )
    def download_list(country, language):
        try:
            country_dir = country_code_to_asset_dir[country]
        except KeyError:
            country_dir = 1

        language_dir = language_code_to_asset_dir[language]

        return send_from_directory(
            f"./channel_static/static/{country_dir}/{language_dir}/", "dllist.bin"
        )

    @channel_static_blueprint.route(
        "/f/248/49125/1h/entus.wapp.wii.com/6/VHFQ3VjDqKlZDIWAyCY0S38zIoGAoTEqvJjr8OVua0G8UwHqixKklOBAHVw9UaZmTHqOxqSaiDd5bjhSQS6hk6nkYJVdioanD5Lc8mOHkobUkblWf8KxczDUZwY84FIV/thumbnail/<country>/<language>/434968891-001.thumb"
    )
    def thumbnail(country, language):
        return send_from_directory(f"./channel_static/static/", "thumbnail.bin")
