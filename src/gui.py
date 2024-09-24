# © 2024 Philipp Kaess. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for more information

import os
from tkinter import filedialog, END
import shutil
from src.processing_logic import process_loop
from src.prediction.prediction_utils import get_device
from src.user_interface.settings_manager import SettingsManager
from src.user_interface.reset_popup import show_reset_popup
from src.user_interface.edit_popup import show_edit_popup
from src.user_interface.provide_popup import show_provide_popup
from src.user_interface.build_gui import build_gui
from src.user_interface.ui_utils import update_start_button, update_reset_button
from src.preprocessing.series_manager import load_and_display_series

class CTScanSeriesPredictionApp:
    def __init__(self, root):
        self.root = root
        self.series_data = []
        self.all_series_data = []
        self.predicted_series = []
        self.is_paused = False
        self.prediction_in_progress = False
        self.index_mapping = {}
        self.directory = None
        self.out_dir = None
        self.device = get_device()
        self.reset_allowed = False

        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.load_settings()
        build_gui(self)

    def open_settings(self): #Called by Settings Button
        """Opens the settings window."""
        if not self.prediction_in_progress:
            prev_txt = self.progress_var.get()
            self.progress_var.set("Please answer the pop-up window.")
            reset_happened = self.settings_manager.open_settings_window(self)
            self.settings = self.settings_manager.load_settings()
            self.update_table_columns()
            self.update_tables()
            if not reset_happened: self.progress_var.set(prev_txt)

    def start_prediction(self): #Called by Start Prediction Button
        """Starts or resumes the prediction process for each series."""
        if self.prediction_in_progress: #User pressed pause button
            #self.start_button.config(text="Resume Prediction")
            update_start_button(self,"Start")
            self.prediction_in_progress = False
            self.is_paused = True
            #self.reset_button.config(state="normal", cursor="hand2")
            update_reset_button(self, "Active")
            prev_txt = self.progress_var.get()
            self.progress_var.set(prev_txt + "   (paused)")
        elif self.is_paused: #User pressed play during pause
            self.is_paused = False
            self.start_prediction()
        else: #Default Case, start process loop
            if len(self.series_data) == 0: return #No series loaded, ignore click
            self.prediction_in_progress = True
            self.provide_button.config(state="disabled", cursor="arrow")
            self.settings_button.config(state="normal", cursor="hand2")
            #self.reset_button.config(state="normal", cursor="hand2")
            update_reset_button(self, "Disabled")
            #self.start_button.config(text="Pause Prediction")
            update_start_button(self,"Pause")
            process_loop(self)
            
    def exit_application(self): #Called by Exit Button
        """Exits the application."""
        self.root.quit()
        self.root.destroy()

    def select_directory(self): #Called by Browse button
        """Opens a file dialog to select a directory and brings focus back to the main window."""
        selected_directory = filedialog.askdirectory()
        if selected_directory:
            self.directory_var.set(selected_directory)
            self.directory = selected_directory
            self.list_series()
        self.root.focus_force()
    
    def update_table_columns(self):
        for row in self.series_table.get_children():
            self.series_table.delete(row)
        columns = [key for key, value in self.settings['series_table_columns'].items() if value]
        self.series_table["columns"] = columns
        for idx, col in enumerate(columns):
            self.series_table.heading(col, text=col)
            self.series_table.column(col, width=20 if idx == 0 else 100)
        
        for row in self.prediction_table.get_children():
            self.prediction_table.delete(row)
        columns = [key for key, value in self.settings['predicted_table_columns'].items() if value]
        self.prediction_table["columns"] = columns
        for idx, col in enumerate(columns):
            self.prediction_table.heading(col, text=col)
            self.prediction_table.column(col, width=20 if idx == 0 else 100)

    def update_tables(self): #Auxiliary Function
        """Update the tables with the latest data."""
        # Clear the series_table
        for item in self.series_table.get_children():
            self.series_table.delete(item)

        if len(self.series_data) != 0:
            series_table_columns = list(self.series_table["columns"])
            filtered_series_data = self.series_data[self.series_data["Selected"]==True]
            filtered_series_data = filtered_series_data[series_table_columns]
            for row in filtered_series_data.itertuples(index=False):
                self.series_table.insert("", END, values=row)

        # Clear the prediction_table
        for item in self.prediction_table.get_children():
            self.prediction_table.delete(item)
        
        if len(self.predicted_series) != 0:
            predicted_table_columns = list(self.prediction_table["columns"])
            filtered_prediction_data = self.predicted_series[predicted_table_columns]
            for row in reversed(list(filtered_prediction_data.itertuples(index=False))):
                self.prediction_table.insert("", END, values=row)

    def list_series(self): #Called by List Series Button
        """List and display series in the selected directory."""
        load_and_display_series(self)

    def reset(self, show_confirm=True): #Called by Reset Button
        """Shows a confirmation popup before resetting progress."""
        if show_confirm and not self.reset_allowed: return
        if self.directory:
            def reset_prediction(reset=True, prev_txt='', delete_files=True):
                if reset:
                    if delete_files and os.path.exists(self.out_dir): shutil.rmtree(self.out_dir)

                    self.series_data = []
                    self.all_series_data = []
                    self.predicted_series = []
                    self.update_tables()
                    self.is_paused = False
                    self.prediction_in_progress = False
                    self.settings_button.config(state="normal", cursor="hand2")
                    #self.reset_button.config(state="normal", cursor="hand2")
                    update_reset_button(self, "Disabled")
                    self.edit_button.config(state="disabled", cursor="arrow")
                    self.provide_button.config(state="disabled", cursor="arrow")
                    self.directory_var.set("")
                    self.directory = None
                    self.out_dir = None
                    self.progress_var.set(f"Prediction progress reset. Select a directory to restart.")
                    update_start_button(self, "Disabled")
                else:
                    self.progress_var.set(prev_txt)
            if show_confirm:
                prev_txt = self.progress_var.get()
                self.progress_var.set("Please answer the pop-up window.")
                show_reset_popup(self.root, reset_prediction, prev_txt=prev_txt)
            else:
                reset_prediction(reset=True, delete_files=False)
        else:
            self.progress_var.set("Please select a directory to start.")

    def update_series_lists(self):
        self.all_series_data.to_csv(os.path.join(self.out_dir, "list_of_series.csv"), index=True)
        self.series_data = self.all_series_data.copy()
        if len(self.predicted_series) != 0:
            predicted_indices = self.predicted_series.index
            self.series_data.drop(predicted_indices, inplace=True)
        
    def open_edit_popup(self): #Called by Edit Button
        """Opens the pop-up for editing series selection."""
        if len(self.all_series_data)!=0:
            show_edit_popup(self)
            self.update_series_lists()
            self.update_tables()

    def open_provide_popup(self):
        show_provide_popup(self)
        self.update_series_lists()
        self.update_tables()
    
