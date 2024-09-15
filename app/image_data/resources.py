import os

from flask import request, send_file
from flask_restful import Resource, fields, reqparse
from marshmallow import ValidationError
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import BadRequest

from app import db
from app.helpers import generate_random_filename, secure_filename
from app.image_data.models import ImageDataFile, ImageDataFileThumbnail, ImageMask
from app.image_data.schemas import (
    ImageConvertRequestSchema,
    ImageCropRequestSchema,
    ImageDataSchema,
    ImageMaskRequestSchema,
    ImageMaskSchema,
)
from app.image_data.service import ImageService
from config import Config

image_data_fields = {
    "id": fields.Integer,
    "name": fields.String,
    "path": fields.String,
    "created_at": fields.DateTime,
    "updated_at": fields.DateTime,
}


class ImageDataResource(Resource):

    def get(self, image_id):
        image_data = ImageDataFile.query.filter_by(id=image_id).first()
        if not image_data:
            return {"message": "Image not found"}, 404
        return ImageDataSchema().dump(image_data)

    def delete(self, image_id):
        image_data = ImageDataFile.query.get(image_id)
        db.session.delete(image_data)
        db.session.commit()

        return "", 204

    def put(self, image_id):
        parser = reqparse.RequestParser()
        parser.add_argument("image", type=FileStorage, location="files", required=True)
        try:
            args = parser.parse_args()
        except BadRequest as e:
            return e.data, e.code
        except Exception as e:
            return {"message": str(e)}, 400

        image_data = ImageDataFile.query.filter_by(id=image_id).first()
        if not image_data:
            return {"message": "Image not found"}, 404

        old_path = None
        if args["image"]:
            old_path = image_data.path
            if not ImageDataResource.allowed_file(args["image"].filename):
                return {"message": "Invalid file type"}, 400
            file_name = secure_filename(
                args["image"].filename.split(".")[0] + generate_random_filename(args["image"].filename)
            )
            path = f"{Config.MEDIA_DIR}/{file_name}"
            args["image"].save(path)
            image_data.path = path
            image_data.name = file_name
        db.session.commit()
        if old_path:
            if os.path.exists(old_path):
                os.remove(old_path)
            try:
                thumbnail_old_path = image_data.thumbnail.path
                thumbnail_path = f"{Config.MEDIA_DIR}/thumbnail_{image_data.name}"
                image_service = ImageService(image=image_data.path)
                image_service.generate_thumbnail(save_path=thumbnail_path)
                image_data.thumbnail.path = thumbnail_path
                db.session.commit()
                if os.path.exists(thumbnail_old_path):
                    os.remove(thumbnail_old_path)
            except Exception as e:
                db.session.rollback()
                if os.path.exists(image_data.path):
                    os.remove(image_data.path)
                return {"message": str(e)}, 500

        return ImageDataSchema().dump(image_data)

    @staticmethod
    def allowed_file(filename):
        """
        Check if the file extension is allowed.
        """
        ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
        return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


class ImageDownloadResource(Resource):

    def get(self, image_id):
        image_data = ImageDataFile.query.filter_by(id=image_id).first()
        if not image_data:
            return {"message": "Image not found"}, 404
        return send_file(
            f"{Config.MEDIA_FOLDER}/{image_data.path.split('/')[-1]}", download_name=image_data.name, as_attachment=True
        )


class ImageThumbnailDownloadResource(Resource):

    def get(self, image_id):
        image_data = ImageDataFile.query.filter_by(id=image_id).first()
        if not image_data:
            return {"message": "Image not found"}, 404
        return send_file(
            f"{Config.MEDIA_FOLDER}/{image_data.thumbnail.path.split('/')[-1]}",
            download_name=image_data.thumbnail.path.split("/")[-1],
            as_attachment=True,
        )


class ImageDataResources(Resource):

    def get(self):
        image_data = ImageDataFile.query.all()
        return ImageDataSchema().dump(image_data, many=True)

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("image", type=FileStorage, location="files", required=True)
        try:
            args = parser.parse_args()
        except BadRequest as e:
            return e.data, e.code
        except Exception as e:
            return {"message": str(e)}, 400

        if not ImageDataResource.allowed_file(args["image"].filename):
            return {"message": "Invalid file type"}, 400

        file_name = secure_filename(
            args["image"].filename.split(".")[0] + generate_random_filename(args["image"].filename)
        )
        path = f"{Config.MEDIA_DIR}/{file_name}"
        args["image"].save(path)
        image_service = ImageService(image=args["image"])
        image_data = ImageDataFile(name=file_name, path=path)
        db.session.add(image_data)
        db.session.commit()
        try:
            thumbnail_path = f"{Config.MEDIA_DIR}/thumbnail_{image_data.name}"
            image_service.generate_thumbnail(save_path=thumbnail_path)
            image_data.thumbnail = ImageDataFileThumbnail(path=thumbnail_path)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            if os.path.exists(image_data.path):
                os.remove(image_data.path)
            return {"message": str(e)}, 500
        return ImageDataSchema().dump(image_data), 201


