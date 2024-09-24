from tkinter import Toplevel, Label, Button, Checkbutton, IntVar, DISABLED, NORMAL, Entry, filedialog, font
import pandas as pd
import copy

LABEL_DICT = {0:'HeadNeck', 1:'Chest', 2:'Abdomen'}

def show_provide_popup(app):
    """Displays the Provide Body-Part Labels pop-up window for selecting series to process."""
    # Make a copy of all_series_data so we can revert if "Back" is pressed
    root = app.root
    original_all_series_data = app.all_series_data.copy()

    popup = Toplevel(root)
    popup.title("Provide body-part labels")
    popup.geometry("700x400")  # Adjust size as needed

    # Keep popup above the main window
    popup.transient(root)          
    popup.attributes("-topmost", True)  
    popup.focus_set()   
    popup.grab_set()
    Label(popup, text="Please select one of the following options to provide body-part labels:", font=("",18,"bold")).grid(row=0, 
                                                                            column=0, columnspan=2, padx=10, pady=10)
    
    # Create IntVar for checkboxes, only one can be selected at a time
    selection_var = IntVar()

    # Option 1: All series are head-neck CTs
    head_neck_checkbox = Checkbutton(popup, text="All series are head-neck CTs", variable=selection_var, onvalue=1, offvalue=0)
    head_neck_checkbox.grid(row=1, column=0, sticky='w', padx=10, pady=5)

    # Option 2: All series are chest CTs
    chest_checkbox = Checkbutton(popup, text="All series are chest CTs", variable=selection_var, onvalue=2, offvalue=0)
    chest_checkbox.grid(row=2, column=0, sticky='w', padx=10, pady=5)

    # Option 3: All series are abdomen CTs
    abdomen_checkbox = Checkbutton(popup, text="All series are abdomen CTs", variable=selection_var, onvalue=3, offvalue=0)
    abdomen_checkbox.grid(row=3, column=0, sticky='w', padx=10, pady=5)

    #spacing
    Label(popup, text="").grid(row=4, column=0, columnspan=3, padx=10, pady=10)
    # Option 4: Load body-part labels from CSV
    csv_checkbox = Checkbutton(popup, text="Load body-part labels from CSV", variable=selection_var, onvalue=4, offvalue=0)
    csv_checkbox.grid(row=5, column=0, sticky='w', padx=10, pady=5)

    # Button to select CSV (initially disabled)
    select_csv_button = Button(popup, text="Select label CSV", state=DISABLED, command=lambda: select_csv_path(csv_path_entry, popup))
    select_csv_button.grid(row=6, column=1, padx=10, pady=10)

    # Text field to display the selected CSV path
    csv_path_entry = Entry(popup, width=30)
    csv_path_entry.grid(row=6, column=0, padx=10, pady=10)

    # Load Labels button (initially disabled)
    #load_labels_button = Button(popup, text="Load Labels", state=DISABLED, command=lambda: load_labels(csv_path_entry.get(), all_series_data, result_label))
    #load_labels_button.grid(row=6, column=2, padx=10, pady=10)

    # Label to display the result (how many labels were found)
    result_label = Label(popup, text="")
    result_label.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

    # Back button
    back_button = Button(popup, text="Back", state=NORMAL, command=lambda: abort_provide(original_all_series_data))
    back_button.grid(row=9, column=0, padx=10, pady=10)

    # Save button (initially disabled until changes are made)
    save_button = Button(popup, text="Save", state=DISABLED, command=lambda: save_changes(selection_var.get(), app, popup))
    save_button.grid(row=9, column=1, padx=10, pady=10)

    # Function to handle enabling/disabling of the CSV and Load Labels buttons
    def update_button_states():
        if selection_var.get() == 4:
            select_csv_button.config(state=NORMAL)
            #load_labels_button.config(state=DISABLED)
            save_button.config(state=DISABLED)
        else:
            select_csv_button.config(state=DISABLED)
            #load_labels_button.config(state=DISABLED)
            save_button.config(state=NORMAL)  # Enable save for uniform labels

    # Function to open file dialog and select CSV path
    def select_csv_path(entry, root):
        csv_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if csv_path:
            entry.delete(0, 'end')
            entry.insert(0, csv_path)
            #load_labels_button.config(state=NORMAL)  # Enable the "Load Labels" button
        root.focus_force()
        load_labels(csv_path, app, result_label)

    # Trace the selection variable to monitor changes and update the state of buttons
    selection_var.trace("w", lambda *args: update_button_states())

    def abort_provide(original_data):
        """Revert all changes and close the popup."""
        # Restore the original DataFrame
        app.all_series_data = original_data.copy()
        popup.destroy()

    def load_labels(csv_path, app, result_label):
        """Loads body-part labels from the CSV and updates all_series_data."""
        num_found = get_bp_labels_from_csv(csv_path, app)
        total_series = len(app.all_series_data)
        
        # Update the result label with the count of found labels
        result_label.config(text=f"For {num_found} of {total_series} series, labels have been found in the CSV.")
        
        # Enable the save button after loading labels
        save_button.config(state=NORMAL)
        #load_labels_button.config(state=DISABLED)
        # Keep the popup running until the user closes it
    popup.wait_window()

def save_changes(selection, app, popup):
    """Apply changes to all_series_data (list of lists) and close the popup."""
    if selection in [1,2,3]:
        app.all_series_data["Body Part Label"] = LABEL_DICT[selection-1]
    #else the changes from the csv are already in the df, so no change needed
    # Close the popup after saving
    popup.destroy()


def get_bp_labels_from_csv(csv_path, app):
    """Updates all_series_data DataFrame with labels from the provided CSV based on Series UID."""
    try:
        label_df = pd.read_csv(csv_path)

        # Check if the CSV contains the necessary columns
        if 'Series Instance UID' not in label_df.columns or 'Body Part Label' not in label_df.columns:
            print("CSV does not contain all required columns (Series Instance UID and Body Part Label).")
            return 0

        # Filter out rows that don't have the required body part labels
        label_df = label_df[label_df['Body Part Label'].isin(["Chest", "HeadNeck", "Abdomen"])]

        # Check for duplicates in Series Instance UID in label_df
        if label_df.duplicated(subset=['Series Instance UID']).any():
            print("Warning: Duplicate Series Instance UID found in label_df. Removing duplicates.")
            label_df = label_df.drop_duplicates(subset=['Series Instance UID'])

        app.all_series_data['Body Part Label'] = ""
        original_index = app.all_series_data.index #save index to avoid index confusion after matching

        matched_df = pd.merge(app.all_series_data, label_df[['Series Instance UID', 'Body Part Label']], 
                              on='Series Instance UID', how='left', suffixes=('', '_label_df'))

        matched_df.index = original_index #Restore original index
        app.all_series_data['Body Part Label'] = matched_df['Body Part Label_label_df'].fillna(" ")
        unique_matches_count = (app.all_series_data['Body Part Label'] != " ").sum()

    except Exception as e:
        print(f"Error loading labels from CSV: {e}")
        return 0

    return unique_matches_count
