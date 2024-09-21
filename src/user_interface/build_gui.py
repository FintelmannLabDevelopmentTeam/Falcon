from tkinter import Label, Entry, Button, ttk, StringVar, Canvas
from src.user_interface.ui_utils import ToolTip, update_start_button, update_reset_button

def build_gui(app):
    app.root.title("CT Scan Series Prediction")
    app.root.geometry("1100x800")  # Initial window size that fits the content
    root = app.root

    Label(root, text="Select a directory containing patient folders:").grid(row=0, column=0, sticky='w', padx=(20,0), pady=(20,0))
    app.directory_var = StringVar()
    app.directory_var.set(app.settings.get("last_directory", ""))
    app.directory_entry = Entry(root, textvariable=app.directory_var, width=50)
    app.directory_entry.grid(row=0, column=1, sticky='ew', pady=(20,0))
    Button(root, text="Browse", command=app.select_directory).grid(row=0, column=2, sticky='w', padx=(20,20), pady=(20,0))

    Label(root, text="Enter minimum number of .dcm files to include a series:").grid(row=1, column=0, sticky='w', padx=(20,0))
    app.min_dcm_var = StringVar(value='20')
    app.min_dcm_entry = Entry(root, textvariable=app.min_dcm_var, width=10)
    app.min_dcm_entry.grid(row=1, column=1, sticky='w')
    Button(root, text="List Series", command=app.list_series).grid(row=1, column=2, sticky='w')

    s = 3

    button_frame = ttk.Frame(root)
    button_frame.grid(row=2, column=0, columnspan=3, sticky='ew', pady=20, padx=(20,0))
    #Button(button_frame, text="List Series", command=app.list_series).pack(side="left", padx=(10*s,10*s))

    #Reset Button
    app.reset_canvas = Canvas(button_frame, width=40, height=40, highlightthickness=0)
    app.reset_canvas.pack(side="left", padx=(10 * s, 0))
    app.reset_canvas.bind("<Button-1>", lambda event: app.reset())
    update_reset_button(app,"Disabled")

    #Start Button
    app.start_canvas = Canvas(button_frame, width=40, height=40, highlightthickness=0)
    app.start_canvas.pack(side="left", padx=(1 * s, 0))
    update_start_button(app,"Start")

    app.settings_button = Button(button_frame, text="Settings", command=app.open_settings)
    app.settings_button.pack(side="left", padx=(50*s, 50*s))
    app.settings_button.config(state="normal")

    Button(button_frame, text="Exit", command=app.exit_application).pack(side="left", padx=(10*s, 10*s))

    separator1 = ttk.Separator(root, orient="horizontal")
    separator1.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(20,0), padx=(20,20))

    # Create a frame for progress and table
    progress_frame = ttk.Frame(root)
    progress_frame.grid(row=4, column=0, columnspan=3, sticky='ew', pady=(5,10), padx=(20,20))
    Label(progress_frame, text="Progress:").pack(side="left")
    app.progress_var = StringVar()
    app.progress_label = Label(progress_frame, textvariable=app.progress_var)
    app.progress_label.pack(side="left")

    separator2 = ttk.Separator(root, orient="horizontal")
    separator2.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(0,20), padx=(20,20))

    # Create table for DICOM series with a scrollbar
    Label(root, text="Unprocessed Series:").grid(row=6, column=0, sticky='w', padx=(20,0))

    # Edit button, initially disabled
    app.edit_button = Button(root, text="Edit", state="disabled", command=app.open_edit_popup)
    app.edit_button.grid(row=6, column=1, sticky='w', padx=(10, 0))

    # Provide Labels button, initially disabled
    app.provide_button = Button(root, text="Provide Body-Part Labels", state="disabled", command=app.open_provide_popup)
    app.provide_button.grid(row=6, column=2, sticky='w', padx=(10, 0))

    # Scrollbar for series_table
    series_scrollbar = ttk.Scrollbar(root, orient="vertical")
    columns = [key for key, value in app.settings['series_table_columns'].items() if value]
    app.series_table = ttk.Treeview(root, columns=columns, show="headings", yscrollcommand=series_scrollbar.set)
    app.series_table.grid(row=7, column=0, columnspan=3, sticky='nsew', pady=(10,30), padx=(20,0))
    series_scrollbar.grid(row=7, column=3, sticky='ns', padx=(0, 20), pady=(10,30))
    series_scrollbar.config(command=app.series_table.yview)

    for idx, col in enumerate(app.series_table["columns"]):
        app.series_table.heading(col, text=col)
        app.series_table.column(col, width=20 if idx==0 else 100)

    Label(root, text="Processed Series:").grid(row=8, column=0, sticky='w', padx=(20,0))

    # Scrollbar for prediction_table
    prediction_scrollbar = ttk.Scrollbar(root, orient="vertical")
    columns = [key for key, value in app.settings['predicted_table_columns'].items() if value]
    app.prediction_table = ttk.Treeview(root, columns=columns, show="headings", yscrollcommand=prediction_scrollbar.set)
    app.prediction_table.grid(row=9, column=0, columnspan=3, sticky='nsew', pady=(10,20), padx=(20,0))
    prediction_scrollbar.grid(row=9, column=3, sticky='ns', padx=(0, 20), pady=(10,20))
    prediction_scrollbar.config(command=app.prediction_table.yview)

    #col_widths = [30, 130, 130, 130, 100, 100, 100, 100]
    for idx, col in enumerate(app.prediction_table["columns"]):
        app.prediction_table.heading(col, text=col)
        app.prediction_table.column(col, width=20 if idx==0 else 100)

    # Configure resizing behavior for rows and columns
    app.root.grid_columnconfigure(1, weight=1)
    app.root.grid_columnconfigure(0, weight=1)
    app.root.grid_rowconfigure(7, weight=1)  # Unprocessed series table expands vertically
    app.root.grid_rowconfigure(9, weight=1)  # Processed series table expands vertically