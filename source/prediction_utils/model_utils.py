from PrivateModelArchitectures.classification import ResNet9
import torch

BODY_PART_MODEL_PATH = ''
ABDOMEN_MODEL_PATH = ''
CHEST_MODEL_PATH = ''
HN_MODEL_PATH = ''

def load_model(mode, device='cpu'):
    model = ResNet9(in_channels=3, num_classes=1, act_func=torch.nn.Sigmoid, scale_norm=True, norm_layer='group')
    # Load the original state dict with the '_module' prefix
    if mode == 'body_part': model_path = BODY_PART_MODEL_PATH
    elif mode == 'abdomen': model_path = ABDOMEN_MODEL_PATH
    elif mode == 'chest': model_path = CHEST_MODEL_PATH
    elif mode == 'head_neck': model_path = HN_MODEL_PATH
    else: raise Exception ("Invalid mode in model loading.")
    original_state_dict = torch.load(model_path, map_location=device, weights_only=True)
    # Adjust the state dict by removing the '_module' prefix
    adjusted_state_dict = remove_module_prefix(original_state_dict)
    # Now load the adjusted state dict into your model
    model.load_state_dict(adjusted_state_dict)
    model.to(device)
    model.eval()
    return model

def remove_module_prefix(state_dict):
    """Remove the '_module.' prefix from each key in the state dictionary."""
    new_state_dict = {}
    for k, v in state_dict.items():
        name = k[8:] if k.startswith('_module.') else k  # Remove '_module.' prefix
        new_state_dict[name] = v
    return new_state_dict

def get_device():
    return 'cuda:0' if torch.cuda.is_available() else 'cpu'