import customtkinter as ctk
from datetime import date
from tkinter import messagebox
import json
import os

# ==========================================
# 1. NEW DUAL-MODE COLOR PALETTE (Tuple format: ("Light Mode Color", "Dark Mode Color"))
# ==========================================
COLOR_BG = ("#f0f4f8", "#1a1c2a")  # Main background
COLOR_FRAME = ("#ffffff", "#262a3f")  # Inner frames and text boxes
COLOR_BORDER = ("#d1d5db", "#30354c")  # Borders
COLOR_TEXT = ("#1f2937", "#ffffff")  # Main titles and text
COLOR_MUTED = ("#6b7280", "#a0a0a0")  # Secondary/gray text
COLOR_PRIMARY = ("#4f46e5", "#3a406f")  # Main buttons
COLOR_HOVER = ("#6366f1", "#535c9d")  # Main buttons hover state
COLOR_ACCENT_1 = ("#0d9488", "#40a798")  # Turquoise accent (+)
COLOR_ACCENT_2 = ("#e11d48", "#b83b5e")  # Rose red accent (-)
COLOR_SAVE = ("#16a34a", "#18b87e")  # Save button

# General font settings
FONT_TITLE = ("Arial", 32, "bold")
FONT_HEADER = ("Arial", 22, "bold")
FONT_NORMAL = ("Arial", 14)


# ==========================================
# 2. OOP DATA MODELS
# ==========================================
class DailyRecord:
    """Base Class for daily tracking"""

    def __init__(self, record_date):
        self.record_date = record_date

    def get_summary(self):
        return f"Date: {self.record_date}"


class HealthRecord(DailyRecord):
    """Subclass - Inherits from DailyRecord"""

    def __init__(self, record_date, mood, water_intake, pain_level):
        super().__init__(record_date)
        self.mood = mood
        self.water_intake = water_intake
        self.pain_level = pain_level

    @property
    def pain_level(self):
        return self.__pain_level

    @pain_level.setter
    def pain_level(self, level):
        if 1 <= level <= 5:
            self.__pain_level = level
        else:
            raise ValueError("Pain level must be between 1 and 5!")

    def get_summary(self):
        base_summary = super().get_summary()
        return f"{base_summary} | Mood: {self.mood} | Water: {self.water_intake}ml | Pain: {self.pain_level}/5"

    def to_dict(self):
        """Converts this object to a dictionary so it can be saved to a JSON file"""
        return {
            "record_date": self.record_date,
            "mood": self.mood,
            "water_intake": self.water_intake,
            "pain_level": self.pain_level
        }


# ==========================================
# 3. GUI SCREENS
# ==========================================

class MainMenuScreen(ctk.CTkFrame):
    """Main Menu Screen with Theme Toggle"""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG, border_width=2, border_color=COLOR_BORDER)
        self.controller = controller

        # Title
        label = ctk.CTkLabel(self, text="Health & Period Tracker",
                             font=FONT_TITLE, text_color=COLOR_TEXT)
        label.pack(pady=(70, 40))

        # Navigation Buttons
        add_btn = ctk.CTkButton(self, text="Add New Record", width=260, height=50,
                                font=FONT_NORMAL, fg_color=COLOR_PRIMARY, hover_color=COLOR_HOVER,
                                command=lambda: controller.show_frame("AddRecordScreen"))
        add_btn.pack(pady=15)

        history_btn = ctk.CTkButton(self, text="View History", width=260, height=50,
                                    font=FONT_NORMAL, fg_color=COLOR_PRIMARY, hover_color=COLOR_HOVER,
                                    command=lambda: controller.show_frame("HistoryScreen"))
        history_btn.pack(pady=15)

        # Theme Toggle Switch (Dark / Light Mode)
        self.theme_switch = ctk.CTkSwitch(self, text="Dark Mode", font=FONT_NORMAL, text_color=COLOR_TEXT,
                                          command=self.toggle_theme)
        self.theme_switch.select()  # Default is dark mode (ON)
        self.theme_switch.pack(side="bottom", pady=30)

    def toggle_theme(self):
        """Switches between dark and light mode dynamically"""
        if self.theme_switch.get() == 1:
            ctk.set_appearance_mode("dark")
            self.theme_switch.configure(text="Dark Mode")
        else:
            ctk.set_appearance_mode("light")
            self.theme_switch.configure(text="Light Mode")


