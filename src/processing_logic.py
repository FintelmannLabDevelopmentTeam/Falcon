import time
import numpy as np
import time
import gc
import os
import pandas as pd
from datetime import timedelta
from src.preprocessing.preprocess_series import preprocess_series
from src.prediction.get_probabilities import get_body_part_probabilities, get_contrast_probability
from src.prediction.prediction_utils import load_models, save_predictions_to_csv

#series_info: [index, patient_name, study, series, len(dcm_files), root, mrn, series_uid, (body_part)]

LABEL_DICT = {0:'HeadNeck', 1:'Chest', 2:'Abdomen'}
REV_LABEL_DICT = {'HeadNeck':0, 'Chest':1, 'Abdomen':2}

def process_loop(app):
    verbose = app.settings.get("verbose",False)
    store_preprocessed = app.settings.get("store_nrrd_files", False)
    if verbose: print("Starting the processing of series...")
    start_time = time.time()
    #to_do = [s for s in app.series_data if s[-1]]  # Only process selected series
    to_do = app.series_data[app.series_data["Selected"]==True].copy()
    num_pred = len(to_do)
    models = None
    if len(to_do):
        app.progress_var.set(f"Initializing Prediction...")
        models = load_models(app.device)
        if store_preprocessed:
            preprocessed_dir = os.path.join(app.directory, "preprocessed")
            if not os.path.exists(preprocessed_dir): os.makedirs(preprocessed_dir)
        if len(app.predicted_series) == 0: app.predicted_series = pd.DataFrame(columns=app.series_data.columns)

    for i, (index,series) in enumerate(to_do.iterrows()):
        gc.collect()
        app.root.update()
        if app.is_paused:
            del models
            gc.collect()
            return
        series["Body Part (BP)"], series["BP Confidence"], series["IV Contrast (IVC)"], series["IVC Confidence"] = process(models, 
                                    series, app.directory, device=app.device, save_nrrds=store_preprocessed, verbose=verbose)
        elapsed_time = time.time() - start_time
        seconds = round((elapsed_time / (i + 1)) * (num_pred - (i + 1)))
        eta = timedelta(seconds=seconds)
        app.progress_var.set(f"{((i + 1) / num_pred * 100):.2f}%       ETA: {str(eta)}")
        app.series_data = app.series_data[app.series_data["Index"]!=series["Index"]]
        app.predicted_series = pd.concat([app.predicted_series, pd.DataFrame([series], columns=app.predicted_series.columns)], ignore_index=False)
        app.update_tables()
        #app.predicted_series.set_index("idx", inplace=True)
        app.predicted_series.to_csv(os.path.join(app.directory, "predictions.csv"), index=True, index_label='idx')
        #save_predictions_to_csv(app.predicted_series, app.directory)
    del models
    app.start_button.config(text="Start Prediction")
    app.prediction_in_progress = False
    app.settings_button.config(state="normal")
    app.reset_button.config(state="normal")

def process(models, series_info, directory=None, device='cpu', save_nrrds=False, verbose=False):
    if verbose: print(f"\nProcessing series {series_info['Index']}:")
    img = preprocess_series(series_info=series_info, directory=directory, verbose=verbose, save_nrrds=save_nrrds)
    if img is None: return 'ERROR', 'ERROR', 'ERROR', 'ERROR'
    if models is None: return 'DUMMY', '100%', 'DUMMY', '100%'
    part_model, hn_model, ch_model, ab_model = models
    
    if series_info["Body Part Label"] in ["HeadNeck", "Chest", "Abdomen"]:
        if verbose: print(f"Using provided body-part label {series_info['Body Part Label']}.")
        part_prediction = REV_LABEL_DICT[series_info["Body Part Label"]]
        part_conf = "Provided"
    else:
        if verbose: print("Predicting the body-part for this series:")
        part_probabilities = get_body_part_probabilities(part_model, img, device=device)
        if verbose: print(f"Got the following probabilities for the body-parts: {part_probabilities}")
        part_prediction = np.argmax(part_probabilities)
        part_conf = str(round(part_probabilities[part_prediction]*100,2))+"%"
        if verbose: print(f"Body-Part Prediction: {LABEL_DICT[part_prediction]} with confidence {part_conf}")

    if verbose: print(f"Initiating contrast prediction with the {LABEL_DICT[part_prediction]}-Model...")
    if part_prediction == 0: contrast_prob = get_contrast_probability(hn_model, img, part='HeadNeck', device=device)
    elif part_prediction == 1: contrast_prob = get_contrast_probability(ch_model, img, part='Chest' ,device=device)
    elif part_prediction == 2: contrast_prob = get_contrast_probability(ab_model, img, part='Abdomen', device=device)
    else: raise Exception("FATAL ERROR, UNKNOWN PART PREDICTION.")

    contrast = (contrast_prob >= 0.5).astype(int)
    if contrast == 0: contrast_prob = 1-contrast_prob
    c_conf = str(round(contrast_prob*100,2))+"%"
    if verbose: print(f"Contrast Prediction: {contrast} with confidence {c_conf}")
    return LABEL_DICT[part_prediction], part_conf, contrast, c_conf






