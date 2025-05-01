"""
Home screen module for the ASL Quiz application
"""
import customtkinter as ctk
from config import FONT_FAMILY


class HomeScreen(ctk.CTkFrame):
    """Home screen with difficulty selection"""

    def __init__(self, master):
        """
        Initialize the home screen

        Args:
            master: Parent widget (ASLQuizApp)
        """
        super().__init__(master)
        self.app = master
        self._build_ui()

    def _build_ui(self):
        """Build the UI elements"""
        # Title
        title_label = ctk.CTkLabel(
            self,
            text="Welcome to ASL Quiz Game!",
            font=(FONT_FAMILY, 28, "bold")
        )
        title_label.pack(pady=50)

        # Instructions
        instruction_label = ctk.CTkLabel(
            self,
            text="Choose a difficulty level to start learning ASL!",
            font=(FONT_FAMILY, 18)
        )
        instruction_label.pack(pady=20)

        # Easy mode button
        easy_button = ctk.CTkButton(
            self,
            text="Easy Mode",
            font=(FONT_FAMILY, 16),
            command=lambda: self.app.start_quiz("easy")
        )
        easy_button.pack(pady=10)

        # Hard mode button
        hard_button = ctk.CTkButton(
            self,
            text="Hard Mode",
            font=(FONT_FAMILY, 16),
            command=lambda: self.app.start_quiz("hard")
        )
        hard_button.pack(pady=10)