class AddRecordScreen(ctk.CTkFrame):
    """Add New Record Screen"""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG, border_width=2, border_color=COLOR_BORDER)
        self.controller = controller
        self.water_intake = 0

        # Back button
        back_btn = ctk.CTkButton(self, text="← Back to Menu", font=("Arial", 12),
                                 fg_color=COLOR_BORDER, text_color=COLOR_TEXT, hover_color=COLOR_MUTED,
                                 width=140, height=35,
                                 command=lambda: controller.show_frame("MainMenuScreen"))
        back_btn.pack(anchor="nw", padx=15, pady=15)

        title = ctk.CTkLabel(self, text="Daily Health Record", font=FONT_HEADER, text_color=COLOR_TEXT)
        title.pack(pady=15)

        # Mood Selection
        mood_label = ctk.CTkLabel(self, text="Today's Mood:", font=FONT_NORMAL, text_color=COLOR_MUTED)
        mood_label.pack(pady=(20, 5))
        self.mood_var = ctk.StringVar(value="Happy 😊")
        mood_selector = ctk.CTkOptionMenu(self, values=["Happy 😊", "Tired 🥱", "Stressed 😠", "In Pain 😖"],
                                          variable=self.mood_var, font=FONT_NORMAL,
                                          fg_color=COLOR_PRIMARY, button_color=COLOR_PRIMARY,
                                          dropdown_fg_color=COLOR_FRAME, dropdown_hover_color=COLOR_HOVER)
        mood_selector.pack(pady=5)

        # Water Intake
        self.water_label = ctk.CTkLabel(self, text="Water: 0 ml", font=FONT_NORMAL, text_color=COLOR_MUTED)
        self.water_label.pack(pady=(30, 5))

        water_frame = ctk.CTkFrame(self, fg_color="transparent")
        water_frame.pack(pady=10)

        self.decrease_water_btn = ctk.CTkButton(water_frame, text="-250ml", width=80, height=40,
                                                font=("Arial", 12, "bold"),
                                                fg_color=COLOR_ACCENT_2, hover_color=COLOR_HOVER,
                                                command=self.decrease_water)
        self.decrease_water_btn.pack(side="left", padx=10)

        self.increase_water_btn = ctk.CTkButton(water_frame, text="+250ml", width=80, height=40,
                                                font=("Arial", 12, "bold"),
                                                fg_color=COLOR_ACCENT_1, hover_color=COLOR_HOVER,
                                                command=self.increase_water)
        self.increase_water_btn.pack(side="left", padx=10)

        # Pain Level
        self.pain_label = ctk.CTkLabel(self, text="Pain Level: 1 / 5", font=FONT_NORMAL, text_color=COLOR_MUTED)
        self.pain_label.pack(pady=(30, 5))

        self.pain_slider = ctk.CTkSlider(self, from_=1, to=5, number_of_steps=4,
                                         width=350, height=20,
                                         progress_color=COLOR_ACCENT_1, button_color=COLOR_ACCENT_2,
                                         button_hover_color=COLOR_HOVER,
                                         command=self.update_pain)
        self.pain_slider.set(1)
        self.pain_slider.pack(pady=10)

        # Save Button
        save_btn = ctk.CTkButton(self, text="Save Today's Record", width=280, height=60, font=("Arial", 18, "bold"),
                                 fg_color=COLOR_SAVE, hover_color=COLOR_HOVER, text_color="#ffffff",
                                 command=self.save_data)
        save_btn.pack(pady=50)

    def increase_water(self):
        self.water_intake += 250
        self.water_label.configure(text=f"Water: {self.water_intake} ml")

    def decrease_water(self):
        if self.water_intake >= 250:
            self.water_intake -= 250
            self.water_label.configure(text=f"Water: {self.water_intake} ml")

    def update_pain(self, value):
        self.pain_label.configure(text=f"Pain Level: {int(value)} / 5")

    def save_data(self):
        try:
            today = date.today().strftime("%d/%m/%Y")
            new_record = HealthRecord(today, self.mood_var.get(), self.water_intake, int(self.pain_slider.get()))

            self.controller.records.append(new_record)
            self.controller.save_data_to_file()

            messagebox.showinfo("Success", "Daily record saved to file!")
            self.controller.show_frame("MainMenuScreen")

        except ValueError as error:
            messagebox.showerror("Error", str(error))


