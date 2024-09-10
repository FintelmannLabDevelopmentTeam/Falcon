import SimpleITK as sitk
import numpy as np
import torch

BODY_PART_SLICE_IDX = 10
BODY_PART_SLICE_RANGE = range(40,60) #TODO: Adjust! ######################################


def get_body_part(model, nrrd_file, device='cpu'):
    img_arr = sitk.GetArrayFromImage(nrrd_file)
    data = img_arr[BODY_PART_SLICE_RANGE, :, :]
    
    data = np.clip(data, a_min=-200, a_max=200)
    MAX, MIN = data.max(), data.min()
    data = (data - MIN) / (MAX - MIN)
    data_single_slice = data[BODY_PART_SLICE_IDX, :, :]
    data_3ch = np.broadcast_to(data_single_slice[np.newaxis, ...], (3, data_single_slice.shape[0], data_single_slice.shape[1]))
    data_3ch = np.copy(data_3ch)
    img = torch.from_numpy(data_3ch).float().to(device)
    with torch.no_grad():
        output = model(img.unsqueeze(0)).cpu() #add batch dimension
    probabilities = torch.softmax(output, dim=1).squeeze(0) #remove batch dim
    return probabilities.cpu().numpy() # e.g. [10%, 75%, 15%]
    
