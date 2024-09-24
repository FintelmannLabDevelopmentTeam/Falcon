from tkinter import Toplevel, BooleanVar, Button, Label, Frame, Checkbutton, Scrollbar, VERTICAL, HORIZONTAL, Canvas, BOTH, LEFT, RIGHT, X, Y, BOTTOM
from src.user_interface.ui_utils import get_font_size
def show_edit_popup(app):
    """Displays the Edit Series pop-up window for selecting series to process."""
    root = app.root
    popup = Toplevel(root)
    popup.title("Edit Series to process")
    popup.geometry("800x600")  # Adjust size as needed

    # Keep popup above the main window
    popup.transient(root)  # Set the popup as a child of the main window
    popup.attributes("-topmost", True)  # Keep it on top
    popup.focus_set()   

    # Label at the top
    Label(popup, text="Select DICOM Series to Process:", font=("",get_font_size("xlarge"),"bold")).pack(pady=10)

    # Frame around the scrollable area to make it distinguishable
    outer_frame = Frame(popup, relief="solid", bd=2)  # Add border to distinguish the area
    outer_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    # Create a frame for the scrollable area (canvas + scrollbars)
    scroll_frame = Frame(outer_frame)
    scroll_frame.pack(fill=BOTH, expand=True)

    # Create a canvas to hold the checkboxes and series data
    canvas = Canvas(scroll_frame)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)

    # Add vertical scrollbar
    v_scrollbar = Scrollbar(scroll_frame, orient=VERTICAL, command=canvas.yview)
    v_scrollbar.pack(side=RIGHT, fill=Y)
    canvas.configure(yscrollcommand=v_scrollbar.set)

    # Add a frame to hold the table content inside the canvas
    table_frame = Frame(canvas)
    canvas.create_window((0, 0), window=table_frame, anchor='nw')

    # Add horizontal scrollbar under the canvas (linked to the canvas width)
    h_scrollbar = Scrollbar(outer_frame, orient=HORIZONTAL, command=canvas.xview)
    h_scrollbar.pack(side=BOTTOM, fill=X)
    canvas.configure(xscrollcommand=h_scrollbar.set)

    # List of checkbox variables
    checkbox_vars = []
    columns = [key for key, value in app.settings['series_table_columns'].items() if value]

    # Create the header row
    Label(table_frame, text="Index", font=("",get_font_size("large"),"bold"),width=5).grid(row=0, column=0, columnspan=2)
    for idx, col in enumerate(columns[1:]):
        Label(table_frame, text=col, font=("",get_font_size("large"),"bold"),width=20).grid(row=0, column=idx+2)

    # Add rows with checkboxes and series data
    for row_idx, (_, series) in enumerate(app.all_series_data.iterrows()):
        var = BooleanVar(value=series["Selected"])  # Initialize with the current "selected" status
        checkbox_vars.append(var)

        # Create checkboxes in the first column
        checkbutton = Checkbutton(table_frame, variable=var)
        checkbutton.grid(row=row_idx + 1, column=0)

        # Add the series data in other columns
        for col_idx, col in enumerate(columns):
            Label(table_frame, text=series[col], width=2 if col_idx == 0 else 20).grid(row=row_idx + 1, column=col_idx + 1)

    # Update the canvas scrolling region
    table_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    # Create a frame at the bottom for the Save button
    save_button_frame = Frame(popup)
    save_button_frame.pack(fill=X, pady=10)  # Ensure it's placed below the scrollable area
    Button(save_button_frame, text="Save", command=lambda: save_and_close(checkbox_vars)).pack(side=RIGHT, padx=20, pady=10)

    def save_and_close(checkbox_vars):
        """Saves the selected series and closes the pop-up."""
        selected_vars = [var.get() for var in checkbox_vars]
        app.all_series_data['Selected'] = selected_vars
        popup.destroy()

    popup.grab_set()
    popup.wait_window()


def show_edit_popup_old(app):
    """Displays the Edit Series pop-up window for selecting series to process."""
    root = app.root
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
    columns = [key for key, value in app.settings['series_table_columns'].items() if value]
    Label(table_frame, text="Index", width=5).grid(row=0, column=0, columnspan=2)
    for idx, col in enumerate(columns[1:5]):
        Label(table_frame, text=col, width=20).grid(row=0, column=idx+2)

    # Add rows with checkboxes and series data
    for row_idx, (_,series) in enumerate(app.all_series_data.iterrows()):
        var = BooleanVar(value=series["Selected"])  # Initialize with the current "selected" status
        checkbox_vars.append(var)

        # Create checkboxes in the first column
        checkbutton = Checkbutton(table_frame, variable=var)
        checkbutton.grid(row=row_idx + 1, column=0)

        # Add the series data in other columns
        for col_idx, col in enumerate(columns[:5]):
            Label(table_frame, text=series[col], width=2 if col_idx==0 else 20).grid(row=row_idx + 1, column=col_idx+1)

    # Update the canvas scrolling region
    table_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    # Save button at the bottom
    Button(popup, text="Save", command=lambda: save_and_close(checkbox_vars)).pack(pady=10)

    def save_and_close(checkbox_vars):
        """Saves the selected series and closes the pop-up."""
        selected_vars = [var.get() for var in checkbox_vars]
        app.all_series_data['Selected'] = selected_vars
        popup.destroy()

    popup.grab_set()
    popup.wait_window()

