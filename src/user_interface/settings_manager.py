import json
from tkinter import Toplevel, Label, Checkbutton, BooleanVar, Button
from tkinter import ttk
from src.user_interface.ui_utils import get_info_icon, ToolTip


SETTINGS_FILE = "settings.json"

class SettingsManager:
    def __init__(self):
        """Initializes the SettingsManager and loads settings from file."""
        self.settings = {
            "store_nrrd_files": False,       # Default setting
            "verbose": False,               # Dummy checkbox setting
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
        #settings_window.geometry("")
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
        Label(frame, text="Store preprocessed NRRD files:", font=("", 14, "bold")).grid(row=0, column=0, sticky="w", pady=10)
        store_nrrd_checkbox = Checkbutton(frame, variable=store_nrrd_var)
        store_nrrd_checkbox.grid(row=0, column=1, sticky="w")

        # Checkbox for detailed output
        verbose_var = BooleanVar(value=self.settings.get("verbose", False))
        Label(frame, text="Detailed terminal output:", font=("", 14, "bold")).grid(row=1, column=0, sticky="w", pady=10)
        verbose_checkbox = Checkbutton(frame, variable=verbose_var)
        verbose_checkbox.grid(row=1, column=1, sticky="w")

        # Table settings labels
        label_frame = ttk.Frame(frame)
        label_frame.grid(row=2, column=0, sticky="w", pady=(10,0))
        Label(label_frame, text="Edit visible table columns:", font=("", 14, "bold")).pack(side="left")
        
        #Information
        icon_image = get_info_icon((16,16))
        info_label = Label(label_frame, image=icon_image)
        info_label.pack(side="left", padx=(10,0))
        ToolTip(info_label, 
                "This choice only affects the visibility in the tables, in the output CSV all columns will be stored.")



        Label(frame, text="Unprocessed", font=("", 14, "bold"), width=10).grid(row=3, column=1, sticky="w",pady=(10,0))
        Label(frame, text="Processed", font=("", 14, "bold"), width=10).grid(row=3, column=2, sticky="w",pady=(10,0))

        # Dictionary to hold the BooleanVars for checkboxes
        series_checkboxes = {}
        predicted_checkboxes = {}

        no_edit_keys = ['Index', 'Body Part Label', 'Selected']
        predict_only_keys = ["Body Part (BP)", "BP Confidence", "IV Contrast (IVC)" ,"IVC Confidence"]
        editable_keys = [key for key in self.settings['series_table_columns'].keys() if key not in no_edit_keys]
        # Create checkboxes for both series and predicted table columns
        for i, key in enumerate(editable_keys):
            # Display the column label
            Label(frame, text=key).grid(row=i+4, column=0, sticky="w", padx=(40,0))

            # Predicted Table checkbox
            predicted_check_var = BooleanVar(value=self.settings['predicted_table_columns'][key])
            predicted_checkboxes[key] = predicted_check_var
            predicted_checkbox = Checkbutton(frame, variable=predicted_check_var)
            predicted_checkbox.grid(row=i+4, column=2)

            # Series Table checkbox
            if key in predict_only_keys: continue #This setting is only meaningful for predicted table
            series_check_var = BooleanVar(value=self.settings['series_table_columns'][key])
            series_checkboxes[key] = series_check_var
            series_checkbox = Checkbutton(frame, variable=series_check_var)
            series_checkbox.grid(row=i+4, column=1)



        def save_and_close():
            """Save the settings and close the window."""
            # Update the settings with the current checkbox values
            self.settings["store_nrrd_files"] = store_nrrd_var.get()
            self.settings["verbose"] = verbose_var.get()

            # Update series_table_columns and predicted_table_columns from the checkboxes
            for key in series_checkboxes:
                self.settings["series_table_columns"][key] = series_checkboxes[key].get()
            for key in predicted_checkboxes:
                self.settings["predicted_table_columns"][key] = predicted_checkboxes[key].get()

            # Save the updated settings
            self.save_settings(self.settings)
            settings_window.destroy()

        # Save button
        Button(frame, text="Save", command=save_and_close).grid(row=len(self.settings['series_table_columns'])+3, column=0, columnspan=3, pady=(30,20))
        settings_window.update_idletasks()
        settings_window.geometry("")
        settings_window.grab_set()
        settings_window.wait_window()


