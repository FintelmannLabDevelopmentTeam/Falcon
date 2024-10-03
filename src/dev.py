import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
from pydicom import dcmread
from scipy import stats

def get_dicom_metadata(dicom_file):
    try:
        ds = dcmread(dicom_file)
        metadata = {
            'Manufacturer': ds.get('Manufacturer', 'NA'),
            'ModelName': ds.get('ManufacturerModelName', 'NA'),
            'PixelSpacing': ds.get('PixelSpacing', [None, None])[0],  # Assuming row spacing
            'SliceThickness': ds.get('SliceThickness', None),
            'KVP': ds.get('KVP', None),
            'Rows': ds.Rows if hasattr(ds, 'Rows') else None,
            'Columns': ds.Columns if hasattr(ds, 'Columns') else None,
        }
        return metadata
    except Exception as e:
        print(f"Error reading DICOM file {dicom_file}: {e}")
        return None

def traverse_directory(dicom_dir):
    all_metadata = []
    for root, _, files in os.walk(dicom_dir):
        dicom_files = [f for f in files if f.lower().endswith('.dcm')]
        if len(dicom_files) > 10:  # Series with more than 10 slices
            first_slice = dicom_files[0]  # Use only the first slice
            metadata = get_dicom_metadata(os.path.join(root, first_slice))
            if metadata:
                all_metadata.append({
                    'num_slices': len(dicom_files),
                    'manufacturer': metadata['Manufacturer'],
                    'model': metadata['ModelName'],
                    'pixel_spacing': metadata['PixelSpacing'],
                    'slice_thickness': metadata['SliceThickness'],
                    'kvp': metadata['KVP'],
                    'resolution': (metadata['Rows'], metadata['Columns'])  # Tuple of Rows x Columns
                })
    return all_metadata

def calculate_statistics(series_data, attribute_name):
    valid_values = [s[attribute_name] for s in series_data if s[attribute_name] is not None]
    invalid_count = len(series_data) - len(valid_values)
    if len(valid_values) == 0:
        return {
            'mean': None,
            'median': None,
            'mode': None,
            'range': None,
            'std_dev': None,
            'invalid_count': invalid_count,
            'invalid_percent': (invalid_count / len(series_data)) * 100 if len(series_data) > 0 else 0
        }
    return {
        'mean': np.mean(valid_values),
        'median': np.median(valid_values),
        'mode': stats.mode(valid_values)[0][0] if len(valid_values) > 0 else None,
        'range': (np.min(valid_values), np.max(valid_values)),
        'std_dev': np.std(valid_values),
        'invalid_count': invalid_count,
        'invalid_percent': (invalid_count / len(series_data)) * 100
    }

def print_statistics(statistics, attribute_name):
    print(f"--- {attribute_name} ---")
    print(f"Mean: {statistics['mean']}")
    print(f"Median: {statistics['median']}")
    print(f"Mode: {statistics['mode']}")
    print(f"Range: {statistics['range']}")
    print(f"Standard Deviation: {statistics['std_dev']}")
    print(f"Invalid/Missing: {statistics['invalid_count']} ({statistics['invalid_percent']}%)")
    print("")

def plot_histogram(series_data, attribute_name, bin_size=10):
    num_slices = [s[attribute_name] for s in series_data]
    plt.hist(num_slices, bins=range(0, max(num_slices) + bin_size, bin_size), edgecolor='black')
    plt.title(f'Number of {attribute_name.capitalize()} per Series')
    plt.xlabel(f'Number of {attribute_name.capitalize()} (bin size = {bin_size})')
    plt.ylabel('Number of Series')
    plt.show()

def plot_resolution_histogram(series_data):
    # Separate valid and invalid resolutions
    valid_resolutions = [f'{s["resolution"][0]}x{s["resolution"][1]}' for s in series_data 
                         if s['resolution'][0] is not None and s['resolution'][1] is not None]
    invalid_count = len([s for s in series_data if s['resolution'][0] is None or s['resolution'][1] is None])

    # Count the occurrences of each resolution
    resolution_counts = Counter(valid_resolutions)
    total_series = len(series_data)

    # Print the counts and ratios in the terminal
    print("--- Resolution (Rows x Columns) Histogram ---")
    for resolution, count in resolution_counts.items():
        ratio = count / total_series * 100
        print(f"{resolution}: {count} series ({ratio:.2f}%)")

    if invalid_count > 0:
        invalid_ratio = invalid_count / total_series * 100
        print(f"Invalid/Missing resolutions: {invalid_count} series ({invalid_ratio:.2f}%)")
    
    # Plot the bar chart for valid resolutions
    plt.bar(resolution_counts.keys(), resolution_counts.values(), edgecolor='black')
    plt.title('Resolution (Rows x Columns) of Scans')
    plt.xlabel('Resolution (Rows x Columns)')
    plt.ylabel('Number of Series')
    plt.xticks(rotation=45, ha="right")
    plt.show()


def count_non_numeric(series_data, attribute_name):
    count = Counter([s[attribute_name] for s in series_data if s[attribute_name] != 'NA'])
    return count

def print_non_numeric_counts(non_numeric_counts, attribute_name):
    print(f"--- {attribute_name} ---")
    for key, count in non_numeric_counts.items():
        print(f"{key}: {count}")
    print("")

def main(dicom_dir):
    # Traverse DICOM directory and collect metadata
    series_data = traverse_directory(dicom_dir)
    
    if not series_data:
        print("No series with more than 10 slices found.")
        return
    
    # Count series with more than 10 slices
    print(f"Number of series with more than 10 slices: {len(series_data)}")

    # Numeric statistics
    num_slices_stats = calculate_statistics(series_data, 'num_slices')
    slice_thickness_stats = calculate_statistics(series_data, 'slice_thickness')
    pixel_spacing_stats = calculate_statistics(series_data, 'pixel_spacing')
    kvp_stats = calculate_statistics(series_data, 'kvp')

    # Print numeric statistics
    print_statistics(num_slices_stats, 'Number of Slices')
    print_statistics(slice_thickness_stats, 'Slice Thickness')
    print_statistics(pixel_spacing_stats, 'Pixel Spacing')
    print_statistics(kvp_stats, 'Tube Voltage (kVp)')

    # Plot histogram for number of slices per series
    plot_histogram(series_data, 'num_slices')

    # Plot histogram for resolution (Rows x Columns)
    plot_resolution_histogram(series_data)

    # Non-numeric statistics
    manufacturer_model_counts = count_non_numeric(series_data, 'manufacturer')
    print_non_numeric_counts(manufacturer_model_counts, 'Manufacturer and Model')

if __name__ == "__main__":
    dicom_dir = input("Enter the path to the DICOM directory: ")
    main(dicom_dir)
