import os
import pydicom
import time
import csv
import random
from datetime import timedelta
from tkinter import Tk, Label, Entry, Button, filedialog, ttk, StringVar, END
from processing_logic import process_series
from prediction.model_utils import load_models, get_device

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

        Label(root, text="Select a directory containing patient folders:").grid(row=0, column=0, sticky='w')
        self.directory_var = StringVar()
        self.directory_entry = Entry(root, textvariable=self.directory_var, width=50)
        self.directory_entry.grid(row=0, column=1)
        Button(root, text="Browse", command=self.select_directory).grid(row=0, column=2)

        Label(root, text="Enter minimum number of .dcm files to include a series:").grid(row=1, column=0, sticky='w')
        self.min_dcm_var = StringVar(value='20')
        self.min_dcm_entry = Entry(root, textvariable=self.min_dcm_var, width=10)
        self.min_dcm_entry.grid(row=1, column=1, sticky='w')

        Button(root, text="List Series", command=self.list_series).grid(row=2, column=0)
        self.start_button = Button(root, text="Start Prediction", command=self.start_prediction)
        self.start_button.grid(row=2, column=1)
        Button(root, text="Exit", command=self.exit_application).grid(row=2, column=2)
        
        # Create a frame to hold both the "Progress:" label and the progress output
        progress_frame = ttk.Frame(root)
        progress_frame.grid(row=3, column=0, columnspan=3, sticky='w', pady=10)

        # Create the labels inside the frame and use pack() to place them next to each other
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

    def select_directory(self):
        self.directory = filedialog.askdirectory()
        self.directory_var.set(self.directory)

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

    def start_prediction(self):
        """Starts or resumes the prediction process for each series."""
        if self.prediction_in_progress: #Pause button pressed
            self.start_button.config(text="Resume Prediction")
            self.prediction_in_progress = False
            self.is_paused = True

        elif self.is_paused: #Resume button pressed
            self.is_paused = False
            self.start_prediction()
        
        else:
            self.prediction_in_progress = True
            self.start_button.config(text="Pause Prediction")
            self.device = get_device()
            start_time = time.time()
            # Body part prediction
            to_do= self.series_data.copy()
            num_pred = len(to_do)
            models = None
            if len(to_do)>0 and not DUMMY_MODE:
                self.progress_var.set(f"Initializing Prediction...")
                models = load_models(self.device)
            for i, series in enumerate(to_do):
                self.root.update()
                if self.is_paused:
                    return
                body_part, contrast = process_series(models, series, self.directory, device=self.device) #add other models
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
            self.prediction_in_progress=False

    def update_tables(self):
        """Update the tables with the latest data."""
        for table, data in zip([self.series_table, self.prediction_table], 
                               [self.series_data, self.predicted_series]):
            table.delete(*table.get_children())
            for row in data:
                table.insert("", END, values=row)

    def exit_application(self):
        """Exits the application."""
        self.root.quit()
        self.root.destroy()

    def list_series(self):
        """List series in the selected directory."""
        self.directory = self.directory_var.get()
        min_dcm_files = int(self.min_dcm_var.get()) if self.min_dcm_var.get().isdigit() else 1
        if min_dcm_files < 1:
            min_dcm_files = 1

        list_csv = os.path.join(self.directory, "list_of_series.csv")
        prediction_csv = os.path.join(self.directory, "predictions.csv")

        if os.path.exists(list_csv):
            self.series_data = self.load_data_from_csv(mode='series')
            if os.path.exists(prediction_csv):
                self.predicted_series = self.load_data_from_csv(mode='predictions')
            # Update to-do list to exclude already body-part predicted series
            predicted_series_identifiers = [
                (entry[1], entry[2], entry[3]) for entry in self.predicted_series
            ]
            self.series_data = [
                s for s in self.series_data if (s[1], s[2], s[3]) not in predicted_series_identifiers
            ]
            self.update_tables()
            self.start_button.config(text="Start Prediction")
        else:
            self.progress_var.set(f"Loading all DICOM series in directory...")
            self.series_data = self.list_series_in_directory(self.directory, min_dcm_files)
            self.save_series_list_to_csv()
            self.update_tables()
            self.progress_var.set(f"DICOM series loaded. Ready for prediction.")


if __name__ == "__main__":
    root = Tk()
    app = CTScanSeriesPredictionApp(root)
    root.mainloop()
