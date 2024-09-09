import SimpleITK as sitk
import numpy as np
from scipy import ndimage
from skimage.transform import resize

def respacing(img, interp_type, new_spacing): 
    ### calculate new spacing
    old_size = img.GetSize()
    old_spacing = img.GetSpacing()

    new_size = [
        int(round((old_size[0] * old_spacing[0]) / float(new_spacing[0]))),
        int(round((old_size[1] * old_spacing[1]) / float(new_spacing[1]))),
        int(round((old_size[2] * old_spacing[2]) / float(new_spacing[2])))
        ]

    ### choose interpolation algorithm
    if interp_type == 'linear':
        interp_type = sitk.sitkLinear
    elif interp_type == 'bspline':
        interp_type = sitk.sitkBSpline
    elif interp_type == 'nearest_neighbor':
        interp_type = sitk.sitkNearestNeighbor
    
    ### interpolate
    resample = sitk.ResampleImageFilter()
    resample.SetOutputSpacing(new_spacing)
    resample.SetSize(new_size)
    resample.SetOutputOrigin(img.GetOrigin())
    resample.SetOutputDirection(img.GetDirection())
    resample.SetInterpolator(interp_type)
    resample.SetDefaultPixelValue(img.GetPixelIDValue())
    resample.SetOutputPixelType(sitk.sitkFloat32)
    img_nrrd = resample.Execute(img) 
    
    return img_nrrd

#--------------------------------------------------------------------------------------
# crop image
#-------------------------------------------------------------------------------------
def crop_image(nrrd_file, crop_shape, clipping=None, scale_size=None, verbose=False, mass_centered=False):
    print_lines = []
    ## load stik and arr
    img_arr = sitk.GetArrayFromImage(nrrd_file)
    if clipping:
        img_arr[img_arr<clipping] = clipping
        img_arr[img_arr>700] = 0
    c, y, x = img_arr.shape
    x_crop, y_crop, c_crop = crop_shape
    
    ## Get center of mass to center the crop in Y plane
    mask_arr = np.copy(img_arr) 
    mask_arr[mask_arr > -500] = 1
    mask_arr[mask_arr <= -500] = 0
    if not mass_centered: mask_arr[mask_arr >= -500] = 1
    centermass = ndimage.measurements.center_of_mass(mask_arr)
    print_lines.append("Center of mass: "+str(centermass))
    startc = int(centermass[0] - c_crop//2)
    starty = int(centermass[1] - y_crop//2)      
    startx = int(centermass[2] - x_crop//2)

    print_lines.append("Startx, y, c: "+str(startx)+" ,"+str(starty)+" ,"+str(startc))
    print_lines.append("Crop Shape: "+str(crop_shape))
    print_lines.append("Cropping image with the following values (c, y, x):")
    print_lines.append(str(startc) + " : "+str(startc + c_crop))
    print_lines.append(str(starty) + " : "+str(starty + y_crop))
    print_lines.append(str(startx) + " : "+str(startx + x_crop))

    # Check for out-of-bound scenarios and apply padding if needed
    pad_c_before = -min(0, startc)
    pad_c_after = max(0, startc + c_crop - c)
    pad_y_before = -min(0, starty)
    pad_y_after = max(0, starty + y_crop - y)
    pad_x_before = -min(0, startx)
    pad_x_after = max(0, startx + x_crop - x)
    
    # Print if padding is applied
    if any([pad_c_before, pad_c_after, pad_y_before, pad_y_after, pad_x_before, pad_x_after]):
        print_lines.append(f"Applying padding. Before: {(pad_c_before, pad_y_before, pad_x_before)}, After: {(pad_c_after, pad_y_after, pad_x_after)}")
    a = (-1000.0)
    # Apply padding
    img_arr_padded = np.pad(
        img_arr, 
        ((pad_c_before, pad_c_after), (pad_y_before, pad_y_after), (pad_x_before, pad_x_after)), 
        'constant', 
        constant_values=((a, a), (a, a), (a, a))
    )
    # Update start indices after padding
    startc += pad_c_before
    starty += pad_y_before
    startx += pad_x_before

    img_crop_arr = img_arr_padded[
        startc:(startc + c_crop),
        starty:(starty + y_crop),
        startx:(startx + x_crop)
    ]

    print_lines.append("Image shape after cropping: "+str(img_crop_arr.shape))
    if scale_size is not None:
        img_crop_arr = scale_image(img_crop_arr=img_crop_arr, scale_size=scale_size)
        print_lines.append("Image shape after scaling: "+str(img_crop_arr.shape))

    img_crop_nrrd = sitk.GetImageFromArray(img_crop_arr)
    img_crop_nrrd.SetSpacing(nrrd_file.GetSpacing())
    img_crop_nrrd.SetOrigin(nrrd_file.GetOrigin())

    for line in print_lines:
        if verbose: print(line)
    
    return img_crop_nrrd
    
def scale_image(img_crop_arr, scale_size):
    # Assuming scale_size is a tuple (new_x, new_y)
    new_size = (img_crop_arr.shape[0], scale_size[0], scale_size[1])
    img_crop_arr_scaled = resize(img_crop_arr, new_size, mode='constant', anti_aliasing=True, preserve_range=True)
    return img_crop_arr_scaled.astype(img_crop_arr.dtype)