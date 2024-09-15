from flask import request
from marshmallow import Schema, ValidationError, fields, validate, validates_schema

from app.image_data.models import ImageDataFile, ImageDataFileThumbnail, ImageMask
from app.image_data.service import ImageService


class ImageDataFileThumbnailSchema(Schema):
    path = fields.Method("get_thumbnail_full_url")

    class Meta:
        model = ImageDataFileThumbnail
        fields = ("id", "path", "created_at", "updated_at")

    def get_thumbnail_full_url(self, obj):
        return ImageService.generate_image_full_url(obj.path, request)


class ImageDataSchema(Schema):
    thumbnail = fields.Nested(ImageDataFileThumbnailSchema)
    path = fields.Method("get_image_full_url")
    histogram = fields.Method("get_histogram")

    class Meta:
        model = ImageDataFile
        fields = ("id", "name", "path", "created_at", "updated_at", "thumbnail", "histogram")

    def get_image_full_url(self, obj):
        return ImageService.generate_image_full_url(obj.path, request)

    def get_histogram(self, obj):
        return ImageService(obj.path).generate_histogram()


class ImageConvertRequestSchema(Schema):
    format = fields.String(required=True, validate=validate.OneOf(["png", "webp", "jpeg", "bmp", "tiff", "gif"]))


class ImageMaskSchema(Schema):

    class Meta:
        model = ImageMask
        fields = ("id", "name", "description", "created_at", "updated_at", "mask_type")


class ImageMaskRequestSchema(Schema):
    mask_id = fields.Integer(required=True)

    @validates_schema
    def validate_mask_id(self, data, **kwargs):
        mask_id = data["mask_id"]
        mask = ImageMask.query.filter_by(id=mask_id).first()
        if not mask:
            raise ValidationError({"mask_id": "Invalid mask id"})


class ImageCropRequestSchema(Schema):
    x = fields.Integer(required=True)
    y = fields.Integer(required=True)
    width = fields.Integer(required=True)
    height = fields.Integer(required=True)

    @validates_schema
    def validate_crop_request(self, data, **kwargs):
        image = ImageDataFile.query.filter_by(id=request.view_args["image_id"]).first()
        if not image:
            raise ValidationError({"image_id": "Invalid image id"})
        image = ImageService(image.path).pil_image
        x, y, width, height = data["x"], data["y"], data["width"], data["height"]
        if x < 0 or y < 0 or width < 0 or height < 0:
            raise ValidationError({"crop": "Invalid crop values"})
        if x + width > image.width:
            raise ValidationError({"width": "Invalid width value"})
        if y + height > image.height:
            raise ValidationError({"height": "Invalid height value"})
