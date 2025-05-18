import customtkinter as ctk
import matplotlib

from config import FONT_FAMILY, errors, ASL_CLASS_NAMES

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class HomeScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.app = master
        self._build_ui()

    def _build_ui(self):
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

        # Statistics button
        stats_button = ctk.CTkButton(
            self,
            text="Show Statistics",
            font=(FONT_FAMILY, 16),
            command=self.show_statistics_popup
        )
        stats_button.pack(pady=20)

    def show_statistics_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Error Statistics")
        popup.geometry("750x650")
        popup.grab_set()

        title = ctk.CTkLabel(
            popup,
            text="Error Statistics per Letter",
            font=(FONT_FAMILY, 20, "bold")
        )
        title.pack(pady=10)

        # Prepare data for plotting
        letters = ASL_CLASS_NAMES
        video_errors = [errors['letters'][ltr]['video_errors'] for ltr in letters]
        text_errors = [errors['letters'][ltr]['text_errors'] for ltr in letters]

        # Use dark background for plot
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(11, 4.5), facecolor='#222222')
        fig.patch.set_facecolor('#222222')
        ax.set_facecolor('#222222')

        x = range(len(letters))
        ax.bar(x, video_errors, width=0.4, label='Video Errors', color='#4F8DFD', align='center')
        ax.bar(x, text_errors, width=0.4, label='Text Errors', color='#FFB347', align='edge')
        ax.set_xticks(x)
        ax.set_xticklabels(letters, color='white')
        ax.set_xlabel('Letter', color='white')
        ax.set_ylabel('Errors', color='white')
        ax.set_title('Errors per Letter', color='white')
        ax.legend(facecolor='#222222', edgecolor='white', labelcolor='white')
        ax.tick_params(axis='y', colors='white')
        ax.tick_params(axis='x', colors='white')
        fig.tight_layout(pad=3.0)

        # Embed the plot in the popup with padding
        plot_frame = ctk.CTkFrame(popup, fg_color="transparent")
        plot_frame.pack(padx=20, pady=10, fill="both", expand=True)
        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=10, pady=10, fill="both", expand=True)

        # Totals
        totals = ctk.CTkLabel(
            popup,
            text=f"Total Video Errors: {errors['video_total_errors']:.2f}\n"
                 f"Total Text Errors: {errors['text_total_errors']:.2f}\n"
                 f"Video Tests: {errors['video_tests']}\n"
                 f"Text Tests: {errors['text_tests']}",
            font=(FONT_FAMILY, 14)
        )
        totals.pack(pady=10)
