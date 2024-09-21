import os
from tkinter import filedialog, END
from src.processing_logic import process_loop
from src.prediction.prediction_utils import get_device
from src.user_interface.settings_manager import SettingsManager
from src.user_interface.reset_popup import show_reset_popup
from src.user_interface.edit_popup import show_edit_popup
from src.user_interface.provide_popup import show_provide_popup
from src.user_interface.build_gui import build_gui
from src.preprocessing.series_manager import load_and_display_series, save_series_list_to_csv

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
        self.device = get_device()

        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.load_settings()
        build_gui(self)

    def open_settings(self): #Called by Settings Button
        """Opens the settings window."""
        if not self.prediction_in_progress:
            prev_txt = self.progress_var.get()
            self.progress_var.set("Please answer the pop-up window.")
            self.settings_manager.open_settings_window(self.root)
            self.settings = self.settings_manager.load_settings()
            self.progress_var.set(prev_txt)

    def start_prediction(self): #Called by Start Prediction Button
        """Starts or resumes the prediction process for each series."""
        if self.prediction_in_progress:
            self.start_button.config(text="Resume Prediction")
            self.prediction_in_progress = False
            self.is_paused = True
            self.reset_button.config(state="normal")
        elif self.is_paused:
            self.is_paused = False
            self.start_prediction()
        else:
            self.prediction_in_progress = True
            self.provide_button.config(state='disabled')
            self.settings_button.config(state="disabled")
            self.reset_button.config(state="disabled")
            self.start_button.config(text="Pause Prediction")
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
            self.settings["last_directory"] = selected_directory
            self.settings_manager.save_settings(self.settings)
        self.root.focus_force()


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
            for row in filtered_prediction_data.itertuples(index=False):
                self.prediction_table.insert("", END, values=row)

    def list_series(self): #Called by List Series Button
        """List and display series in the selected directory."""
        load_and_display_series(self)

    def reset(self): #Called by Reset Button
        """Shows a confirmation popup before resetting progress."""
        if self.directory:
            def reset_prediction(reset=True, prev_txt=''):
                if reset:
                    series_csv = os.path.join(self.directory, "list_of_series.csv")
                    prediction_csv = os.path.join(self.directory, "predictions.csv")
                    if os.path.exists(series_csv):
                        os.remove(series_csv)
                    if os.path.exists(prediction_csv):
                        os.remove(prediction_csv)

                    preprocessed_dir = os.path.join(os.path.join(self.directory, "preprocessed"))
                    if os.path.exists(preprocessed_dir):
                        for root, dirs, files in os.walk(preprocessed_dir):
                            for file in files:
                                os.remove(os.path.join(root, file))
                        os.rmdir(preprocessed_dir)

                    self.series_data = []
                    self.all_series_data = []
                    self.predicted_series = []
                    self.update_tables()
                    self.is_paused = False
                    self.prediction_in_progress = False
                    self.settings_button.config(state="normal")
                    self.reset_button.config(state="disabled")
                    self.edit_button.config(state="disabled")
                    self.provide_button.config(state="disabled")
                    self.start_button.config(text="Start Prediction")

                    self.progress_var.set(f"Prediction progress reset. List Series to restart.")
                else:
                    self.progress_var.set(prev_txt)

            prev_txt = self.progress_var.get()
            self.progress_var.set("Please answer the pop-up window.")
            show_reset_popup(self.root, reset_prediction, prev_txt=prev_txt)

    def update_series_lists(self):
        self.all_series_data.to_csv(os.path.join(self.directory, "list_of_series.csv"), index=True)
        self.series_data = self.all_series_data.copy()
        if len(self.predicted_series) != 0:
            predicted_indices = self.predicted_series.index
            print(f"Removing indices {predicted_indices}")
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
    
