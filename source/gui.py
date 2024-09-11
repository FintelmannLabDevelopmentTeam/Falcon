import os
import pydicom
import time
import csv
import random
from datetime import timedelta
from tkinter import Tk, Label, Entry, Button, filedialog, ttk, StringVar, END, Toplevel
from processing_logic import process_series
from prediction.model_utils import load_models, get_device
from user_interface.settings_manager import SettingsManager
from user_interface.reset_popup import show_reset_popup

DUMMY_MODE = True

class CTScanSeriesPredictionApp:
    def __init__(self, root):
        self.series_data = []
        self.predicted_series = []
        self.is_paused = False
        self.prediction_in_progress = False
        self.index_mapping = {}
        self.directory = None

        self.root = root
        self.root.title("CT Scan Series Prediction")
        self.root.geometry("1000x800")

        # Load settings using SettingsManager
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.load_settings()

        Label(root, text="Select a directory containing patient folders:").grid(row=0, column=0, sticky='w')
        self.directory_var = StringVar()
        self.directory_var.set(self.settings.get("last_directory", ""))
        self.directory_entry = Entry(root, textvariable=self.directory_var, width=50)
        self.directory_entry.grid(row=0, column=1)
        Button(root, text="Browse", command=self.select_directory).grid(row=0, column=2)

        Label(root, text="Enter minimum number of .dcm files to include a series:").grid(row=1, column=0, sticky='w')
        self.min_dcm_var = StringVar(value='20')
        self.min_dcm_entry = Entry(root, textvariable=self.min_dcm_var, width=10)
        self.min_dcm_entry.grid(row=1, column=1, sticky='w')

        s = 2.5
        button_frame = ttk.Frame(root)
        button_frame.grid(row=2, column=0, columnspan=5, pady=10)
        Button(button_frame, text="List Series", command=self.list_series).pack(side="left", padx=(0,10*s))
        self.start_button = Button(button_frame, text="Start Prediction", command=self.start_prediction)
        self.start_button.pack(side="left", padx=(0,50*s))
        
        
        # Add Settings button, enabled only when prediction is not in progress
        self.settings_button = Button(button_frame, text="Settings", command=self.open_settings)
        self.settings_button.pack(side="left", padx=(0,50*s))
        self.update_settings_button_state()

        self.reset_button = Button(button_frame, text="Reset Prediction", command=self.reset_prediction, state="disabled")
        self.reset_button.pack(side="left", padx=(0,10*s))

        Button(button_frame, text="Exit", command=self.exit_application).pack(side="left", padx=(0,10))

        # Create a frame for progress and table
        progress_frame = ttk.Frame(root)
        progress_frame.grid(row=3, column=0, columnspan=3, sticky='w', pady=10)
        Label(progress_frame, text="Progress:").pack(side="left")
        self.progress_var = StringVar()
        self.progress_label = Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.pack(side="left")

        self.series_table = ttk.Treeview(root, columns=("Index", "Patient", "Study", "Series", "DCM Files", "Path", "MRN", "Series UID"), show="headings")
        self.series_table.grid(row=4, column=0, columnspan=4, sticky='nsew', pady=10)
        for col in self.series_table["columns"]:
            self.series_table.heading(col, text=col)
            self.series_table.column(col, width=100)

        Label(root, text="Prediction:").grid(row=5, column=0, sticky='w')
        self.prediction_table = ttk.Treeview(root, columns=("Index", "Patient", "Study", "Series", "Body Part", "Contrast"), show="headings")
        self.prediction_table.grid(row=6, column=0, columnspan=4, sticky='nsew')
        for col in self.prediction_table["columns"]:
            self.prediction_table.heading(col, text=col)
            self.prediction_table.column(col, width=120)

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
            # Update the settings variable after the settings window is closed
            self.settings = self.settings_manager.load_settings()
            self.progress_var.set(prev_txt)

    def start_prediction(self):
        """Starts or resumes the prediction process for each series."""
        # Disable settings button when prediction starts
        if self.prediction_in_progress:  # Pause button pressed
            self.start_button.config(text="Resume Prediction")
            self.prediction_in_progress = False
            self.is_paused = True
            self.reset_button.config(state="normal")
        elif self.is_paused:  # Resume button pressed
            self.is_paused = False
            self.start_prediction()
        else:
            self.prediction_in_progress = True
            self.update_settings_button_state()
            self.reset_button.config(state="disabled")
            self.start_button.config(text="Pause Prediction")
            self.device = get_device()
            start_time = time.time()
            to_do = self.series_data.copy()
            num_pred = len(to_do)
            models = None
            if len(to_do) > 0 and not DUMMY_MODE:
                self.progress_var.set(f"Initializing Prediction...")
                models = load_models(self.device)
            for i, series in enumerate(to_do):
                self.root.update()
                if self.is_paused:
                    return
                body_part, contrast = process_series(models, series, self.directory, 
                                                     device=self.device, save_nrrds=self.settings.get("store_nrrd_files", False))
                elapsed_time = time.time() - start_time
                seconds = round((elapsed_time / (i + 1)) * (num_pred - (i + 1)))
                eta = timedelta(seconds=seconds)
                self.progress_var.set(f"{((i + 1) / num_pred * 100):.2f}%       ETA: {str(eta)})")
                self.series_data.remove(series)
                series_entry = series[:4] + [body_part] + [contrast]
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
        if selected_directory:  # If a directory is selected, update the directory variable and settings
            self.directory_var.set(selected_directory)
            self.directory = selected_directory
            
            # Update settings with the new directory and save it
            self.settings["last_directory"] = selected_directory
            self.settings_manager.save_settings(self.settings)

        # Bring the main window back into focus
        self.root.focus_force()


    def list_series_in_directory(self, directory, min_dcm_files):
        """Lists all series in the directory with at least the minimum number of DICOM files."""
        series_data = []
        dirs_processed = 0
        index = 1

        for root, dirs, files in os.walk(directory):
            dcm_files = [f for f in files if f.endswith('.dcm')]
            if len(dcm_files) >= min_dcm_files:
                series_info = self.get_series_info(root, dcm_files, index)
                series_data.append(series_info)
                index += 1

            dirs_processed += 1
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
        """Saves the list of series to a CSV file."""
        csv_file = os.path.join(self.directory, "list_of_series.csv")
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Index", "Patient", "Study", "Series", "DCM Files", "Path", "MRN", "Series UID"])
            writer.writerows(self.series_data)

    def save_predictions_to_csv(self):
        """Saves the prediction results to a CSV file."""
        csv_file = os.path.join(self.directory, "predictions.csv")
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Index", "Patient", "Study", "Series", "Body Part", "Contrast"])
            writer.writerows(self.predicted_series)

    def load_data_from_csv(self, mode):
        """Loads data from a CSV file."""
        mode_dict = {'series':"list_of_series.csv", 'predictions':"predictions.csv"}
        csv_file = os.path.join(self.directory, mode_dict[mode])
        series = []
        with open(csv_file, mode='r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                series.append(row)
        return series

    def update_tables(self):
        """Update the tables with the latest data."""
        for table, data in zip([self.series_table, self.prediction_table], 
                               [self.series_data, self.predicted_series]):
            table.delete(*table.get_children())
            for row in data:
                table.insert("", END, values=row)

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
        prediction_csv = os.path.join(self.directory, "predictions.csv")

        if os.path.exists(list_csv):
            self.progress_var.set(f"Loaded state of previous prediction.")
            self.series_data = self.load_data_from_csv(mode='series')
            self.start_button.config(text="Start Prediction")
            if os.path.exists(prediction_csv):
                self.predicted_series = self.load_data_from_csv(mode='predictions')
                self.is_paused = True
                self.start_button.config(text="Continue Prediction")
                self.update_settings_button_state()
            # Update to-do list to exclude already body-part predicted series
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
            if len(self.series_data) == 0:
                self.progress_var.set(f"No series found in directory. Please adjust parameters or change directory.")
                return
            self.save_series_list_to_csv()
            self.update_tables()
            self.progress_var.set(f"DICOM series loaded. Ready for prediction.")
        self.reset_button.config(state="normal")
    
    def reset_prediction(self):
        """Shows a confirmation popup before resetting progress."""
        if self.directory:
            # Define what should happen when the user confirms the reset
            def perform_reset(reset=True, prev_txt=''):
                if reset:
                    # Delete series and prediction CSVs
                    series_csv = os.path.join(self.directory, "list_of_series.csv")
                    prediction_csv = os.path.join(self.directory, "predictions.csv")
                    if os.path.exists(series_csv):
                        os.remove(series_csv)
                    if os.path.exists(prediction_csv):
                        os.remove(prediction_csv)

                    # Delete folder of preprocessed NRRD files if it exists
                    preprocessed_dir = os.path.join(self.directory, "preprocessed")
                    if os.path.exists(preprocessed_dir):
                        for root, dirs, files in os.walk(preprocessed_dir):
                            for file in files:
                                os.remove(os.path.join(root, file))
                        os.rmdir(preprocessed_dir)

                    # Reset data and update UI
                    self.series_data = []
                    self.predicted_series = []
                    self.update_tables()
                    self.is_paused = False
                    self.prediction_in_progress = False
                    self.update_settings_button_state()
                    # Disable Reset button
                    self.reset_button.config(state="disabled")
                    self.start_button.config(text="Start Prediction")

                    self.progress_var.set(f"Prediction progress reset. List Series to restart.")
                else: 
                    self.progress_var.set(prev_txt)

            prev_txt = self.progress_var.get()
            self.progress_var.set("Please answer the pop-up window.")
            # Call the function to show the reset confirmation popup
            show_reset_popup(self.root, perform_reset, prev_txt=prev_txt)



if __name__ == "__main__":
    root = Tk()
    app = CTScanSeriesPredictionApp(root)
    root.mainloop()
