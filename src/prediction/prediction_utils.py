from PrivateModelArchitectures.classification import ResNet9
import torch
import os
import csv

# Get the path to source
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Define relative model paths
BODY_PART_MODEL_PATH = os.path.join(BASE_DIR, "prediction", "models", "body_part_model.pth")
ABDOMEN_MODEL_PATH = os.path.join(BASE_DIR, "prediction", "models", "abdomen_model.pth")
CHEST_MODEL_PATH = os.path.join(BASE_DIR, "prediction", "models", "chest_model.pth")
HN_MODEL_PATH = os.path.join(BASE_DIR, "prediction", "models", "headneck_model.pth")


def load_models(device='cpu'):
    part_model = ResNet9(in_channels=3, num_classes=3, act_func=torch.nn.Sigmoid, scale_norm=True, norm_layer='group')
    hn_model = ResNet9(in_channels=3, num_classes=1, act_func=torch.nn.Sigmoid, scale_norm=True, norm_layer='group')
    ch_model = ResNet9(in_channels=3, num_classes=1, act_func=torch.nn.Sigmoid, scale_norm=True, norm_layer='group')
    ab_model = ResNet9(in_channels=3, num_classes=1, act_func=torch.nn.Sigmoid, scale_norm=True, norm_layer='group')
    
    part_original_state_dict = torch.load(BODY_PART_MODEL_PATH, map_location=device, weights_only=True)
    part_adjusted_state_dict = remove_module_prefix(part_original_state_dict)
    part_model.load_state_dict(part_adjusted_state_dict)
    part_model.to(device)
    part_model.eval()

    hn_original_state_dict = torch.load(HN_MODEL_PATH, map_location=device, weights_only=True)
    hn_adjusted_state_dict = remove_module_prefix(hn_original_state_dict)
    hn_model.load_state_dict(hn_adjusted_state_dict)
    hn_model.to(device)
    hn_model.eval()

    ch_original_state_dict = torch.load(CHEST_MODEL_PATH, map_location=device, weights_only=True)
    ch_adjusted_state_dict = remove_module_prefix(ch_original_state_dict)
    ch_model.load_state_dict(ch_adjusted_state_dict)
    ch_model.to(device)
    ch_model.eval()

    ab_original_state_dict = torch.load(ABDOMEN_MODEL_PATH, map_location=device, weights_only=True)
    ab_adjusted_state_dict = remove_module_prefix(ab_original_state_dict)
    ab_model.load_state_dict(ab_adjusted_state_dict)
    ab_model.to(device)
    ab_model.eval()


    return part_model, hn_model, ch_model, ab_model

def remove_module_prefix(state_dict):
    """Remove the '_module.' prefix from each key in the state dictionary."""
    new_state_dict = {}
    for k, v in state_dict.items():
        name = k[8:] if k.startswith('_module.') else k  # Remove '_module.' prefix
        new_state_dict[name] = v
    return new_state_dict

def get_device():
    return 'cuda:0' if torch.cuda.is_available() else 'cpu'

def save_predictions_to_csv(predicted_series, directory):
    """Saves the prediction results to a CSV file."""
    csv_file = os.path.join(directory, "predictions.csv")
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Index", "Patient", "Study", "Series", "Body Part", "Body Part Confidence", "Contrast", "Contrast Confidence"])
        writer.writerows(predicted_series)