import os

import customtkinter as ctk
import cv2
from PIL import Image, ImageTk

from config import IMAGES_DIR


def create_blank_image(size=(200, 200)):
    return Image.new("RGBA", size, (0, 0, 0, 0))


def create_ctk_image(image, size=(200, 200)):
    """ Convert a PIL image to CTkImage """
    return ctk.CTkImage(light_image=image, size=size)


def load_asl_letter_image(letter, size=(200, 200)):
    """ Load an ASL letter image, process it and convert to CTkImage """
    image_path = os.path.join(IMAGES_DIR, f"{letter}.png")
    if not os.path.exists(image_path):
        return None

    # Load and process the image (flip for mirror effect)
    img = Image.open(image_path).resize(size).transpose(Image.FLIP_LEFT_RIGHT)
    img = img.convert("RGBA")

    # Extract alpha channel (since it is png, the background has alpha = zero) and use the uniform black color for images
    *_, alpha = img.split()
    black_img = Image.new("RGBA", img.size, (0, 0, 0, 255))
    processed_img = Image.merge("RGBA", (*black_img.split()[:3], alpha))

    return create_ctk_image(processed_img, size)


def process_frame(frame):
    """ Process webcam frame for display, from np.ndarray to ImageTk.PhotoImage """
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame)
    return ImageTk.PhotoImage(image=img)