class ImageMultipleUploadResource(Resource):

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("images", type=FileStorage, location="files", required=True, action="append")
        try:
            args = parser.parse_args()
        except BadRequest as e:
            return e.data, e.code
        except Exception as e:
            return {"message": str(e)}, 400

        images = []
        for image in args["images"]:
            if not ImageDataResource.allowed_file(image.filename):
                return {"message": "Invalid file type"}, 400
            file_name = secure_filename(image.filename.split(".")[0] + generate_random_filename(image.filename))
            path = f"{Config.MEDIA_DIR}/{file_name}"
            image.save(path)
            image_data = ImageDataFile(name=file_name, path=path)
            images.append(image_data)
        db.session.add_all(images)
        db.session.commit()
        try:
            for image in images:
                thumbnail_path = f"{Config.MEDIA_DIR}/thumbnail_{image.name}"
                image_service = ImageService(image=image.path)
                image_service.generate_thumbnail(save_path=thumbnail_path)
                image.thumbnail = ImageDataFileThumbnail(path=thumbnail_path)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            for image in images:
                if os.path.exists(image.path):
                    os.remove(image.path)
            return {"message": str(e)}, 500
        return ImageDataSchema().dump(images, many=True), 201


class ImageConvertResource(Resource):

    def post(self, image_id):
        try:
            body = ImageConvertRequestSchema().load(request.json)
        except ValidationError as e:
            return e.messages, 400
        except Exception:
            return {"message": "Invalid request Content-Type"}, 400
        image_data = ImageDataFile.query.filter_by(id=image_id).first()
        if not image_data:
            return {"message": "Image not found"}, 404
        image_service = ImageService(image=image_data.path)
        image = image_service.convert_to_format(format=body["format"])
        return send_file(image, download_name=f"{image_data.name.split('.')[0]}.{body['format']}", as_attachment=True)


class ImageMasksListResource(Resource):

    def get(self):
        masks = ImageMask.query.all()
        return ImageMaskSchema().dump(masks, many=True)


class ImageMaskApplyResource(Resource):

    def post(self, image_id):
        try:
            body = ImageMaskRequestSchema().load(request.json)
        except ValidationError as e:
            return e.messages, 400
        except Exception:
            return {"message": "Invalid request Content-Type"}, 400
        image_data = ImageDataFile.query.filter_by(id=image_id).first()
        if not image_data:
            return {"message": "Image not found"}, 404
        mask = ImageMask.query.get(body["mask_id"])

        image_service = ImageService(image=image_data.path)
        masked_image = image_service.apply_mask(mask)
        return send_file(
            masked_image, download_name=f"{image_data.name.split('.')[0]}_masked_{mask.name}.png", as_attachment=True
        )


class ImageCropResource(Resource):

    def post(self, image_id):
        try:
            body = ImageCropRequestSchema().load(request.json)
        except ValidationError as e:
            return e.messages, 400
        except Exception:
            return {"message": "Invalid request Content-Type"}, 400

        image_data = ImageDataFile.query.filter_by(id=image_id).first()
        image_service = ImageService(image=image_data.path)
        cropped_image = image_service.crop_image(body["x"], body["y"], body["width"], body["height"])
        return send_file(
            cropped_image, download_name=f"{image_data.name.split('.')[0]}_cropped.png", as_attachment=True
        )


class ImageResizeResource(Resource):

    def post(self, image_id):
        parser = reqparse.RequestParser()
        parser.add_argument("width", type=int, required=True)
        parser.add_argument("height", type=int, required=True)
        try:
            args = parser.parse_args()
        except BadRequest as e:
            return e.data, e.code
        except Exception as e:
            return {"message": str(e)}, 400

        image_data = ImageDataFile.query.filter_by(id=image_id).first()
        if not image_data:
            return {"message": "Image not found"}, 404
        image_service = ImageService(image=image_data.path)
        resized_image = image_service.resize_image(args["width"], args["height"])
        return send_file(
            resized_image, download_name=f"{image_data.name.split('.')[0]}_resized.png", as_attachment=True
        )


class ImageRGBChangeResource(Resource):

    @staticmethod
    def int_in_range(min_value, max_value):
        def validate(value):
            value = int(value)  # Convert value to int
            if value < min_value or value > max_value:
                raise ValueError(f"Value must be between {min_value} and {max_value}")
            return value

        return validate

    def post(self, image_id):
        parser = reqparse.RequestParser()
        parser.add_argument("red", type=ImageRGBChangeResource.int_in_range(0, 255), required=True)
        parser.add_argument("green", type=ImageRGBChangeResource.int_in_range(0, 255), required=True)
        parser.add_argument("blue", type=ImageRGBChangeResource.int_in_range(0, 255), required=True)
        try:
            args = parser.parse_args()
        except BadRequest as e:
            return e.data, e.code
        except Exception as e:
            return {"message": str(e)}, 400
        image_data = ImageDataFile.query.filter_by(id=image_id).first()
        if not image_data:
            return {"message": "Image not found"}, 404
        image_service = ImageService(image=image_data.path)
        changed_image = image_service.change_rgb_values(args["red"], args["green"], args["blue"])
        return send_file(
            changed_image, download_name=f"{image_data.name.split('.')[0]}_changed.png", as_attachment=True
        )
