import os
import csv
import pydicom
import pandas as pd
import time
from datetime import timedelta

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
            series_data.append(series_info + [""] + [True])  # Body-par label and Selected
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
        mrn = 'not found'
        series_uid = 'not found'

    return [index, patient_name, study, series, len(dcm_files), root_dir, mrn, series_uid]

def save_series_list_to_csv(series_data, directory):
    """Saves the list of series with their selection status to a CSV file."""
    csv_file = os.path.join(directory, "list_of_series.csv")
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Index", "Patient", "Study", "Series", "DCM Files", "Path", "MRN", "Series UID", "Body Part Label","Selected"])
        for row in series_data:
            writer.writerow(row)

def create_series_df(app, min_dcm_files):
    """Traverse the given directory and collect series information."""
    series_dict = {}  # Dictionary to hold series information
    series_lookup = {}
    directory = app.directory
    app.progress_var.set("Initializing Series Listing...")
    app.progress_label.update()
    total_files = 0
    i = 0
    for _, _, files in os.walk(directory): total_files += len(files)
    start_time = time.time()

    for root, dirs, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            i += 1
            # Check if the file is a DICOM file
            if is_dicom_file(filepath):
                dicom_info = get_dicom_info(filepath)
                if dicom_info is None: continue
                series_uid = dicom_info["Series Instance UID"]
                if series_uid not in series_dict:
                    dicom_info = get_dicom_info(filepath)
                    # If the series is new, add it to the dict
                    series_dict[series_uid] = {
                        "Index": -1,
                        "Patient ID": dicom_info["Patient ID"],
                        "Study Instance UID": dicom_info["Study Instance UID"],
                        "Series Instance UID": series_uid,
                        "Study Description" : dicom_info["Study Description"],
                        "Series Description": dicom_info["Series Description"],
                        "Patient Folder": dicom_info["Patient Folder"],
                        "Study Folder": dicom_info["Study Folder"],
                        "Series Folder": dicom_info["Series Folder"],
                        "Number of Slices": 1,
                        "Series Directory": root,
                        "Body Part Label": " ",
                        "Body Part (BP)": " ",
                        "BP Confidence": " ",
                        "IV Contrast (IVC)": " ",
                        "IVC Confidence": " ",
                        "Selected": True
                    }
                else:
                    # If the series exists, increment the slice count
                    series_dict[series_uid]["Number of Slices"] += 1
                
        #dir processed
        elapsed_time = time.time() - start_time
        seconds = round((elapsed_time / (i + 1)) * (total_files - (i + 1)))
        eta = timedelta(seconds=seconds)
        app.progress_var.set(f"{((i + 1) / total_files * 100):.2f}%       ETA: {str(eta)}")
        app.progress_label.update()

    df = pd.DataFrame.from_dict(series_dict, orient="index")
    filtered_df = df[df["Number of Slices"] >= min_dcm_files]
    filtered_df["Index"] = range(1, len(filtered_df)+1)
    filtered_df["idx"] = range(1, len(filtered_df)+1)
    filtered_df.set_index("idx", inplace=True)
    return filtered_df

def is_dicom_file(filepath):
    """Check if a file is a DICOM file by reading basic metadata."""
    try: pydicom.dcmread(filepath, stop_before_pixels=True)
    except: return False
    return True

def get_dicom_info(filepath):
    """Extract key information from a DICOM file, handling missing attributes."""
    dicom_data = pydicom.dcmread(filepath, stop_before_pixels=True)
    data = {}
    
    # Check if it's a regular DICOM file and has necessary attributes
    try: data["Series Instance UID"] = dicom_data.SeriesInstanceUID
    except: return None

    try: data["Patient ID"] = dicom_data.PatientID
    except: data["Patient ID"] = "unknown"

    try: data["Study Instance UID"] = dicom_data.StudyInstanceUID
    except: data["Study Instance UID"] = "unknown"

    try: data["Study Description"] = dicom_data.StudyDescription
    except: data["Study Description"] = "unknown"

    try: data["Series Description"] = dicom_data.SeriesDescription
    except: data["Series Description"] = "unknown"

    path_parts = filepath.split(os.sep)
    try: data["Series Folder"] = path_parts[-2]
    except: data["Series Folder"] = "unknown"

    try: data["Study Folder"] = path_parts[-3]
    except: data["Study Folder"] = "unknown"

    try: data["Patient Folder"] = path_parts[-4]
    except: data["Patient Folder"] = "unknown"

    return data

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
        app.series_data = pd.read_csv(list_csv, index_col="idx")
        app.all_series_data = app.series_data.copy()
        app.start_button.config(text="Start Prediction")
        app.provide_button.config(state='normal')
        if os.path.exists(prediction_csv):
            app.provide_button.config(state='disabled')
            app.predicted_series = pd.read_csv(prediction_csv, index_col="idx")
            app.is_paused = True
            app.start_button.config(text="Continue Prediction")
            app.settings_button.config(state="disabled")
            predicted_indices = app.predicted_series.index
            app.series_data = app.series_data.drop(predicted_indices)
        app.update_tables()
    else:
        app.progress_var.set(f"Loading all DICOM series in directory...")
        app.series_data = create_series_df(app, min_dcm_files,)
        app.all_series_data = app.series_data.copy()
        if len(app.series_data) == 0:
            app.progress_var.set(f"No series found in directory. Please adjust parameters or change directory.")
            return
        app.series_data.to_csv(list_csv, index=True)
        app.update_tables()
        app.progress_var.set(f"DICOM series loaded. Ready for prediction.")
        app.provide_button.config(state='normal')
    app.reset_button.config(state="normal")
    app.edit_button.config(state="normal")  # Enable Edit button