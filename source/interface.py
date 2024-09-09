import time
import random
import os
import numpy as np
from preprocessing import preprocess_series
from predict_body_part import get_body_part
#series_info: [index, patient_name, study, series, len(dcm_files), root, mrn, series_uid, (body_part)]

LABEL_DICT = {0:'HeadNeck', 1:'Chest', 2:'Abdomen'}

def body_part_prediction(model, series_info, directory=None, device='cpu'):
    nrrd_file = preprocess_series(series_info=series_info, directory=directory, verbose=True)
    if nrrd_file == 0: return 'ERROR'
    probabilities = get_body_part(model, nrrd_file, device=device)
    prediction = np.argmax(probabilities)
    return LABEL_DICT[prediction]

def contrast_prediction(model, series_info, directory=None):
    """Simulates a contrast prediction function that returns 0 or 1."""
    body_part = series_info[-1]
    time.sleep(3)  # Simulate some processing time
    return random.choice([0, 1])  # Simulated contrast prediction





