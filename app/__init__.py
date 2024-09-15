from flask import Flask
from flask_migrate import Migrate

from app.db import db
from app.image_data import image_blueprint
from app.media_server import media_server
from app.tabular_data import tabular_blueprint
from app.text_data import text_blueprint

# from app.text_data import text_blueprint

migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    db.init_app(app)

    migrate.init_app(app, db)

    # Register blueprints for each data type app
    app.register_blueprint(tabular_blueprint, url_prefix="/tabular")
    app.register_blueprint(media_server, url_prefix="/uploads")
    app.register_blueprint(image_blueprint, url_prefix="/images")
    app.register_blueprint(text_blueprint, url_prefix="/text")

    return app
