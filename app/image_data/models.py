import os

from sqlalchemy.event import listens_for

from app.base_abstracts import ParentAbstract
from app.db import db

"""
    This is the models.py file for the image_data blueprint.
    it contains the following tables:
    - ImageDataFile: This table stores the information about the image data files uploaded by the user.
"""


class ImageDataFile(ParentAbstract):
    """
    This table stores the information about the image data files uploaded by the user.
    """

    __tablename__ = "image_data_files"

    name = db.Column(db.String(255))
    path = db.Column(db.String(255))
    histogram = db.Column(db.JSON)

    thumbnail = db.relationship(
        "ImageDataFileThumbnail",
        backref=db.backref("image_data_file", lazy=True),
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<ImageDataFile {self.id} {self.name}>"


class ImageDataFileThumbnail(ParentAbstract):
    """
    This table stores the information about the thumbnails of the image data files uploaded by the user.
    """

    __tablename__ = "image_data_file_thumbnails"

    image_data_file_id = db.Column(db.Integer, db.ForeignKey("image_data_files.id"), nullable=False)
    path = db.Column(db.String(255))

    def __repr__(self):
        return f"<ImageDataFileThumbnail {self.id} {self.image_data_file_id}>"


class ImageMask(ParentAbstract):
    """
    This table stores the information about the masks that can be applied to the image data files.
    """

    __tablename__ = "image_masks"

    name = db.Column(db.String(255))
    description = db.Column(db.Text)
    mask_data = db.Column(db.LargeBinary)
    # mask_type should be one of the following: 'gray' or 'rgb'
    mask_type = db.Column(db.String(10), default="gray")


@listens_for(ImageDataFile, "after_delete")
def delete_image_data_file_and_thumbnail(mapper, connection, target):

    if os.path.exists(target.path):
        os.remove(target.path)
    if target.thumbnail and os.path.exists(target.thumbnail.path):
        os.remove(target.thumbnail.path)
