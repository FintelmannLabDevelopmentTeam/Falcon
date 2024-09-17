from tkinter import Toplevel, BooleanVar, Button, Label, Frame, Checkbutton, Scrollbar, VERTICAL, Canvas, BOTH, LEFT, RIGHT, Y

def show_edit_popup(root, all_series_data):
    """Displays the Edit Series pop-up window for selecting series to process."""
    popup = Toplevel(root)
    popup.title("Edit Series to process")
    popup.geometry("800x600")  # Adjust size as needed

    # Keep popup above the main window
    popup.transient(root)          # Set the popup as a child of the main window
    popup.attributes("-topmost", True)  # Keep it on top
    popup.focus_set()   

    # Label at the top
    Label(popup, text="Select Series to Process:").pack(pady=10)

    # Create a canvas to hold the checkboxes and series data
    canvas = Canvas(popup)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)

    # Add a scrollbar
    scrollbar = Scrollbar(popup, orient=VERTICAL, command=canvas.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Create a frame to hold the table
    table_frame = Frame(canvas)
    canvas.create_window((0, 0), window=table_frame, anchor='nw')

    # List of checkbox variables
    checkbox_vars = []

    # Add a label row for the headers
    Label(table_frame, text="Select", width=10).grid(row=0, column=0)
    Label(table_frame, text="Index", width=10).grid(row=0, column=1)
    Label(table_frame, text="Patient", width=20).grid(row=0, column=2)
    Label(table_frame, text="Study", width=20).grid(row=0, column=3)
    Label(table_frame, text="Series", width=20).grid(row=0, column=4)
    Label(table_frame, text="DCM Files", width=10).grid(row=0, column=5)

    # Add rows with checkboxes and series data
    for idx, series in enumerate(all_series_data):
        var = BooleanVar(value=series[-1])  # Initialize with the current "selected" status
        checkbox_vars.append(var)

        # Create checkboxes in the first column
        checkbutton = Checkbutton(table_frame, variable=var)
        checkbutton.grid(row=idx + 1, column=0, sticky='w')

        # Add the series data in other columns
        Label(table_frame, text=series[0], width=10).grid(row=idx + 1, column=1)
        Label(table_frame, text=series[1], width=20).grid(row=idx + 1, column=2)
        Label(table_frame, text=series[2], width=20).grid(row=idx + 1, column=3)
        Label(table_frame, text=series[3], width=20).grid(row=idx + 1, column=4)
        Label(table_frame, text=series[4], width=10).grid(row=idx + 1, column=5)

    # Update the canvas scrolling region
    table_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    # Save button at the bottom
    Button(popup, text="Save", command=lambda: save_and_close(checkbox_vars)).pack(pady=10)

    def save_and_close(checkbox_vars):
        """Saves the selected series and closes the pop-up."""
        for i, var in enumerate(checkbox_vars):
            all_series_data[i][-1] = var.get()  # Update the 'selected' status
        popup.destroy()

    popup.grab_set()
    popup.wait_window()

