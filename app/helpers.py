import uuid

from werkzeug.utils import secure_filename as secure_filename_werkzeug


def generate_random_filename(filename):
    """
    Generate a random filename.
    """
    return f'{uuid.uuid4().hex}.{filename.rsplit(".", 1)[1]}'


def secure_filename(filename):
    """
    Generate a secure filename.
    """
    return secure_filename_werkzeug(filename)
