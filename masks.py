from io import BytesIO

from PIL import Image, ImageDraw

from app import create_app
from app.db import db
from app.image_data.models import ImageMask


# Function to generate predefined masks
def generate_mask(shape, size=(256, 256), mask_type="gray", color=None):
    if mask_type == "gray":
        mask = Image.new("L", size, 0)  # Create a grayscale mask
        draw = ImageDraw.Draw(mask)

        if shape == "circle":
            draw.ellipse((50, 50, size[0] - 50, size[1] - 50), fill=255)
        elif shape == "square":
            draw.rectangle((50, 50, size[0] - 50, size[1] - 50), fill=255)
        elif shape == "horizontal_stripes":
            for i in range(0, size[1], 40):
                draw.rectangle((0, i, size[0], i + 20), fill=255)
        elif shape == "diagonal_stripes":
            for i in range(0, size[0], 40):
                draw.line((i, 0, 0, i), fill=255, width=20)
        elif shape == "border":
            draw.rectangle((10, 10, size[0] - 10, size[1] - 10), outline=255, width=20)
        elif shape == "fill":
            draw.rectangle((0, 0, size[0], size[1]), fill=255)
        elif shape == "outline":
            draw.rectangle((0, 0, size[0], size[1]), outline=255, width=20)
        elif shape == "ellipse":
            draw.ellipse((50, 50, size[0] - 50, size[1] - 50), fill=255)
        elif shape == "quad":
            draw.polygon([(100, 100), (200, 100), (200, 200), (100, 200)], fill=255)
        elif shape == "triangle":
            draw.polygon([(100, 200), (200, 200), (150, 100)], fill=255)
        elif shape == "pentagon":
            draw.polygon([(100, 200), (200, 200), (250, 150), (150, 100), (50, 150)], fill=255)

    elif mask_type == "rgb":
        mask = Image.new("RGB", size, (0, 0, 0))  # Create an RGB mask
        draw = ImageDraw.Draw(mask)

        if shape == "solid_red":
            draw.rectangle((0, 0, size[0], size[1]), fill=(255, 0, 0))
        elif shape == "solid_green":
            draw.rectangle((0, 0, size[0], size[1]), fill=(0, 255, 0))
        elif shape == "solid_blue":
            draw.rectangle((0, 0, size[0], size[1]), fill=(0, 0, 255))
        elif shape == "stripes":
            for i in range(0, size[1], 20):
                draw.rectangle((0, i, size[0], i + 10), fill=(255, 255, 255))  # White stripes
        elif shape == "dots":
            for i in range(0, size[0], 20):
                for j in range(0, size[1], 20):
                    draw.ellipse((i, j, i + 10, j + 10), fill=(255, 255, 255))  # White dots

    img_io = BytesIO()
    mask.save(img_io, "PNG")  # Save as PNG
    img_io.seek(0)
    return img_io.read()


# Function to create and save masks to the database
def create_default_masks():
    gray_masks = [
        {"name": "Circle Mask", "description": "A circular mask", "shape": "circle"},
        {"name": "Square Mask", "description": "A square mask", "shape": "square"},
        {"name": "Horizontal Stripes", "description": "Mask with horizontal stripes", "shape": "horizontal_stripes"},
        {"name": "Diagonal Stripes", "description": "Mask with diagonal stripes", "shape": "diagonal_stripes"},
        {"name": "Border Mask", "description": "Mask with a border", "shape": "border"},
        {"name": "Outline Mask", "description": "Mask with an outline", "shape": "outline"},
        {"name": "Ellipse Mask", "description": "Mask with an ellipse", "shape": "ellipse"},
        {"name": "Triangle Mask", "description": "Mask with a triangle", "shape": "triangle"},
        {"name": "Pentagon Mask", "description": "Mask with a pentagon", "shape": "pentagon"},
    ]

    rgb_masks = [
        {"name": "Solid Red Mask", "description": "A solid red mask", "shape": "solid_red"},
        {"name": "Solid Green Mask", "description": "A solid green mask", "shape": "solid_green"},
        {"name": "Solid Blue Mask", "description": "A solid blue mask", "shape": "solid_blue"},
        {"name": "Stripes Mask", "description": "Mask with stripes", "shape": "stripes"},
        {"name": "Dots Mask", "description": "Mask with dots", "shape": "dots"},
    ]

    masks_instances = []
    for mask_data in gray_masks:
        mask_binary = generate_mask(mask_data["shape"], mask_type="gray")
        mask = ImageMask(
            name=mask_data["name"], description=mask_data["description"], mask_data=mask_binary, mask_type="gray"
        )
        masks_instances.append(mask)

    for mask_data in rgb_masks:
        mask_binary = generate_mask(mask_data["shape"], mask_type="rgb")
        mask = ImageMask(
            name=mask_data["name"], description=mask_data["description"], mask_data=mask_binary, mask_type="rgb"
        )
        masks_instances.append(mask)

    db.session.add_all(masks_instances)
    db.session.commit()
    print("Default masks created and saved to the database.")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        create_default_masks()
