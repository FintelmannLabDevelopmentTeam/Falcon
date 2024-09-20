import json
from tkinter import Toplevel, Label, Checkbutton, BooleanVar, Button, Entry, StringVar
from tkinter import ttk

SETTINGS_FILE = "settings.json"

class SettingsManager:
    def __init__(self):
        """Initializes the SettingsManager and loads settings from file."""
        self.settings = {
            "store_nrrd_files": False,       # Default setting
            "verbose": False,               # Dummy checkbox setting
            "dummy_setting_2": False,        # Dummy checkbox setting
            "dummy_text_field_1": "",        # Dummy text field setting
            "dummy_text_field_2": "",         # Another dummy text field setting
            "last_directory": "",
            "series_table_columns": {
                'Index': True,
                'Patient ID': True,
                'Study Instance UID': True,
                'Series Instance UID': True,
                'Study Description': False,
                'Series Description': True,
                'Patient Folder': False,
                'Study Folder': False,
                'Series Folder': False,
                'Number of Slices': True,
                'Series Directory': True,
                "Body Part Label": True,
                "Body Part (BP)": False,
                "BP Confidence": False,
                "IV Contrast (IVC)": False,
                "IVC Confidence": False,
                "Selected": False
            },
            "predicted_table_columns": {
                'Index': True,
                'Patient ID': True,
                'Study Instance UID': True,
                'Series Instance UID': True,
                'Study Description': False,
                'Series Description': False,
                'Patient Folder': False,
                'Study Folder': False,
                'Series Folder': False,
                'Number of Slices': False,
                'Series Directory': False,
                "Body Part Label": False,
                "Body Part (BP)": True,
                "BP Confidence": True,
                "IV Contrast (IVC)": True,
                "IVC Confidence": True,
                "Selected": False
            }
        }
        self.load_settings()

    def load_settings(self):
        """Loads settings from a JSON file, or creates default settings if the file doesn't exist."""
        try:
            with open(SETTINGS_FILE, 'r') as f:
                self.settings = json.load(f)
        except FileNotFoundError:
            # If the settings file doesn't exist, create it with default values
            self.save_settings(self.settings)
        return self.settings

    def save_settings(self, settings):
        """Saves the current settings to a JSON file."""
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f)

    def open_settings_window(self, root):
        """Opens the settings window where users can modify the settings."""
        settings_window = Toplevel(root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.resizable(False, False)

        # Keep popup above the main window
        settings_window.transient(root)          # Set the popup as a child of the main window
        settings_window.attributes("-topmost", True)  # Keep it on top
        settings_window.focus_set()   

        # Frame for better layout
        frame = ttk.Frame(settings_window, padding="10")
        frame.grid(row=0, column=0, sticky='nsew')

        # Checkbox for storing NRRD files
        store_nrrd_var = BooleanVar(value=self.settings.get("store_nrrd_files", False))
        Label(frame, text="Store preprocessed NRRD files:").grid(row=0, column=0, sticky="w", pady=5)
        store_nrrd_checkbox = Checkbutton(frame, variable=store_nrrd_var)
        store_nrrd_checkbox.grid(row=0, column=1, sticky="w")

        # Dummy checkbox settings
        verbose_var = BooleanVar(value=self.settings.get("verbose", False))
        Label(frame, text="Print detailed processing steps:").grid(row=1, column=0, sticky="w", pady=5)
        verbose_checkbox = Checkbutton(frame, variable=verbose_var)
        verbose_checkbox.grid(row=1, column=1, sticky="w")

        dummy_setting_2_var = BooleanVar(value=self.settings.get("dummy_setting_2", False))
        Label(frame, text="Dummy Setting 2:").grid(row=2, column=0, sticky="w", pady=5)
        dummy_setting_2_checkbox = Checkbutton(frame, variable=dummy_setting_2_var)
        dummy_setting_2_checkbox.grid(row=2, column=1, sticky="w")

        # Dummy text field settings
        dummy_text_field_1_var = StringVar(value=self.settings.get("dummy_text_field_1", ""))
        Label(frame, text="Dummy Text Field 1:").grid(row=3, column=0, sticky="w", pady=5)
        dummy_text_field_1_entry = Entry(frame, textvariable=dummy_text_field_1_var, width=30)
        dummy_text_field_1_entry.grid(row=3, column=1, sticky="w")

        dummy_text_field_2_var = StringVar(value=self.settings.get("dummy_text_field_2", ""))
        Label(frame, text="Dummy Text Field 2:").grid(row=4, column=0, sticky="w", pady=5)
        dummy_text_field_2_entry = Entry(frame, textvariable=dummy_text_field_2_var, width=30)
        dummy_text_field_2_entry.grid(row=4, column=1, sticky="w")

        def save_and_close():
            """Save the settings and close the window."""
            self.settings["store_nrrd_files"] = store_nrrd_var.get()
            self.settings["verbose"] = verbose_var.get()
            self.settings["dummy_setting_2"] = dummy_setting_2_var.get()
            self.settings["dummy_text_field_1"] = dummy_text_field_1_var.get()
            self.settings["dummy_text_field_2"] = dummy_text_field_2_var.get()
            self.save_settings(self.settings)
            settings_window.destroy()

        # Save button
        Button(frame, text="Save", command=save_and_close).grid(row=5, column=0, columnspan=2, pady=10)
        settings_window.grab_set()
        settings_window.wait_window()

