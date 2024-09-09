import os
import pydicom
import time
import csv
import random
from datetime import timedelta
from tkinter import Tk, Label, Entry, Button, filedialog, ttk, StringVar, END

class CTScanSeriesPredictionApp:
    def __init__(self, root):
        self.series_data = []
        self.body_part_predicted_series = []
        self.contrast_predicted_series = []
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

        Label(root, text="Body Part Prediction:").grid(row=5, column=0, sticky='w')
        self.body_part_table = ttk.Treeview(root, columns=("Index", "Patient", "Study", "Series", "Body Part Prediction"), show="headings")
        self.body_part_table.grid(row=6, column=0, columnspan=4, sticky='nsew')
        for col in self.body_part_table["columns"]:
            self.body_part_table.heading(col, text=col)
            self.body_part_table.column(col, width=120)

        Label(root, text="Contrast Prediction:").grid(row=7, column=0, sticky='w')
        self.contrast_table = ttk.Treeview(root, columns=("Index", "Patient", "Study", "Series", "Body Part Prediction", "Contrast Prediction"), show="headings")
        self.contrast_table.grid(row=8, column=0, columnspan=4, sticky='nsew')
        for col in self.contrast_table["columns"]:
            self.contrast_table.heading(col, text=col)
            self.contrast_table.column(col, width=150)

    def select_directory(self):
        self.directory = filedialog.askdirectory()
        self.directory_var.set(self.directory)

    def dummy_body_part_prediction(self, series_path):
        """Simulates a body-part prediction function that returns a body part name."""
        time.sleep(3)  # Simulate some processing time
        return "Chest"  # Simulated body-part prediction

    def dummy_contrast_prediction(self, series_info, body_part):
        """Simulates a contrast prediction function that returns 0 or 1."""
        time.sleep(3)  # Simulate some processing time
        return random.choice([0, 1])  # Simulated contrast prediction

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

    def save_body_part_predictions_to_csv(self):
        """Saves the body part prediction results to a CSV file."""
        csv_file = os.path.join(self.directory, "body_part_predictions.csv")
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Index", "Patient", "Study", "Series", "Body Part Prediction"])
            writer.writerows(self.body_part_predicted_series)

    def save_contrast_predictions_to_csv(self):
        """Saves the contrast prediction results to a CSV file."""
        csv_file = os.path.join(self.directory, "contrast_predictions.csv")
        with open(csv_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Index", "Patient", "Study", "Series", "Body Part Prediction", "Contrast Prediction"])
            writer.writerows(self.contrast_predicted_series)

    def load_data_from_csv(self, mode):
        """Loads data from a CSV file."""
        mode_dict = {'series':"list_of_series.csv", 'body_part':"body_part_predictions.csv", 'contrast':"contrast_predictions.csv"}
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
            start_time = time.time()
            # Body part prediction
            to_do_body_part = self.series_data.copy()
            num_body_part_pred = len(to_do_body_part)
            for i, series in enumerate(to_do_body_part):
                self.root.update()
                if self.is_paused:
                    return
                body_part = self.dummy_body_part_prediction(series[5])
                elapsed_time = time.time() - start_time
                seconds = round((elapsed_time / (i + 1)) * (num_body_part_pred - (i + 1)))
                eta = timedelta(seconds=seconds)
                self.progress_var.set(f"Step 2/3: Predicting Body-Part, {((i + 1) / num_body_part_pred * 100):.2f}%, ETA {str(eta)})")

                self.series_data.remove(series)
                body_part_series_entry = series[:4] + [body_part]
                self.body_part_predicted_series.append(body_part_series_entry)
                self.update_tables()
                self.save_body_part_predictions_to_csv()

            # Contrast prediction
            to_do_contrast = self.body_part_predicted_series.copy()
            num_contrast_pred = len(to_do_contrast)
            for i, series in enumerate(to_do_contrast):
                self.root.update()
                if self.is_paused:
                    return
                contrast_prediction = self.dummy_contrast_prediction(series, series[-1])
                elapsed_time = time.time() - start_time
                seconds = round((elapsed_time / (i + 1)) * (num_contrast_pred - (i + 1)))
                eta = timedelta(seconds=seconds)
                self.progress_var.set(f"Step 3/3: Predicting Contrast, {((i + 1) / num_contrast_pred * 100):.2f}%, ETA {str(eta)})")

                self.body_part_predicted_series.remove(series)
                contrast_series_entry = series + [contrast_prediction]
                self.contrast_predicted_series.append(contrast_series_entry)
                self.update_tables()
                self.save_contrast_predictions_to_csv()
                self.save_body_part_predictions_to_csv()
            self.start_button.config(text="Start Prediction")
            self.prediction_in_progress=False

    def update_tables(self):
        """Update the tables with the latest data."""
        for table, data in zip([self.series_table, self.body_part_table, self.contrast_table], 
                               [self.series_data, self.body_part_predicted_series, self.contrast_predicted_series]):
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
        body_part_csv = os.path.join(self.directory, "body_part_predictions.csv")
        contrast_csv = os.path.join(self.directory, "contrast_predictions.csv")

        if os.path.exists(list_csv):
            self.series_data = self.load_data_from_csv(mode='series')
            if os.path.exists(body_part_csv):
                self.body_part_predicted_series = self.load_data_from_csv(mode='body_part')
            if os.path.exists(contrast_csv):
                self.contrast_predicted_series = self.load_data_from_csv(mode='contrast')

            # Update to-do list to exclude already body-part predicted series
            predicted_series_identifiers = [
                (entry[1], entry[2], entry[3]) for entry in self.body_part_predicted_series
            ]
            # Append those already contrast-predicted
            for entry in self.contrast_predicted_series: 
                predicted_series_identifiers.append((entry[1], entry[2], entry[3]))

            self.series_data = [
                s for s in self.series_data if (s[1], s[2], s[3]) not in predicted_series_identifiers
            ]

            self.update_tables()
            self.start_button.config(text="Continue Prediction")
        else:
            self.progress_var.set(f"Step 1/3: Loading all DICOM series...")
            self.series_data = self.list_series_in_directory(self.directory, min_dcm_files)
            self.save_series_list_to_csv()
            self.update_tables()
            self.progress_var.set(f"DICOM series loaded. Ready for prediction.")


if __name__ == "__main__":
    root = Tk()
    app = CTScanSeriesPredictionApp(root)
    root.mainloop()
