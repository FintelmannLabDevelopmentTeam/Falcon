import SimpleITK as sitk
import numpy as np
import torch

#Range for the normalization
HN_SLICE_RANGE = range(35,75)
CH_SLICE_RANGE = range(50,80)
AB_SLICE_RANGE = range(20,80)
BP_SLICE_RANGE = range(35,65)

#Index of slice (in range, 0-based) for the actual prediction
BP_SLICE_IDX = 15
HN_SLICE_IDX = 20
CH_SLICE_IDX = 15
AB_SLICE_IDX = 43


def get_body_part_probabilities(model, nrrd_file, device='cpu'):
    img_arr = sitk.GetArrayFromImage(nrrd_file)
    data = img_arr[BP_SLICE_RANGE, :, :]
    
    data = np.clip(data, a_min=-200, a_max=200)
    MAX, MIN = data.max(), data.min()
    data = (data - MIN) / (MAX - MIN)
    data_single_slice = data[BP_SLICE_IDX, :, :]
    data_3ch = np.broadcast_to(data_single_slice[np.newaxis, ...], (3, data_single_slice.shape[0], data_single_slice.shape[1]))
    data_3ch = np.copy(data_3ch)
    img = torch.from_numpy(data_3ch).float().to(device)
    with torch.no_grad():
        output = model(img.unsqueeze(0)).cpu() #add batch dimension
    probabilities = torch.softmax(output, dim=1).squeeze(0) #remove batch dim
    return probabilities.cpu().numpy() # e.g. [10%, 75%, 15%]

def get_contrast_probability(model, img, part, device='cpu'):
    slice_range, slice_idx = get_slices(part)
    img_arr = sitk.GetArrayFromImage(img)
    data = img_arr[slice_range, :, :]
    
    data = np.clip(data, a_min=-200, a_max=200)
    MAX, MIN = data.max(), data.min()
    data = (data - MIN) / (MAX - MIN)
    data_single_slice = data[slice_idx, :, :]
    data_3ch = np.broadcast_to(data_single_slice[np.newaxis, ...], (3, data_single_slice.shape[0], data_single_slice.shape[1]))
    data_3ch = np.copy(data_3ch)
    img = torch.from_numpy(data_3ch).float().to(device)
    with torch.no_grad():
        output = model(img.unsqueeze(0)).cpu() #add batch dimension
    probability = torch.sigmoid(output).squeeze() #remove batch dimension and class dimension
    return probability.cpu().numpy()

def get_slices(part):
    if part == 'HeadNeck': return HN_SLICE_RANGE, HN_SLICE_IDX
    elif part == 'Chest': return CH_SLICE_RANGE, CH_SLICE_IDX
    elif part == 'Abdomen': return AB_SLICE_RANGE, AB_SLICE_IDX
    else: raise Exception("FATAL ERROR: INVALID BODY PART RECIEVED.")