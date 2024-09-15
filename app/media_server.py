from flask import Blueprint, send_from_directory

from config import Config

media_server = Blueprint("uploads", __name__)


@media_server.route("/<path:filename>")
def get_file(filename):
    try:
        return send_from_directory(Config.MEDIA_FOLDER, filename)
    except FileNotFoundError:
        return {"message": "File not found"}, 404


#
# Compare this snippet from app/image_data/service.py:
