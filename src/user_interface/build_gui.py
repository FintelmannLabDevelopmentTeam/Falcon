from tkinter import Label, Entry, Button, ttk, StringVar, Canvas, font
from src.user_interface.ui_utils import ToolTip, get_font_size, update_start_button, update_reset_button, setup_sorting
from src.user_interface.ui_utils import get_info_icon, get_fintelmann_logo, get_mgh_logo, call_fintelmann_website

def build_gui(app):
    app.root.title("FALCON  -  Fully-automated Labeling of CT Anatomy and IV Contrast")
    app.root.geometry("1200x800")  # Initial window size that fits the content
    root = app.root
    title_frame = ttk.Frame(root)
    title_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(20,20), padx=(20,0))
    title_frame.grid_columnconfigure(1, weight=1) 
    Label(title_frame, text="FALCON", font=("", get_font_size("title"), "bold")).grid(row=0,column=0, sticky="w")
    Label(title_frame, text="  -   Fully-automated Labeling of CT Anatomy and IV Contrast", font=("", get_font_size("huge"), "")).grid(row=0,column=1, sticky="w")
    app.finti_logo = get_fintelmann_logo(width=300)
    app.finti = Label(title_frame, image=app.finti_logo, cursor="hand2")
    app.finti.grid(row=0,column=2, sticky="e")
    app.finti.bind("<Button-1>", lambda event: call_fintelmann_website())

    frame1 = ttk.Frame(root)
    frame1.grid(row=1,column=0, columnspan=3, sticky="ew", padx=(20,0), pady=(0,0))
    Label(frame1, text="Select a directory containing CT scans in DICOM format:").pack(side="left", padx=(0,0))
    app.icon_image = get_info_icon((16,16))
    info_label = Label(frame1, image=app.icon_image)
    info_label.pack(side="left", padx=(0,10))
    ToolTip(info_label, "In this directory, the tool will search for CT series, identified by their Series Instance UID. As long as every series has a unique Series Instance UID DICOM tag and is stored in a distinct series folder, arbitrarily many series are allowed in the directory, with an arbitrary folder structure.")
    app.directory_var = StringVar()
    app.directory_entry = Entry(frame1, textvariable=app.directory_var)
    app.directory_entry.pack(side="left", fill="x", expand=True, padx=(0,20), pady=(0,0))
    Button(frame1, text="Browse", command=app.select_directory, cursor="hand2").pack(side="right", pady=(0,5))

    separator1 = ttk.Separator(root, orient="horizontal")
    separator1.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(30,0), padx=(20,20))

    # Create a frame for progress and table
    progress_frame = ttk.Frame(root)
    progress_frame.grid(row=4, column=0, columnspan=3, sticky='ew', pady=(5,10), padx=(20,20))

    #Reset Button
    app.reset_canvas = Canvas(progress_frame, width=40, height=35, highlightthickness=0)
    app.reset_canvas.pack(side="left", padx=(30, 0))
    app.reset_canvas.bind("<Button-1>", lambda event: app.reset())
    update_reset_button(app,"Disabled")
    ToolTip(app.reset_canvas, "Reset prediction: Empty both tables and delete progress made in this directory")

    #Start Button
    app.start_canvas = Canvas(progress_frame, width=40, height=35, highlightthickness=0)
    app.start_canvas.pack(side="left", padx=(20, 0))
    update_start_button(app,"Disabled")
    ToolTip(app.start_canvas, "Start/pause prediction of unprocessed series")

    separator3 = ttk.Separator(progress_frame, orient="vertical")
    separator3.pack(side="left", fill="y", padx=(30,30), pady=(5,0))

    app.progress_var = StringVar(value="Please select a directory to start.")
    app.progress_label = Label(progress_frame, textvariable=app.progress_var)
    app.progress_label.pack(side="left", padx=(10,0))

    separator2 = ttk.Separator(root, orient="horizontal")
    separator2.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(0,20), padx=(20,20))

    # Create table for DICOM series with a scrollbar
    unprocessed_frame = ttk.Frame(root)
    unprocessed_frame.grid(row=6, column=0, columnspan=2, sticky='w', padx=(20,0))
    Label(unprocessed_frame, text="Unprocessed Series: ").pack(side="left")
    app.unprocessed_label = Label(unprocessed_frame, text="")
    app.unprocessed_label.pack(side="left")

    frame = ttk.Frame(root)
    frame.grid(row=6, column=1, columnspan=2, sticky="e")

    app.provide_button = Button(frame, text="Provide Body-Part Labels", state="disabled", command=app.open_provide_popup, cursor="arrow")
    app.provide_button.pack(side="right", padx=(15,0))

    app.edit_button = Button(frame, text="Edit Selection", state="disabled", command=app.open_edit_popup, cursor="arrow")
    app.edit_button.pack(side="right")

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

    processed_frame = ttk.Frame(root)
    processed_frame.grid(row=8, column=0, columnspan=2, sticky='w', padx=(20,0))
    Label(processed_frame, text="Processed Series: ").pack(side="left")
    app.processed_label = Label(processed_frame, text="")
    app.processed_label.pack(side="left")

    # Scrollbar for prediction_table
    prediction_scrollbar = ttk.Scrollbar(root, orient="vertical")
    columns = [key for key, value in app.settings['predicted_table_columns'].items() if value]
    app.prediction_table = ttk.Treeview(root, columns=columns, show="headings", yscrollcommand=prediction_scrollbar.set)
    app.prediction_table.grid(row=9, column=0, columnspan=3, sticky='nsew', pady=(10,10), padx=(20,0))
    prediction_scrollbar.grid(row=9, column=3, sticky='ns', padx=(0, 20), pady=(10,10))
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

    app.update_table_columns()

    copyright_frame = ttk.Frame(root)
    copyright_frame.grid(row=11, column=0, columnspan=3, padx=(20,0), pady=(0,5), sticky="esw")
    copyright_frame.grid_columnconfigure(1, weight=1) 
    app.settings_button = Button(copyright_frame,text="Settings",command=app.open_settings, cursor="hand2")
    app.settings_button.grid(row=0, column=0, pady=(0,10), sticky="w")
    
    middle_frame = ttk.Frame(copyright_frame)
    middle_frame.grid(row=0, column=1)
    app.mgh_logo = get_mgh_logo(width=50)
    app.mgh = Label(middle_frame, image=app.mgh_logo)
    app.mgh.pack(side="left", padx=(0,20))
    Label(middle_frame, text="© 2024 Philipp Kaess. All rights reserved. Licensed under the MIT License.", 
          font=("",10,"")).pack(side="left")
    

    
    Button(copyright_frame, text="Exit", command=app.exit_application, cursor="hand2").grid(row=0,column=3, sticky="e", pady=(0,10))

    
    
    