import os
import csv
import pydicom
import pandas as pd
import time
from datetime import timedelta
from src.user_interface.ui_utils import update_start_button, update_reset_button

def create_series_df(app, min_dcm_files):
    """Traverse the given directory and collect series information."""
    series_dict = {}  # Dictionary to hold series information
    series_lookup = {}
    directory = app.directory
    app.progress_var.set("Initializing Series Listing...")
    app.progress_label.update()
    total_files = 0
    j = 0
    for _, _, files in os.walk(directory): total_files += len(files)
    start_time = time.time()

    for root, dirs, files in os.walk(directory):
        i = 0
        j += len(files)
        for file in files:
            filepath = os.path.join(root, file)
            i += 1
            # Check if the file is a DICOM file
            if not is_dicom_file(filepath):
                if i==3: break #allow up to 2 non-dcm files in a folder before considering it not a dcm series folder
                continue
            else:
                dicom_info = get_dicom_info(filepath)
                if dicom_info is None:
                    if i==3: break #similarly, allow up to 2 dicom files without series info 
                    continue
                #a dicom file with series info has been found
                series_uid = dicom_info["Series Instance UID"]
                if series_uid not in series_dict:
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
                        "Number of Slices": len(files) + 1 - i, #subtract the invalid files
                        "Series Directory": root,
                        "Body Part Label": " ",
                        "BODY PART (BP)": " ",
                        "BP Confidence": " ",
                        "IV CONTRAST (IVC)": " ",
                        "IVC Confidence": " ",
                        "Selected": True
                    }
                break
                
        #dir processed
        elapsed_time = time.time() - start_time
        seconds = round((elapsed_time / (j + 1)) * (total_files - (i + 1)))
        eta = timedelta(seconds=seconds)
        app.progress_var.set(f"Series Listing Progress:     {((j + 1) / total_files * 100):.2f}%       ETA: {str(eta)}")
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

    for key in data: 
        if data[key] == "": data[key] = ""

    return data

def load_and_display_series(app):
    """List series in the selected directory."""
    app.directory = app.directory_var.get()
    app.out_dir = os.path.join(app.directory, app.settings["output_folder"])
    min_dcm_files = app.settings["min_dcm"]
    if min_dcm_files < 1:
        min_dcm_files = 1

    list_csv = os.path.join(app.out_dir,"list_of_series.csv")
    prediction_csv = os.path.join(os.path.join(app.out_dir, "predictions.csv"))

    if os.path.exists(list_csv):
        update_start_button(app, "Start")
        app.progress_var.set(f"Loaded state of previous prediction. Press Play to continue or reset to delete the progress and start over.")
        app.series_data = pd.read_csv(list_csv, index_col="idx")
        app.all_series_data = app.series_data.copy()
        #app.start_button.config(text="Start Prediction")
        update_start_button(app, "Start")
        app.provide_button.config(state="normal", cursor="hand2")
        if os.path.exists(prediction_csv):
            app.provide_button.config(state="disabled", cursor="arrow")
            app.predicted_series = pd.read_csv(prediction_csv, index_col="idx")
            app.is_paused = True
            #app.start_button.config(text="Continue Prediction")
            update_start_button(app, "Start")
            app.settings_button.config(state="normal", cursor="hand2")
            predicted_indices = app.predicted_series.index
            app.series_data = app.series_data.drop(predicted_indices)
        app.update_tables()
    else:
        app.progress_var.set(f"Loading all DICOM series in directory...")
        app.series_data = create_series_df(app, min_dcm_files,)
        app.all_series_data = app.series_data.copy()
        if len(app.series_data) == 0:
            app.progress_var.set(f"No series found in directory. Please adjust settings or change directory.")
            return
        os.makedirs(app.out_dir, exist_ok=True)
        app.series_data.to_csv(list_csv, index=True)
        app.update_tables()
        app.progress_var.set(f"DICOM series loaded. Press Play to start the prediction.")
        app.provide_button.config(state="normal", cursor="hand2")
        update_start_button(app, "Start")
    #app.reset_button.config(state="normal", cursor="hand2")
    update_reset_button(app, "Active")
    app.edit_button.config(state="normal", cursor="hand2")  # Enable Edit button