import time
import numpy as np
import time
import gc
from datetime import timedelta
from src.preprocessing.preprocess_series import preprocess_series
from src.prediction.get_probabilities import get_body_part_probabilities, get_contrast_probability
from src.prediction.prediction_utils import load_models, save_predictions_to_csv

#series_info: [index, patient_name, study, series, len(dcm_files), root, mrn, series_uid, (body_part)]

LABEL_DICT = {0:'HeadNeck', 1:'Chest', 2:'Abdomen'}

def process_loop(app):
    start_time = time.time()
    to_do = [s for s in app.series_data if s[-1]]  # Only process selected series
    num_pred = len(to_do)
    models = None
    if len(to_do):
        app.progress_var.set(f"Initializing Prediction...")
        models = load_models(app.device)
    for i, series in enumerate(to_do):
        gc.collect()
        app.root.update()
        if app.is_paused:
            del models
            gc.collect
            return
        body_part, bp_conf, contrast, c_conf = process(models, series, app.directory,
                                                device=app.device, save_nrrds=app.settings.get("store_nrrd_files", False))
        elapsed_time = time.time() - start_time
        seconds = round((elapsed_time / (i + 1)) * (num_pred - (i + 1)))
        eta = timedelta(seconds=seconds)
        app.progress_var.set(f"{((i + 1) / num_pred * 100):.2f}%       ETA: {str(eta)}")
        app.series_data.remove(series)
        series_entry = series[:4] + [body_part] + [bp_conf] + [contrast] + [c_conf]
        app.predicted_series.append(series_entry)
        app.update_tables()
        save_predictions_to_csv(app.predicted_series, app.directory)
    del models
    app.start_button.config(text="Start Prediction")
    app.prediction_in_progress = False
    app.settings_button.config(state="normal")
    app.reset_button.config(state="normal")

def process(models, series_info, directory=None, device='cpu', save_nrrds=False):
    img = preprocess_series(series_info=series_info, directory=directory, verbose=True, save_nrrds=save_nrrds)
    if img is None: return 'ERROR', 'ERROR', 'ERROR', 'ERROR'
    if models is None: return 'DUMMY', '100%', 'DUMMY', '100%'
    part_model, hn_model, ch_model, ab_model = models
    
    part_probabilities = get_body_part_probabilities(part_model, img, device=device)
    part_prediction = np.argmax(part_probabilities)
    part_conf = str(round(part_probabilities[part_prediction]*100,2))+"%"

    if part_prediction == 0: contrast_prob = get_contrast_probability(hn_model, img, part='HeadNeck', device=device)
    elif part_prediction == 1: contrast_prob = get_contrast_probability(ch_model, img, part='Chest' ,device=device)
    elif part_prediction == 2: contrast_prob = get_contrast_probability(ab_model, img, part='Abdomen', device=device)
    else: raise Exception("FATAL ERROR, UNKNOWN PART PREDICTION.")

    contrast = (contrast_prob >= 0.5).astype(int)
    if contrast == 0: contrast_prob = 1-contrast_prob
    c_conf = str(round(contrast_prob*100,2))+"%"
    return LABEL_DICT[part_prediction], part_conf, contrast, c_conf






