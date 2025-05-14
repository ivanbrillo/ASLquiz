# UI Settings
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700
WINDOW_TITLE = "ASL Quiz Game"
FONT_FAMILY = "Comic Sans MS"

# Application settings
APP_TITLE = "ASL Quiz Game"
IMAGES_DIR = "asl_images"

# Model settings
MODEL_PATH = "full_model_augmented.keras"
ASL_CLASS_NAMES = list("ABCDEFGHIKLMNOPQRSTUVWXY")  # ASL alphabets without J and Z

#initialize to 1 in order to avoid division by zero for probability calculation
errors = {
    'video_tests': 1,
    'text_tests': 1,
    'text_total_errors': 1,
    'video_total_errors': 1,
    'letters': {ltr: {'video_errors': 1, 'text_errors': 1}
                for ltr in ASL_CLASS_NAMES}
}

# MediaPipe settings
MEDIAPIPE_HANDS_CONFIG = {
    "static_image_mode": False,
    "max_num_hands": 2,
    "min_detection_confidence": 0.8,
    "min_tracking_confidence": 0.8
}

# Camera settings
CAMERA_INDEX = 0
FRAME_UPDATE_MS = 10  # Update interval in milliseconds
