import os
import pydicom
import pandas as pd
from collections import defaultdict
from tqdm import tqdm

def is_dicom_file(filepath):
    """Check if a file is a DICOM file by reading basic metadata."""
    try:
        pydicom.dcmread(filepath)  # Removed stop_before_pixels for full read
        return True
    except:
        return False

def get_dicom_info(filepath):
    """Extract key information from a DICOM file, handling missing attributes."""
    dicom_data = pydicom.dcmread(filepath)  # Removed stop_before_pixels for full read
    
    # Check if it's a regular DICOM file and has necessary attributes
    try:
        patient_id = dicom_data.PatientID
        study_instance_uid = dicom_data.StudyInstanceUID
        series_instance_uid = dicom_data.SeriesInstanceUID
    except AttributeError:
        # Skip files that don't have these attributes (like DICOMDIR files)
        return None

    return {
        "Patient ID": patient_id,
        "Study Instance UID": study_instance_uid,
        "Series Instance UID": series_instance_uid
    }

def traverse_dicom_directory(directory):
    """Traverse the given directory and collect series information."""
    series_dict = {}  # Dictionary to hold series information
    
    for root, dirs, files in tqdm(os.walk(directory)):
        for file in files:
            filepath = os.path.join(root, file)
            
            # Check if the file is a DICOM file
            if is_dicom_file(filepath):
                dicom_info = get_dicom_info(filepath)
                if dicom_info is None:
                    continue
                
                # Use Series Instance UID as the unique key
                series_uid = dicom_info["Series Instance UID"]
                
                if series_uid not in series_dict:
                    # If the series is new, add it to the dict
                    series_dict[series_uid] = {
                        "Patient ID": dicom_info["Patient ID"],
                        "Study Instance UID": dicom_info["Study Instance UID"],
                        "Series Instance UID": dicom_info["Series Instance UID"],
                        "Number of Slices": 1,
                        "Series Directory": root
                    }
                else:
                    # If the series exists, increment the slice count
                    series_dict[series_uid]["Number of Slices"] += 1
    
    return series_dict

def create_series_dataframe(series_dict):
    """Convert the series information into a pandas DataFrame."""
    df = pd.DataFrame.from_dict(series_dict, orient="index")
    return df

def main(directory):
    # Traverse the directory and get series information
    series_info = traverse_dicom_directory(directory)
    
    # Convert series information to a pandas DataFrame
    df = create_series_dataframe(series_info)
    
    # Display the DataFrame
    print(df)

if __name__ == "__main__":
    dicom_directory = "/Users/philipp/Heavy_Data/TestdataMulticenter"
    main(dicom_directory)
