import PySimpleGUI as sg
import os
import pydicom
import time
import csv
import random
from datetime import timedelta

class CTScanSeriesPredictionApp:
    def __init__(self):
        self.series_data = []
        self.body_part_predicted_series = []
        self.contrast_predicted_series = []
        self.to_do_list = []
        self.is_paused = False
        self.prediction_in_progress = False
        self.index_mapping = {}
        self.directory = None

        self.layout = [
            [sg.Text("Select a directory containing patient folders:")],
            [sg.Input(), sg.FolderBrowse()],
            [sg.Text("Enter minimum number of .dcm files to include a series:"), sg.InputText()],
            [sg.Button("List Series"), sg.Button("Start Prediction", key="StartResumePrediction"), sg.Button("Pause Prediction", key="PauseResume"), sg.Button("Exit")],
            [sg.Text('Progress:'), sg.ProgressBar(100, orientation='h', size=(50, 20), key='progressbar'), sg.Text("", size=(50, 1), key='eta')],
            [sg.Table(values=[], headings=["Index", "Patient", "Study", "Series", "DCM Files", "Path", "MRN", "Series UID"],
                      auto_size_columns=False, col_widths=[5, 15, 15, 15, 10, 20, 10, 20],
                      display_row_numbers=False, key="-SERIES-TABLE-", vertical_scroll_only=False)],
            [sg.Text("Body Part Prediction:")],
            [sg.Table(values=[], headings=["Index", "Patient", "Study", "Series", "Body Part Prediction"],
                      auto_size_columns=False, col_widths=[5, 15, 15, 15, 20],
                      display_row_numbers=False, key="-BODY-PART-TABLE-", vertical_scroll_only=False)],
            [sg.Text("Contrast Prediction:")],
            [sg.Table(values=[], headings=["Index", "Patient", "Study", "Series", "Body Part Prediction", "Contrast Prediction"],
                      auto_size_columns=False, col_widths=[5, 15, 15, 15, 20, 20],
                      display_row_numbers=False, key="-CONTRAST-TABLE-", vertical_scroll_only=False)]
        ]

        self.window = sg.Window("CT Scan Series Prediction", self.layout, resizable=True)

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
        total_dirs = sum([len(dirs) for r, dirs, f in os.walk(directory)])
        dirs_processed = 0
        index = 1
        self.window['eta'].update("Step 1/3: Listing Patient Series")

        for root, dirs, files in os.walk(directory):
            dcm_files = [f for f in files if f.endswith('.dcm')]
            if len(dcm_files) >= min_dcm_files:
                series_info = self.get_series_info(root, dcm_files, index)
                series_data.append(series_info)
                index += 1

            dirs_processed += 1
            self.update_progress_bar('progressbar', dirs_processed / total_dirs * 100)
        self.window['eta'].update("Patient Series listed. Please start the prediction.")
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

    def update_progress_bar(self, key, progress):
        """Updates the progress bar with the given key."""
        self.window[key].update(progress)

    def reset_prediction(self):
        """Resets the prediction process."""
        self.series_data = self.to_do_list.copy()
        self.body_part_predicted_series = []
        self.contrast_predicted_series = []
        self.window['-SERIES-TABLE-'].update(self.series_data)
        self.window['-BODY-PART-TABLE-'].update(self.body_part_predicted_series)
        self.window['-CONTRAST-TABLE-'].update(self.contrast_predicted_series)
        self.window['eta'].update("Prediction stopped.")
        self.window['progressbar'].update(0)

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
        self.window["Exit"].update(text="Stop Prediction")
        stop = False
        self.paused = False
        start_time = time.time()

        print("Starting body-part prediction with the following list:")
        print(self.to_do_list)

        # Body part prediction
        num_body_part_pred = len(self.to_do_list)
        for i, series in enumerate(self.to_do_list):
            event, values = self.window.read(100)
            if event == sg.WIN_CLOSED or event == "Exit":
                self.reset_prediction()
                break

            if event == 'PauseResume':
                self.pause_prediction()

            if stop:
                break

            body_part = self.dummy_body_part_prediction(series[5])
            elapsed_time = time.time() - start_time
            seconds = round((elapsed_time / (i + 1)) * (num_body_part_pred - (i + 1)))
            eta = timedelta(seconds=seconds)
            self.window['eta'].update(f"Step 2/3: Predicting Body-Part (ETA: {str(eta)})")
            self.update_progress_bar('progressbar', (i + 1) / num_body_part_pred * 100)

            self.series_data.remove(series)
            body_part_series_entry = series[:4] + [body_part]
            self.body_part_predicted_series.append(body_part_series_entry)
            self.window['-SERIES-TABLE-'].update(self.series_data)
            self.window['-BODY-PART-TABLE-'].update(self.body_part_predicted_series)
            self.save_body_part_predictions_to_csv()

        print("Finished. Doing Contrast prediction with the following scans:")
        print(self.body_part_predicted_series)
        # Contrast prediction
        to_do_contrast = self.body_part_predicted_series.copy()
        num_contrast_pred = len(to_do_contrast)
        for i, series in enumerate(to_do_contrast):
            event, values = self.window.read(100)
            if event == sg.WIN_CLOSED or event == "Exit":
                self.reset_prediction()
                break

            if event == 'PauseResume':
                self.pause_prediction()

            if stop:
                break

            contrast_prediction = self.dummy_contrast_prediction(series, series[-1])
            elapsed_time = time.time() - start_time
            seconds = round((elapsed_time / (i + 1)) * (num_contrast_pred - (i + 1)))
            eta = timedelta(seconds=seconds)
            self.window['eta'].update(f"Step 3/3: Predicting Contrast (ETA: {str(eta)})")
            self.update_progress_bar('progressbar', (i + 1) / num_contrast_pred * 100)

            self.body_part_predicted_series.remove(series)
            contrast_series_entry = series + [contrast_prediction]
            self.contrast_predicted_series.append(contrast_series_entry)
            self.window['-BODY-PART-TABLE-'].update(self.body_part_predicted_series)
            self.window['-CONTRAST-TABLE-'].update(self.contrast_predicted_series)
            self.save_contrast_predictions_to_csv()
            self.save_body_part_predictions_to_csv()

        self.window["Exit"].update(text="Exit")

    def pause_prediction(self):
        """Handles the pausing and resuming of the prediction process."""
        self.window["PauseResume"].update(text="Resume Prediction")
        self.paused = True

        while True:
            event, values = self.window.read(100)
            if event == 'PauseResume':
                self.window["PauseResume"].update(text="Pause Prediction")
                self.paused = False
                break
            if event == "Exit":
                self.reset_prediction()
                stop = True
                break

    def run(self):
        """Runs the main event loop for the application."""
        while True:
            event, values = self.window.read()

            if event == sg.WIN_CLOSED or event == "Exit":
                break

            if event == "List Series":
                self.directory = values[0]
                min_dcm_files = int(values[1]) if values[1].isdigit() else 1
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
                    #Append by those already contrast-predicted
                    for entry in self.contrast_predicted_series: predicted_series_identifiers.append((entry[1], entry[2], entry[3]))
                    
                    self.to_do_list = [
                        s for s in self.series_data if (s[1], s[2], s[3]) not in predicted_series_identifiers
                    ]
                    
                    # Update the series_data to only show unprocessed series
                    self.series_data = self.to_do_list.copy()

                    self.window['-SERIES-TABLE-'].update(self.series_data)
                    self.window['-BODY-PART-TABLE-'].update(self.body_part_predicted_series)
                    self.window['-CONTRAST-TABLE-'].update(self.contrast_predicted_series)
                    self.window["StartResumePrediction"].update(text="Resume Prediction")
                else:
                    self.series_data = self.list_series_in_directory(self.directory, min_dcm_files)
                    self.to_do_list = self.series_data.copy()  # Initialize to_do_list here after listing
                    self.save_series_list_to_csv()
                    self.window['-SERIES-TABLE-'].update(self.series_data)
                    self.update_progress_bar('progressbar', 0)  # Reset progress bar after listing

            if event == "StartResumePrediction":
                self.start_prediction()

        self.window.close()

if __name__ == "__main__":
    app = CTScanSeriesPredictionApp()
    app.run()
