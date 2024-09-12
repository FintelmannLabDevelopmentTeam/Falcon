import os
import pydicom
import time
import csv
from datetime import timedelta
from tkinter import Tk, Label, Entry, Button, filedialog, ttk, StringVar, END
from processing_logic import process_series
from prediction.model_utils import load_models, get_device
from user_interface.settings_manager import SettingsManager
from user_interface.reset_popup import show_reset_popup
from user_interface.edit_popup import show_edit_popup

DUMMY_MODE = False

class CTScanSeriesPredictionApp:
    def __init__(self, root):
        self.series_data = []
        self.all_series_data = []
        self.predicted_series = []
        self.is_paused = False
        self.prediction_in_progress = False
        self.index_mapping = {}
        self.directory = None

        self.root = root
        self.root.title("CT Scan Series Prediction")
        self.root.geometry("1100x800")  # Initial window size that fits the content

        # Load settings using SettingsManager
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.load_settings()

        Label(root, text="Select a directory containing patient folders:").grid(row=0, column=0, sticky='w', padx=(20,0), pady=(20,0))
        self.directory_var = StringVar()
        self.directory_var.set(self.settings.get("last_directory", ""))
        self.directory_entry = Entry(root, textvariable=self.directory_var, width=50)
        self.directory_entry.grid(row=0, column=1, sticky='ew', pady=(20,0))
        Button(root, text="Browse", command=self.select_directory).grid(row=0, column=2, sticky='w', padx=(20,20), pady=(20,0))

        Label(root, text="Enter minimum number of .dcm files to include a series:").grid(row=1, column=0, sticky='w', padx=(20,0))
        self.min_dcm_var = StringVar(value='20')
        self.min_dcm_entry = Entry(root, textvariable=self.min_dcm_var, width=10)
        self.min_dcm_entry.grid(row=1, column=1, sticky='w')

        s = 3
        button_frame = ttk.Frame(root)
        button_frame.grid(row=2, column=0, columnspan=3, sticky='ew', pady=10)
        Button(button_frame, text="List Series", command=self.list_series).pack(side="left", padx=(10*s,10*s))
        self.start_button = Button(button_frame, text="Start Prediction", command=self.start_prediction)
        self.start_button.pack(side="left", padx=(10*s, 0))

        self.settings_button = Button(button_frame, text="Settings", command=self.open_settings)
        self.settings_button.pack(side="left", padx=(50*s, 50*s))
        self.update_settings_button_state()

        self.reset_button = Button(button_frame, text="Reset Prediction", command=self.reset_prediction, state="disabled")
        self.reset_button.pack(side="left", padx=(0,10*s))

        Button(button_frame, text="Exit", command=self.exit_application).pack(side="left", padx=(10*s, 10*s))

        separator1 = ttk.Separator(root, orient="horizontal")
        separator1.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(20,0), padx=(20,20))

        # Create a frame for progress and table
        progress_frame = ttk.Frame(root)
        progress_frame.grid(row=4, column=0, columnspan=3, sticky='ew', pady=(5,10), padx=(20,20))
        Label(progress_frame, text="Progress:").pack(side="left")
        self.progress_var = StringVar()
        self.progress_label = Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.pack(side="left")

        separator2 = ttk.Separator(root, orient="horizontal")
        separator2.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(0,20), padx=(20,20))

        # Create table for DICOM series with a scrollbar
        Label(root, text="Unprocessed Series:").grid(row=6, column=0, sticky='w', padx=(20,0))

        # Edit button, initially disabled
        self.edit_button = Button(root, text="Edit", state="disabled", command=self.open_edit_popup)
        self.edit_button.grid(row=6, column=1, sticky='w', padx=(10, 0))

        # Scrollbar for series_table
        series_scrollbar = ttk.Scrollbar(root, orient="vertical")
        self.series_table = ttk.Treeview(root, columns=("Index", "Patient", "Study", "Series", "DCM Files", "Path", "MRN", "Series UID"), show="headings", yscrollcommand=series_scrollbar.set)
        self.series_table.grid(row=7, column=0, columnspan=3, sticky='nsew', pady=(10,30), padx=(20,0))
        series_scrollbar.grid(row=7, column=3, sticky='ns', padx=(0, 20), pady=(10,30))
        series_scrollbar.config(command=self.series_table.yview)

        col_widths = [30, 130, 130, 130, 40, 130, 130, 130]
        for idx, col in enumerate(self.series_table["columns"]):
            self.series_table.heading(col, text=col)
            self.series_table.column(col, width=col_widths[idx])

        Label(root, text="Processed Series:").grid(row=8, column=0, sticky='w', padx=(20,0))

        # Scrollbar for prediction_table
        prediction_scrollbar = ttk.Scrollbar(root, orient="vertical")
        self.prediction_table = ttk.Treeview(root, columns=("Index", "Patient", "Study", "Series", "Body Part", "BP Confidence", "Contrast", "C Confidence"), show="headings", yscrollcommand=prediction_scrollbar.set)
        self.prediction_table.grid(row=9, column=0, columnspan=3, sticky='nsew', pady=(10,20), padx=(20,0))
        prediction_scrollbar.grid(row=9, column=3, sticky='ns', padx=(0, 20), pady=(10,20))
        prediction_scrollbar.config(command=self.prediction_table.yview)

        col_widths = [30, 130, 130, 130, 100, 100, 100, 100]
        for idx, col in enumerate(self.prediction_table["columns"]):
            self.prediction_table.heading(col, text=col)
            self.prediction_table.column(col, width=col_widths[idx])

        # Configure resizing behavior for rows and columns
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(7, weight=1)  # Unprocessed series table expands vertically
        self.root.grid_rowconfigure(9, weight=1)  # Processed series table expands vertically

    def update_settings_button_state(self):
        """Enable or disable the settings button depending on whether a prediction is in progress."""
        if self.prediction_in_progress or self.is_paused:
            self.settings_button.config(state="disabled")
        else:
            self.settings_button.config(state="normal")

    def open_settings(self):
        """Opens the settings window."""
        if not self.prediction_in_progress:
            prev_txt = self.progress_var.get()
            self.progress_var.set("Please answer the pop-up window.")
            self.settings_manager.open_settings_window(self.root)
            self.settings = self.settings_manager.load_settings()
            self.progress_var.set(prev_txt)

    def start_prediction(self):
        """Starts or resumes the prediction process for each series."""
        if self.prediction_in_progress:
            self.start_button.config(text="Resume Prediction")
            self.prediction_in_progress = False
            self.is_paused = True
            self.reset_button.config(state="normal")
        elif self.is_paused:
            self.is_paused = False
            self.start_prediction()
        else:
            self.prediction_in_progress = True
            self.update_settings_button_state()
            self.reset_button.config(state="disabled")
            self.start_button.config(text="Pause Prediction")
            self.device = get_device()
            start_time = time.time()
            to_do = [s for s in self.series_data if s[-1]]  # Only process selected series
            num_pred = len(to_do)
            models = None
            if len(to_do) > 0 and not DUMMY_MODE:
                self.progress_var.set(f"Initializing Prediction...")
                models = load_models(self.device)
            for i, series in enumerate(to_do):
                self.root.update()
                if self.is_paused:
                    return
                body_part, bp_conf, contrast, c_conf = process_series(models, series, self.directory,
                                                     device=self.device, save_nrrds=self.settings.get("store_nrrd_files", False))
                elapsed_time = time.time() - start_time
                seconds = round((elapsed_time / (i + 1)) * (num_pred - (i + 1)))
                eta = timedelta(seconds=seconds)
                self.progress_var.set(f"{((i + 1) / num_pred * 100):.2f}%       ETA: {str(eta)}")
                self.series_data.remove(series)
                series_entry = series[:4] + [body_part] + [bp_conf] + [contrast] + [c_conf]
                self.predicted_series.append(series_entry)
                self.update_tables()
                self.save_predictions_to_csv()
            del models
            self.start_button.config(text="Start Prediction")
            self.prediction_in_progress = False
            self.update_settings_button_state()
            self.reset_button.config(state="normal")

    def exit_application(self):
        """Exits the application."""
        self.root.quit()
        self.root.destroy()

    def select_directory(self):
        """Opens a file dialog to select a directory and brings focus back to the main window."""
        selected_directory = filedialog.askdirectory()
        if selected_directory:
            self.directory_var.set(selected_directory)
            self.directory = selected_directory
            self.settings["last_directory"] = selected_directory
            self.settings_manager.save_settings(self.settings)
        self.root.focus_force()

    def list_series_in_directory(self, directory, min_dcm_files):
        """Lists all series in the directory with at least the minimum number of DICOM files."""
        series_data = []
        index = 1
        for root, dirs, files in os.walk(directory):
            dcm_files = [f for f in files if f.endswith('.dcm')]
            if len(dcm_files) >= min_dcm_files:
                series_info = self.get_series_info(root, dcm_files, index)
                series_data.append(series_info + [True])  # All series selected initially
                index += 1
        return series_data

    def get_series_info(self, root, dcm_files, index):
        """Extracts information from a DICOM series."""
        path_parts = root.split(os.sep)
        patient_name = path_parts[-3]
        study = path_parts[-2]
        series = path_parts[-1]

        try:
            sample_dcm_path = os.path.join(root, dcm_files[0])
            dcm = pydicom.dcmread(sample_dcm_path)
            mrn = dcm.PatientID
            series_uid = dcm.SeriesInstanceUID
        except Exception as e:
            print(f"Error reading DICOM file: {e}")
            mrn = 'notfound'
            series_uid = 'notfound'

        return [index, patient_name, study, series, len(dcm_files), root, mrn, series_uid]

    def save_series_list_to_csv(self):
        """Saves the list of series with their selection status to a CSV file."""
        csv_file = os.path.join(self.directory, "list_of_series.csv")
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Index", "Patient", "Study", "Series", "DCM Files", "Path", "MRN", "Series UID", "Selected"])
            for row in self.all_series_data:
                writer.writerow(row)

    def save_predictions_to_csv(self):
        """Saves the prediction results to a CSV file."""
        csv_file = os.path.join(self.directory, "predictions.csv")
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Index", "Patient", "Study", "Series", "Body Part", "Contrast"])
            writer.writerows(self.predicted_series)

    def load_data_from_csv(self, mode):
        """Loads data from a CSV file, including selection status."""
        mode_dict = {'series': "list_of_series.csv", 'predictions': "predictions.csv"}
        csv_file = os.path.join(self.directory, mode_dict[mode])
        series = []
        with open(csv_file, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                if mode == 'series':
                    series.append(row[:-1] + [row[-1] == "True"])  # Convert 'selected' to boolean
                else:
                    series.append(row)
        return series

    def update_tables(self):
        """Update the tables with the latest data."""
        # Clear the series_table
        for item in self.series_table.get_children():
            self.series_table.delete(item)

        # Insert new rows for the series_data (only selected series)
        for row in self.series_data:
            if row[-1]:  # Only show selected series
                self.series_table.insert("", END, values=row[:-1])

        # Clear the prediction_table
        for item in self.prediction_table.get_children():
            self.prediction_table.delete(item)

        # Insert new rows for the predicted_series
        for row in self.predicted_series:
            self.prediction_table.insert("", 0, values=row)

    def list_series(self):
        """List series in the selected directory."""
        self.directory = self.directory_var.get()
        if self.directory == '':
            self.progress_var.set(f"Please specify a directory to load the series from.")
            return
        min_dcm_files = int(self.min_dcm_var.get()) if self.min_dcm_var.get().isdigit() else 1
        if min_dcm_files < 1:
            min_dcm_files = 1

        list_csv = os.path.join(self.directory, "list_of_series.csv")
        prediction_csv = os.path.join(os.path.join(self.directory, "predictions.csv"))

        if os.path.exists(list_csv):
            self.progress_var.set(f"Loaded state of previous prediction.")
            self.series_data = self.load_data_from_csv(mode='series')
            self.all_series_data = self.series_data.copy()
            self.start_button.config(text="Start Prediction")
            if os.path.exists(prediction_csv):
                self.predicted_series = self.load_data_from_csv(mode='predictions')
                self.is_paused = True
                self.start_button.config(text="Continue Prediction")
                self.update_settings_button_state()
                predicted_series_identifiers = [
                    (entry[1], entry[2], entry[3]) for entry in self.predicted_series
                ]
                self.series_data = [
                    s for s in self.series_data if (s[1], s[2], s[3]) not in predicted_series_identifiers
                ]
            self.update_tables()
        else:
            self.progress_var.set(f"Loading all DICOM series in directory...")
            self.series_data = self.list_series_in_directory(self.directory, min_dcm_files)
            self.all_series_data = self.series_data.copy()
            if len(self.series_data) == 0:
                self.progress_var.set(f"No series found in directory. Please adjust parameters or change directory.")
                return
            self.save_series_list_to_csv()
            self.update_tables()
            self.progress_var.set(f"DICOM series loaded. Ready for prediction.")
        self.reset_button.config(state="normal")
        self.edit_button.config(state="normal")  # Enable Edit button

    def reset_prediction(self):
        """Shows a confirmation popup before resetting progress."""
        if self.directory:
            def perform_reset(reset=True, prev_txt=''):
                if reset:
                    series_csv = os.path.join(self.directory, "list_of_series.csv")
                    prediction_csv = os.path.join(self.directory, "predictions.csv")
                    if os.path.exists(series_csv):
                        os.remove(series_csv)
                    if os.path.exists(prediction_csv):
                        os.remove(prediction_csv)

                    preprocessed_dir = os.path.join(os.path.join(self.directory, "preprocessed"))
                    if os.path.exists(preprocessed_dir):
                        for root, dirs, files in os.walk(preprocessed_dir):
                            for file in files:
                                os.remove(os.path.join(root, file))
                        os.rmdir(preprocessed_dir)

                    self.series_data = []
                    self.all_series_data = []
                    self.predicted_series = []
                    self.update_tables()
                    self.is_paused = False
                    self.prediction_in_progress = False
                    self.update_settings_button_state()
                    self.reset_button.config(state="disabled")
                    self.edit_button.config(state="disabled")
                    self.start_button.config(text="Start Prediction")

                    self.progress_var.set(f"Prediction progress reset. List Series to restart.")
                else:
                    self.progress_var.set(prev_txt)

            prev_txt = self.progress_var.get()
            self.progress_var.set("Please answer the pop-up window.")
            show_reset_popup(self.root, perform_reset, prev_txt=prev_txt)

    def open_edit_popup(self):
        """Opens the pop-up for editing series selection."""
        if self.all_series_data:
            show_edit_popup(self.root, self.all_series_data, self.save_series_selection)

    def save_series_selection(self, updated_all_series_data):
        """Updates the series list with the user-selected series."""
        self.all_series_data = updated_all_series_data  # Update with user selection
        self.save_series_list_to_csv()  # Save updated selection to CSV
        self.update_series_list()
        self.update_tables()  # Refresh the table with the new selection
    
    def update_series_list(self):
        predicted_series_identifiers = [
            (entry[1], entry[2], entry[3]) for entry in self.predicted_series
        ]
        self.series_data = [
            s for s in self.all_series_data if s[-1] and (s[1], s[2], s[3]) not in predicted_series_identifiers
        ]

if __name__ == "__main__":
    root = Tk()
    app = CTScanSeriesPredictionApp(root)
    root.mainloop()
