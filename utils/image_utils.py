"""
Image processing utilities for the ASL Quiz application
"""
import os
import cv2
import numpy as np
from PIL import Image, ImageTk
import customtkinter as ctk
from config import IMAGES_DIR


def create_blank_image(size=(200, 200)):
    """
    Create a transparent blank image

    Args:
        size (tuple): Image size as (width, height)

    Returns:
        PIL.Image: The created blank image
    """
    return Image.new("RGBA", size, (0, 0, 0, 0))


def create_ctk_image(image, size=(200, 200)):
    """
    Convert a PIL image to CTkImage

    Args:
        image (PIL.Image): The input image
        size (tuple): Image size as (width, height)

    Returns:
        CTkImage: The converted image
    """
    return ctk.CTkImage(light_image=image, size=size)


def load_asl_letter_image(letter, size=(200, 200)):
    """
    Load an ASL letter image, process it and convert to CTkImage

    Args:
        letter (str): The letter to load
        size (tuple): Image size as (width, height)

    Returns:
        CTkImage or None: The processed image or None if not found
    """
    image_path = os.path.join(IMAGES_DIR, f"{letter}.png")
    if not os.path.exists(image_path):
        return None

    # Load and process the image
    img = Image.open(image_path).resize(size).transpose(Image.FLIP_LEFT_RIGHT)
    img = img.convert("RGBA")

    # Extract alpha channel and create black background
    *_, alpha = img.split()
    black_img = Image.new("RGBA", img.size, (0, 0, 0, 255))

    # Merge alpha channel with black background
    processed_img = Image.merge("RGBA", (*black_img.split()[:3], alpha))

    return create_ctk_image(processed_img, size)


def process_frame(frame):
    """
    Process webcam frame for display

    Args:
        frame (numpy.ndarray): The input frame

    Returns:
        ImageTk.PhotoImage: The processed frame for display
    """
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame)
    return ImageTk.PhotoImage(image=img)