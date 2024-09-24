from tkinter import Toplevel, Label, Button

def show_finished_popup(app):
    """Shows a confirmation popup before resetting the prediction."""
    root = app.root
    popup = Toplevel(root)
    popup.title("Prediction complete")
    popup.geometry("400x150")
    popup.resizable(False, False)

    # Keep popup above the main window
    popup.transient(root)          # Set the popup as a child of the main window
    popup.attributes("-topmost", True)  # Keep it on top
    popup.focus_set()   

    # Confirmation message
    Label(popup, text="Prediction complete. The resulting csv containing the").pack(pady=(20,0))
    Label(popup, text=f"detailed prediction result is stored in {app.settings['output_folder']}/predictions.csv").pack(pady=0)

    # 'Reset' button - call the reset callback function
    def confirm():
        popup.destroy()  # Close the popup
        

    # 'Back' button - simply close the popup
    Button(popup, text="OK", command=confirm).pack(side="bottom", padx=50, pady=20)

    popup.grab_set()
    popup.wait_window()