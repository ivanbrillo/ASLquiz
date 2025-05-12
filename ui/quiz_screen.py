import random
import customtkinter as ctk
import numpy as np

from config import FONT_FAMILY, ASL_CLASS_NAMES
from utils.image_utils import load_asl_letter_image, process_frame


class QuizScreen(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)
        self.app = master
        self.target_letter = None
        self.test_mode = None  # 'video' or 'image'
        self._build_ui()

    def _build_ui(self):
        # Configure grid weights
        self.grid_columnconfigure((0, 1), weight=1)

        # Title
        self.label_title = ctk.CTkLabel(self, text="ASL Quiz", font=(FONT_FAMILY, 24, "bold"))
        self.label_title.grid(row=0, column=0, columnspan=2, pady=10)

        # Video canvas
        self.canvas = ctk.CTkCanvas(self, width=500, height=480, bg="black")
        self.canvas.grid(row=1, column=0, columnspan=2, pady=10)

        # Instruction
        self.label_instruction = ctk.CTkLabel(
            self, text="Show the sign for the letter below:", font=(FONT_FAMILY, 18)
        )
        self.label_instruction.grid(row=2, column=0, columnspan=2, pady=5)

        # Target letter (video mode)
        self.label_target = ctk.CTkLabel(
            self, text="", font=(FONT_FAMILY, 36), text_color="white"
        )
        self.label_target.grid(row=3, column=0, columnspan=2, pady=5)

        # Container: easy-video images (side-by-side)
        self.video_image_container = ctk.CTkFrame(self, fg_color="transparent")
        self.video_image_container.grid_columnconfigure((0,1), weight=1)

        # Target image in video-easy
        self.video_target_image = ctk.CTkLabel(
            self.video_image_container, image=self.app.blank_ctk_image, text=""
        )
        self.video_target_image.grid(row=0, column=0, padx=20)

        # Predicted image in video-easy
        self.video_predicted_image = ctk.CTkLabel(
            self.video_image_container, image=self.app.blank_ctk_image, text=""
        )
        self.video_predicted_image.grid(row=0, column=1, padx=20)

        # Container: image-test (centered)
        self.image_test_container = ctk.CTkFrame(self, fg_color="transparent")
        self.image_test_container.grid_columnconfigure(0, weight=1)
        self.image_test_image = ctk.CTkLabel(
            self.image_test_container, image=self.app.blank_ctk_image, text=""
        )
        self.image_test_image.place(relx=0.5, rely=0.5, anchor="center")

        # Text input (image mode)
        self.entry_input = ctk.CTkEntry(self, width=200, font=(FONT_FAMILY, 16))
        self.button_submit = ctk.CTkButton(
            self, text="Submit", font=(FONT_FAMILY, 16), command=self._on_submit
        )

        # Feedback
        self.label_feedback = ctk.CTkLabel(
            self, text="", font=(FONT_FAMILY, 24, "bold")
        )
        self.label_feedback.grid(row=6, column=0, columnspan=2, pady=10)

        # Controls
        self.button_next = ctk.CTkButton(
            self, text="Next Letter", font=(FONT_FAMILY, 16), command=self.app.next_letter
        )
        self.button_next.grid(row=7, column=0, pady=(0, 30), sticky="e", padx=(0, 10))
        self.button_home = ctk.CTkButton(
            self, text="Back to Home", font=(FONT_FAMILY, 16), command=self.app.show_home_screen
        )
        self.button_home.grid(row=7, column=1, pady=(0, 30), sticky="w", padx=(10, 0))

    def next_letter(self, difficulty):
        # Hide all optional UI
        self.canvas.grid_remove()
        self.video_image_container.grid_remove()
        self.image_test_container.grid_remove()
        self.entry_input.grid_remove()
        self.button_submit.grid_remove()
        self.label_target.configure(text="")
        self.label_feedback.configure(text="")

        # Pick mode and letter
        self.test_mode = 'image' if random.random() < 0.3 else 'video'
        self.target_letter = np.random.choice(ASL_CLASS_NAMES)

        if self.test_mode == 'video':
            # Show camera & prompt
            self.canvas.grid()
            self.label_instruction.configure(text="Show the sign for the letter below:")
            self.label_target.configure(text=self.target_letter)

            if difficulty == 'easy':
                # Show both images side-by-side
                self.video_image_container.grid(row=4, column=0, columnspan=2, pady=5)
                # Target
                img_t = load_asl_letter_image(self.target_letter)
                self.video_target_image.configure(
                    image=img_t or self.app.blank_ctk_image,
                    text="" if img_t else "Image not found"
                )
                # Reset predicted
                self.video_predicted_image.configure(image=self.app.blank_ctk_image, text="")
        else:
            # Static image test + input
            self.canvas.grid_remove()
            self.label_instruction.configure(text="Identify the letter shown in the image:")
            self.image_test_container.grid(row=4, column=0, columnspan=2, pady=5, sticky="nsew")
            img = load_asl_letter_image(self.target_letter)
            self.image_test_image.configure(
                image=img or self.app.blank_ctk_image,
                text="" if img else "Image not found"
            )
            self.entry_input.grid(row=5, column=0, pady=10)
            self.button_submit.grid(row=5, column=1, pady=10)

        # Adjust layout
        self.app._adjust_window_size()

    def update_prediction(self, predicted_letter):
        # Always provide feedback in video mode
        if self.test_mode == 'video':
            if predicted_letter == self.target_letter:
                self.label_feedback.configure(text="Correct!", text_color="green")
            else:
                self.label_feedback.configure(text=f"Detected: {predicted_letter}", text_color="red")

            # Show predicted image only in easy mode
            if self.app.difficulty == 'easy':
                img_p = load_asl_letter_image(predicted_letter)
                self.video_predicted_image.configure(
                    image=img_p or self.app.blank_ctk_image,
                    text=""
                )

    def clear_prediction(self):
        if self.test_mode == 'video':
            # Show no-detection feedback
            self.label_feedback.configure(text="Detected: None", text_color="red")
            # Clear predicted sign
            self.video_predicted_image.configure(image=self.app.blank_ctk_image, text="")

    def update_canvas(self, frame):
        if self.test_mode == 'video':
            imgtk = process_frame(frame)
            self.canvas.create_image(0, 0, anchor="nw", image=imgtk)
            self.canvas.imgtk = imgtk

    def _on_submit(self):
        user_input = self.entry_input.get().strip().upper()
        if not user_input:
            return
        if user_input == self.target_letter:
            self.label_feedback.configure(text="Correct!", text_color="green")
        else:
            self.label_feedback.configure(text=f"Entered: {user_input}", text_color="red")
        self.entry_input.delete(0, ctk.END)
