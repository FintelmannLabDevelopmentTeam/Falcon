import pydicom
import numpy as np
import glob
import SimpleITK as sitk

def get_sitk_from_dicom(dicom_dir, verbose=False):
    dicomFiles = sorted(glob.glob(dicom_dir + '/*.dcm'))
    slices, img_spacing, img_direction, img_origin = load_dicom(dicomFiles)
    if 0.0 in img_spacing:
        if verbose: print ('ERROR - Zero spacing found for patient,', img_spacing)
        raise Exception("Zero spacing found for patient.")
    imgCube = getPixelArray(slices)
    imgSitk = sitk.GetImageFromArray(imgCube)
    imgSitk.SetSpacing(img_spacing)
    imgSitk.SetDirection(img_direction)
    imgSitk.SetOrigin(img_origin)
    
    return imgSitk

def load_dicom(slice_list):
    if len(slice_list)<11:
        raise Exception("Not enough DICOM slices in directory.")
    img_dirs = []
    for img_dir in slice_list:
        img_type = img_dir.split('/')[-1].split('.')[0]
        if img_type not in ['RTDOSE', 'RTSTRUCT']:
            img_dirs.append(img_dir)
    slices = []
    for s, t in zip(img_dirs, img_dirs[1:]):
        slice1 = pydicom.read_file(s)
        slice2 = pydicom.read_file(t)
        if slice1.SliceThickness == None:
            slice1.SliceThickness = float(np.abs(slice1.ImagePositionPatient[2] - slice2.ImagePositionPatient[2]))
        if slice1.ImageOrientationPatient==[0, 1, 0, 0, 0, -1]:
            slice1.ImageOrientationPatient=[1, 0, 0, 0, 1, 0]
            slice2.ImageOrientationPatient=[1, 0, 0, 0, 1, 0]
        if float(slice1.SliceThickness) == np.abs(slice1.ImagePositionPatient[2] - slice2.ImagePositionPatient[2]):
            slices.append(slice1)
        elif slice1.ImageOrientationPatient==[1, 0, 0, 0, 1, 0]:    
            slices.append(slice1)
        if t == slice_list[-1]:
            slices.append(slice2)
    slices.sort(key=lambda x: float(x.ImagePositionPatient[2]))
    slice_thickness = np.abs(slices[0].ImagePositionPatient[2] - slices[1].ImagePositionPatient[2])
    if slice_thickness > 3 or slice_thickness == 0:
        slice_thickness = np.abs(slices[9].ImagePositionPatient[2] - slices[10].ImagePositionPatient[2])
    for s in slices:
        s.SliceThickness = slice_thickness
    img_spacing = [float(slices[0].PixelSpacing[0]), float(slices[0].PixelSpacing[1]), slice_thickness]
    img_direction = [float(i) for i in slices[0].ImageOrientationPatient] + [0, 0, 1]
    img_origin = slices[0].ImagePositionPatient
    
    return slices, img_spacing, img_direction, img_origin

def getPixelArray(slices):

    image = np.stack([s.pixel_array for s in slices])
    image = image.astype(np.int16) #Possible, as values should be <32k

    # Convert to Hounsfield units (HU)
    for slice_number in range(len(slices)):
        intercept = slices[slice_number].RescaleIntercept
        slope = slices[slice_number].RescaleSlope
        if slope != 1:
            image[slice_number] = slope * image[slice_number].astype(np.float64)
            image[slice_number] = image[slice_number].astype(np.int16)
        image[slice_number] += np.int16(intercept)
    image[image < -1000] = -1000 #Clip at HU value for air
    return np.array(image, dtype=np.int16)