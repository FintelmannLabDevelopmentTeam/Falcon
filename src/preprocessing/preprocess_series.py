import os
import glob
import numpy as np
import SimpleITK as sitk
from src.preprocessing.dicom_loading import get_sitk_from_dicom
from src.preprocessing.image_transformation import respacing, crop_image

CROP_SHAPE = [200, 200, 100]
SCALE_SIZE = [150,150,100]

def preprocess_series(series_info, directory=None, verbose=False, save_nrrds=False):
    pre_dir = os.path.join(directory, "preprocessed")
    file_dir = os.path.join(pre_dir, str(series_info[0])+".nrrd")
    #if not os.path.exists(pre_dir): os.makedirs(pre_dir)

    try:
        if os.path.exists(file_dir):
            if verbose: print("Loading existing file")
            sitk_object = sitk.ReadImage(file_dir)
            return sitk_object
        if verbose: print("No preprocessed file exists for this series, initiating preprocessing:")
        sitk_object = get_sitk_from_dicom(series_info[5], verbose=verbose)
        respaced_object = respacing(sitk_object, interp_type='linear',new_spacing=(1, 1, 3))
        cropped_object = crop_image(respaced_object, crop_shape=CROP_SHAPE, clipping=-1000, 
                                    scale_size=SCALE_SIZE, verbose=verbose, mass_centered=False)
        if verbose: print("Preprocessing finished.")
        if save_nrrds:
            nrrdWriter = sitk.ImageFileWriter()
            nrrdWriter.SetFileName(file_dir)
            nrrdWriter.SetUseCompression(True)
            nrrdWriter.Execute(cropped_object)
            if verbose: print("Saved "+str(file_dir)+" for scan " + str(series_info[0]))
    except Exception as e:
        if verbose: 
            print("The following error appeared during preprocessing of this series:")
            print(e)
        return None
    return cropped_object




