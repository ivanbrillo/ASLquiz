import customtkinter as ctk
import cv2

from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, CAMERA_INDEX
from models.hand_detector import HandDetector
from ui.home_screen import HomeScreen
from ui.quiz_screen import QuizScreen
from ui.phrase_screen import PhraseScreen
from utils.image_utils import create_blank_image, create_ctk_image


class ASLQuizApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title(WINDOW_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        # Initialize variables
        self.cap = None  # Camera object
        self.detector = None  # Hand detector object
        self.difficulty = "easy"
        self.target_letter = None

        # Create blank image for placeholders
        blank_image = create_blank_image()
        self.blank_ctk_image = create_ctk_image(blank_image)

        # Create frames for screens
        self.home_screen = HomeScreen(self)
        self.quiz_screen = QuizScreen(self)
        self.phrase_screen = PhraseScreen(self)

        # Set up initial screen
        self.show_home_screen()

    def show_home_screen(self):
        self.quiz_screen.pack_forget()
        self.phrase_screen.pack_forget()
        self.home_screen.pack(fill="both", expand=True)

        # Release camera and detector if active
        self._release_resources()

        # Adjust window size to fit home screen
        self._adjust_window_size()

    def start_quiz(self, difficulty):
        self.difficulty = difficulty
        self.home_screen.pack_forget()
        self.phrase_screen.pack_forget()
        self.quiz_screen.pack(fill="both", expand=True)

        # Initialize camera and hand detector
        self.cap = self._init_camera()
        self.detector = self._init_detector()

        # Adjust window size to fit quiz screen
        self._adjust_window_size()

        # Generate the first letter and start processing frames
        self.next_letter()
        self.update_frame()

    def start_phrase_practice(self, phrase=None):
        """Start the phrase practice mode"""
        self.home_screen.pack_forget()
        self.quiz_screen.pack_forget()
        self.phrase_screen.pack(fill="both", expand=True)

        # Initialize camera and hand detector if not already initialized
        self.cap = self._init_camera()
        self.detector = self._init_detector()

        # Adjust window size to fit phrase screen
        self._adjust_window_size()

        # Start the phrase practice with an optional specific phrase
        self.phrase_screen.start_phrase_practice(phrase)

    def _init_camera(self):
        """Initialize the camera"""
        cap = cv2.VideoCapture(CAMERA_INDEX)
        if not cap.isOpened():
            raise RuntimeError("Could not open webcam")
        return cap

    def _init_detector(self):
        """Initialize the hand detector"""
        return HandDetector()

    def next_letter(self):
        """Generate the next letter for the quiz"""
        # Let the quiz screen handle the letter selection and display
        self.quiz_screen.next_letter(self.difficulty)

    def update_frame(self):
        """Update the webcam feed and process hand gestures"""
        if not self.cap or not self.detector:
            return

        # Capture frame
        success, frame = self.cap.read()
        if not success:
            self.after(10, self.update_frame)
            return

        # Flip frame for mirror effect and process with hand detector
        frame = cv2.flip(frame, 1)
        processed_frame, results = self.detector.process_frame(frame)

        # Process hand detection results
        landmarks = self.detector.extract_landmarks(results)
        if landmarks is not None:
            # Get prediction
            predicted_letter, confidence = self.detector.predict_letter(landmarks)
            if predicted_letter:
                self.quiz_screen.update_prediction(predicted_letter)
        else:
            # Clear prediction when no hand detected
            self.quiz_screen.clear_prediction()

        # Update the canvas with the processed frame
        self.quiz_screen.update_canvas(processed_frame)

        # Schedule next frame update
        self.after(10, self.update_frame)

    def on_closing(self):
        """Handle application closing"""
        self._release_resources()
        self.destroy()

    def _release_resources(self):
        """Release camera and other resources"""
        if self.cap:
            self.cap.release()
            self.cap = None

        if self.detector:
            self.detector.close()
            self.detector = None

    def _adjust_window_size(self):
        """Adjust the window size to fit the current screen content"""
        self.update_idletasks()  # Ensure all geometry changes are applied
        width = self.winfo_reqwidth() + 50
        height = self.winfo_reqheight() + 20
        self.geometry(f"{width}x{height}")