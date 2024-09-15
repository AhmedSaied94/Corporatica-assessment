from io import BytesIO

import numpy as np
from PIL import Image

from app.image_data.models import ImageMask


class ImageService:

    def __init__(self, image):
        assert self.is_valid_image(image), "Invalid image file"
        self.image = image
        self.pil_image = Image.open(image)

    @staticmethod
    def is_valid_image(image):
        """
        Check if the file is a valid image

        Args:
            image (str or file): The image file or path to the image file
            return (bool): True if the file is a valid image, False otherwise
        """
        try:
            img = Image.open(image)
            img.verify()
            return True
        except Exception:
            return False

    def generate_histogram(self):
        """
        Generate the histogram of the image
        """
        return self.pil_image.histogram()

    def convert_to_format(self, format: str):
        img_io = BytesIO()
        image = self.pil_image
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.save(img_io, format=format.upper())
        img_io.seek(0)
        return img_io

    def convert_to_io(self, image: Image):
        img_io = BytesIO()
        image.save(img_io, format=self.pil_image.format)
        img_io.seek(0)
        return img_io

    def apply_mask(self, mask: ImageMask):
        image = self.pil_image.convert("RGBA")
        if mask.mask_type == "rgb":
            mask_image = Image.open(BytesIO(mask.mask_data)).convert("RGBA")
            mask_image = mask_image.resize(image.size)
            masked_image = Image.blend(image, mask_image, alpha=0.5)
        else:
            mask_image = Image.open(BytesIO(mask.mask_data)).convert("L")
            mask_image = mask_image.resize(image.size)
            masked_image = Image.composite(image, Image.new("RGBA", image.size, (255, 255, 255, 0)), mask_image)

        return self.convert_to_io(masked_image)

    def crop_image(self, x: int, y: int, width: int, height: int) -> BytesIO:
        cropped_img = self.pil_image.crop((x, y, x + width, y + height))
        return self.convert_to_io(cropped_img)

    def resize_image(self, width: int, height: int) -> BytesIO:
        resized_img = self.pil_image.resize((width, height))
        return self.convert_to_io(resized_img)

    def generate_thumbnail(self, size=(128, 128), save_path=None):
        thumbnail = self.pil_image.copy()
        thumbnail.thumbnail(size)
        if save_path:
            thumbnail.save(save_path)
        return thumbnail

    def convert_to_rgb(self, image: Image):
        return image.convert("RGB")

    @staticmethod
    def generate_image_full_url(image_path, request):
        return request.url_root + image_path

    def convert_to_array(self, image: Image, dtype="uint8"):
        return np.array(image, dtype=dtype)

    def change_rgb_values(self, red: int, green: int, blue: int) -> BytesIO:
        """
        Change the RGB values of an image using NumPy for better performance.

        :param red: The new red value to apply (0-255)
        :param green: The new green value to apply (0-255)
        :param blue: The new blue value to apply (0-255)
        :return: byte_io: The new image as a byte stream
        """
        # Ensure the image is in RGB mode
        image = self.pil_image
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Convert the image to a NumPy array
        img_array = np.array(image, dtype="int16")

        # Adjust RGB values using broadcasting and clamping
        img_array[:, :, 0] = np.clip(img_array[:, :, 0] + red, 0, 255)  # Red channel
        img_array[:, :, 1] = np.clip(img_array[:, :, 1] + green, 0, 255)  # Green channel
        img_array[:, :, 2] = np.clip(img_array[:, :, 2] + blue, 0, 255)  # Blue channel

        # Convert back to uint8 to restore it to an image
        img_array = img_array.astype("uint8")

        # Convert the NumPy array back to a PIL image
        new_image = Image.fromarray(img_array, "RGB")

        return self.convert_to_io(new_image)
