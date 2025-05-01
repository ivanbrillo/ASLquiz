import customtkinter as ctk
import numpy as np

from config import FONT_FAMILY, ASL_CLASS_NAMES
from utils.image_utils import load_asl_letter_image, process_frame


class QuizScreen(ctk.CTkFrame):
    """Quiz screen with webcam feed and ASL detection"""

    def __init__(self, master):
        """
        Initialize the quiz screen

        Args:
            master: Parent widget (ASLQuizApp)
        """
        super().__init__(master)
        self.app = master
        self.target_letter = None
        self.target_ctk_img = None
        self.predicted_ctk_img = None
        self._build_ui()

    def _build_ui(self):
        """Build the UI elements"""
        # Title
        self.label_title = ctk.CTkLabel(
            self,
            text="ASL Quiz",
            font=(FONT_FAMILY, 24, "bold")
        )
        self.label_title.grid(row=0, column=0, columnspan=2, pady=10)

        # Camera canvas
        self.canvas = ctk.CTkCanvas(
            self,
            width=640,
            height=480,
            bg="black"
        )
        self.canvas.grid(row=1, column=0, columnspan=2, pady=10)

        # Instruction label
        self.label_instruction = ctk.CTkLabel(
            self,
            text="Show the sign for the letter below:",
            font=(FONT_FAMILY, 18)
        )
        self.label_instruction.grid(row=2, column=0, columnspan=2, pady=10)

        # Target letter display
        self.label_target = ctk.CTkLabel(
            self,
            text="",
            font=(FONT_FAMILY, 36),
            text_color="white"
        )
        self.label_target.grid(row=3, column=0, columnspan=2, pady=10)

        # Container for images
        self.image_container = ctk.CTkFrame(self, fg_color="transparent")
        self.image_container.grid(row=4, column=0, columnspan=2, pady=10)

        # Set up left side (target image)
        self._setup_target_side()

        # Set up right side (predicted image)
        self._setup_predicted_side()

        # Control buttons
        self.button_next = ctk.CTkButton(
            self,
            text="Next Letter",
            font=(FONT_FAMILY, 16),
            command=self.app.next_letter
        )
        self.button_next.grid(row=5, column=0, pady=10)

        self.button_home = ctk.CTkButton(
            self,
            text="Back to Home",
            font=(FONT_FAMILY, 16),
            command=self.app.show_home_screen
        )
        self.button_home.grid(row=5, column=1, pady=10)

    def _setup_target_side(self):
        """Set up the target image side"""
        self.target_side = ctk.CTkFrame(self.image_container, fg_color="transparent")
        self.target_side.grid(row=0, column=0, padx=30)

        # Label
        self.target_label = ctk.CTkLabel(
            self.target_side,
            text="Sign to Perform",
            font=(FONT_FAMILY, 16, "bold")
        )
        self.target_label.grid(row=0, column=0, pady=(0, 5))

        # Frame for image
        self.target_frame = ctk.CTkFrame(
            self.target_side,
            width=240,
            height=240,
            fg_color="transparent"
        )
        self.target_frame.grid(row=1, column=0)
        self.target_frame.grid_propagate(False)

        # Image label
        self.target_image_label = ctk.CTkLabel(
            self.target_frame,
            image=self.app.blank_ctk_image,
            text=""
        )
        self.target_image_label.place(relx=0.5, rely=0.5, anchor="center")

    def _setup_predicted_side(self):
        """Set up the predicted image side"""
        self.predicted_side = ctk.CTkFrame(self.image_container, fg_color="transparent")
        self.predicted_side.grid(row=0, column=1, padx=30)

        # Label
        self.predicted_label = ctk.CTkLabel(
            self.predicted_side,
            text="Predicted Sign",
            font=(FONT_FAMILY, 16, "bold")
        )
        self.predicted_label.grid(row=0, column=0, pady=(0, 5))

        # Frame for image
        self.predicted_frame = ctk.CTkFrame(
            self.predicted_side,
            width=240,
            height=240,
            fg_color="transparent"
        )
        self.predicted_frame.grid(row=1, column=0)
        self.predicted_frame.grid_propagate(False)

        # Image label
        self.predicted_image_label = ctk.CTkLabel(
            self.predicted_frame,
            image=self.app.blank_ctk_image,
            text=""
        )
        self.predicted_image_label.place(relx=0.5, rely=0.5, anchor="center")

        # Feedback label
        self.label_feedback = ctk.CTkLabel(
            self.predicted_side,
            text="",
            font=(FONT_FAMILY, 16)
        )
        self.label_feedback.grid(row=2, column=0, pady=(5, 0))

    def next_letter(self, difficulty):
        """
        Generate the next letter for the quiz

        Args:
            difficulty (str): Difficulty level
        """
        # Select a random letter
        self.target_letter = np.random.choice(ASL_CLASS_NAMES)
        self.label_target.configure(text=self.target_letter)
        self.label_feedback.configure(text="")

        if difficulty == "easy":
            # Load and display target image in easy mode
            self.target_ctk_img = load_asl_letter_image(self.target_letter)
            if self.target_ctk_img:
                self.target_image_label.configure(image=self.target_ctk_img, text="")
            else:
                self.target_image_label.configure(image=self.app.blank_ctk_image, text="Image not found")
            self.target_side.grid()  # Show target image
            self.predicted_side.grid()  # Show predicted image
        else:
            # Hide images in hard mode
            self.target_side.grid_remove()
            self.predicted_side.grid_remove()

        # Reset prediction image
        self.predicted_image_label.configure(image=self.app.blank_ctk_image, text="")

    def update_prediction(self, predicted_letter):
        """
        Update the prediction display

        Args:
            predicted_letter (str): The predicted letter
        """
        if predicted_letter == self.target_letter:
            self.label_feedback.configure(text="Correct!", text_color="green")
        else:
            self.label_feedback.configure(text=f"Detected: {predicted_letter}", text_color="red")

        # Display the predicted letter image only in easy mode
        if self.app.difficulty == "easy":
            self.predicted_ctk_img = load_asl_letter_image(predicted_letter)
            if self.predicted_ctk_img:
                self.predicted_image_label.configure(image=self.predicted_ctk_img, text="")
            else:
                self.predicted_image_label.configure(image=self.app.blank_ctk_image, text="")

    def clear_prediction(self):
        """Clear prediction display when no hand is detected"""
        self.label_feedback.configure(text="")
        self.predicted_image_label.configure(image=self.app.blank_ctk_image, text="")

    def update_canvas(self, frame):
        """
        Update the canvas with a new webcam frame

        Args:
            frame (numpy.ndarray): The processed webcam frame
        """
        imgtk = process_frame(frame)
        self.canvas.create_image(0, 0, anchor="nw", image=imgtk)
        self.canvas.imgtk = imgtk  # Keep a reference to prevent garbage collection
