import time
import random
import os
import numpy as np
from preprocessing.preprocess_series import preprocess_series
from prediction.get_probabilities import get_body_part_probabilities, get_contrast_probability
#series_info: [index, patient_name, study, series, len(dcm_files), root, mrn, series_uid, (body_part)]

LABEL_DICT = {0:'HeadNeck', 1:'Chest', 2:'Abdomen'}

def process_series(models, series_info, directory=None, device='cpu', save_nrrds=False):
    img = preprocess_series(series_info=series_info, directory=directory, verbose=True, save_nrrds=save_nrrds)
    if img is None: return 'ERROR', 'ERROR'
    if models is None: return 'DUMMY', 0
    part_model, hn_model, ch_model, ab_model = models
    
    part_probabilities = get_body_part_probabilities(part_model, img, device=device)
    part_prediction = np.argmax(part_probabilities)

    if part_prediction == 0: contrast_prob = get_contrast_probability(hn_model, img, part='HeadNeck', device=device)
    elif part_prediction == 1: contrast_prob = get_contrast_probability(ch_model, img, part='Chest' ,device=device)
    elif part_prediction == 2: contrast_prob = get_contrast_probability(ab_model, img, part='Abdomen', device=device)
    else: raise Exception("FATAL ERROR, UNKNOWN PART PREDICTION.")

    contrast = (contrast_prob >= 0.5).astype(int) 
    return LABEL_DICT[part_prediction], contrast





