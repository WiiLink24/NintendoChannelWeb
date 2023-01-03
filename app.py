from flask import Flask, send_from_directory
from models import db, login
from cgi.cgi import cgi_blueprint
from thegateway import thegateway_blueprint
from werkzeug.serving import WSGIRequestHandler
from channel_static.main import channel_static_blueprint
import config
import ssl

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = config.db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = config.secret_key

db.init_app(app)
login.init_app(app)

app.register_blueprint(cgi_blueprint)
app.register_blueprint(thegateway_blueprint)
app.register_blueprint(channel_static_blueprint)

@app.before_first_request
def initialize_server():
    # Ensure our database is present.
    db.create_all()


db.configure_mappers()

if __name__ == "__main__":
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    context.set_ciphers("ALL:@SECLEVEL=0")
    context.load_cert_chain("server.pem", "server.key")
    app.run(host="::", port=443, ssl_context=context, debug=config.debug)
