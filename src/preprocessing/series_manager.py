import os
import csv
import pydicom

def load_and_display_series(app):
    """List series in the selected directory."""
    app.directory = app.directory_var.get()
    if app.directory == '':
        app.progress_var.set(f"Please specify a directory to load the series from.")
        return
    min_dcm_files = int(app.min_dcm_var.get()) if app.min_dcm_var.get().isdigit() else 1
    if min_dcm_files < 1:
        min_dcm_files = 1

    list_csv = os.path.join(app.directory, "list_of_series.csv")
    prediction_csv = os.path.join(os.path.join(app.directory, "predictions.csv"))

    if os.path.exists(list_csv):
        app.progress_var.set(f"Loaded state of previous prediction.")
        app.series_data = load_data_from_csv(app.directory, mode='series')
        app.all_series_data = app.series_data.copy()
        app.start_button.config(text="Start Prediction")
        if os.path.exists(prediction_csv):
            app.predicted_series = load_data_from_csv(app.directory ,mode='predictions')
            app.is_paused = True
            app.start_button.config(text="Continue Prediction")
            app.settings_button.config(state="disabled")
            predicted_series_identifiers = [
                (entry[1], entry[2], entry[3]) for entry in app.predicted_series
            ]
            app.series_data = [
                s for s in app.series_data if (s[1], s[2], s[3]) not in predicted_series_identifiers
            ]
        app.update_tables()
    else:
        app.progress_var.set(f"Loading all DICOM series in directory...")
        app.series_data = list_series_in_directory(app.directory, min_dcm_files)
        app.all_series_data = app.series_data.copy()
        if len(app.series_data) == 0:
            app.progress_var.set(f"No series found in directory. Please adjust parameters or change directory.")
            return
        save_series_list_to_csv(app.all_series_data, app.directory)
        app.update_tables()
        app.progress_var.set(f"DICOM series loaded. Ready for prediction.")
    app.reset_button.config(state="normal")
    app.edit_button.config(state="normal")  # Enable Edit button

def load_data_from_csv(directory, mode):
    """Loads data from a CSV file, including selection status."""
    mode_dict = {'series': "list_of_series.csv", 'predictions': "predictions.csv"}
    csv_file = os.path.join(directory, mode_dict[mode])
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

def list_series_in_directory(directory, min_dcm_files):
    """Lists all series in the directory with at least the minimum number of DICOM files."""
    series_data = []
    index = 1
    for root_dir, dirs, files in os.walk(directory):
        dcm_files = [f for f in files if f.endswith('.dcm')]
        if len(dcm_files) >= min_dcm_files:
            series_info = get_series_info(root_dir, dcm_files, index)
            series_data.append(series_info + [True])  # All series selected initially
            index += 1
    return series_data

def get_series_info(root_dir, dcm_files, index):
    """Extracts information from a DICOM series."""
    path_parts = root_dir.split(os.sep)
    patient_name = path_parts[-3]
    study = path_parts[-2]
    series = path_parts[-1]

    try:
        sample_dcm_path = os.path.join(root_dir, dcm_files[0])
        dcm = pydicom.dcmread(sample_dcm_path)
        mrn = dcm.PatientID
        series_uid = dcm.SeriesInstanceUID
    except Exception as e:
        #print(f"Error reading DICOM file: {e}")
        mrn = 'notfound'
        series_uid = 'notfound'

    return [index, patient_name, study, series, len(dcm_files), root_dir, mrn, series_uid]

def save_series_list_to_csv(series_data, directory):
    """Saves the list of series with their selection status to a CSV file."""
    csv_file = os.path.join(directory, "list_of_series.csv")
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Index", "Patient", "Study", "Series", "DCM Files", "Path", "MRN", "Series UID", "Selected"])
        for row in series_data:
            writer.writerow(row)