class HistoryScreen(ctk.CTkFrame):
    """View History Screen"""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLOR_BG, border_width=2, border_color=COLOR_BORDER)
        self.controller = controller

        # Back button
        back_btn = ctk.CTkButton(self, text="← Back to Menu", font=("Arial", 12),
                                 fg_color=COLOR_BORDER, text_color=COLOR_TEXT, hover_color=COLOR_MUTED,
                                 width=140, height=35,
                                 command=lambda: controller.show_frame("MainMenuScreen"))
        back_btn.pack(anchor="nw", padx=15, pady=15)

        title = ctk.CTkLabel(self, text="Your History", font=FONT_HEADER, text_color=COLOR_TEXT)
        title.pack(pady=15)

        # Textbox
        self.history_textbox = ctk.CTkTextbox(self, width=450, height=450, font=("Courier New", 12),
                                              fg_color=COLOR_FRAME, text_color=COLOR_TEXT,
                                              border_width=1, border_color=COLOR_BORDER)
        self.history_textbox.pack(pady=15, padx=20)
        self.history_textbox.configure(state="disabled")

    def update_history(self):
        self.history_textbox.configure(state="normal")
        self.history_textbox.delete("1.0", "end")

        if not self.controller.records:
            self.history_textbox.insert("end", "No records found yet.\nStart by adding your first daily entry!")
        else:
            for i, record in enumerate(self.controller.records, 1):
                self.history_textbox.insert("end", f"[{i}] {record.get_summary()}\n")

        self.history_textbox.configure(state="disabled")


# ==========================================
# 4. MAIN APP CONTROLLER
# ==========================================

class PeriodTrackerApp(ctk.CTk):
    """Main Application Controller"""

    def __init__(self):
        super().__init__()
        self.title("Period and Health Tracker")
        self.geometry("520x680")

        # Set default startup mode to Dark
        ctk.set_appearance_mode("dark")

        self.records = []
        self.file_name = "health_data.json"

        self.load_data_from_file()

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (MainMenuScreen, AddRecordScreen, HistoryScreen):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainMenuScreen")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        if page_name == "HistoryScreen":
            frame.update_history()
        frame.tkraise()

        # --- FILE OPERATIONS ---

    def save_data_to_file(self):
        data_to_save = [record.to_dict() for record in self.records]
        with open(self.file_name, "w", encoding="utf-8") as file:
            json.dump(data_to_save, file, indent=4, ensure_ascii=False)

    def load_data_from_file(self):
        if os.path.exists(self.file_name):
            with open(self.file_name, "r", encoding="utf-8") as file:
                loaded_data = json.load(file)
                for item in loaded_data:
                    record = HealthRecord(
                        record_date=item["record_date"],
                        mood=item["mood"],
                        water_intake=item["water_intake"],
                        pain_level=item["pain_level"]
                    )
                    self.records.append(record)


if __name__ == "__main__":
    app = PeriodTrackerApp()
    app.mainloop()
