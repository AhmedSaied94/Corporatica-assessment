from flask import Blueprint

from app.image_data.resources import (
    ImageConvertResource,
    ImageCropResource,
    ImageDataResource,
    ImageDataResources,
    ImageDownloadResource,
    ImageMaskApplyResource,
    ImageMasksListResource,
    ImageMultipleUploadResource,
    ImageResizeResource,
    ImageRGBChangeResource,
    ImageThumbnailDownloadResource,
)

image_blueprint = Blueprint("image", __name__)

image_blueprint.add_url_rule(
    "/image/<int:image_id>/download", view_func=ImageDownloadResource.as_view("image_download_resource")
)
image_blueprint.add_url_rule("/image", view_func=ImageDataResources.as_view("image_resources"))
image_blueprint.add_url_rule("/image/<int:image_id>", view_func=ImageDataResource.as_view("image_resource_by_id"))
image_blueprint.add_url_rule(
    "/image/multiple", view_func=ImageMultipleUploadResource.as_view("image_multiple_upload_resource")
)
image_blueprint.add_url_rule(
    "/image/<int:image_id>/convert", view_func=ImageConvertResource.as_view("image_convert_resource")
)
image_blueprint.add_url_rule(
    "/image/<int:image_id>/thumbnail/download",
    view_func=ImageThumbnailDownloadResource.as_view("image_thumbnail_download_resource"),
)
image_blueprint.add_url_rule(
    "/image/<int:image_id>/mask/apply", view_func=ImageMaskApplyResource.as_view("image_mask_apply_resource")
)
image_blueprint.add_url_rule("/image/masks", view_func=ImageMasksListResource.as_view("image_masks_list_resource"))
image_blueprint.add_url_rule("/image/<int:image_id>/crop", view_func=ImageCropResource.as_view("image_crop_resource"))
image_blueprint.add_url_rule(
    "/image/<int:image_id>/resize", view_func=ImageResizeResource.as_view("image_resize_resource")
)
image_blueprint.add_url_rule(
    "/image/<int:image_id>/rgb", view_func=ImageRGBChangeResource.as_view("image_rgb_change_resource")
)
