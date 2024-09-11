from tkinter import Toplevel, Label, Button

def show_reset_popup(root, on_reset_callback, prev_txt):
    """Shows a confirmation popup before resetting the prediction."""
    popup = Toplevel(root)
    popup.title("Confirm Reset")
    popup.geometry("400x150")
    popup.resizable(False, False)

    # Keep popup above the main window
    popup.transient(root)          # Set the popup as a child of the main window
    popup.attributes("-topmost", True)  # Keep it on top
    popup.focus_set()   

    # Confirmation message
    Label(popup, text="Are you sure? Resetting will delete all preprocessing").pack(pady=0)
    Label(popup, text="and prediction progress in the current working directory.").pack(pady=0)

    # 'Reset' button - call the reset callback function
    def confirm_reset():
        popup.destroy()  # Close the popup
        on_reset_callback(reset=True, prev_txt=prev_txt)  # Call the reset function
    
    def abort_reset():
        popup.destroy()
        on_reset_callback(reset=False, prev_txt=prev_txt)
        

    # 'Back' button - simply close the popup
    Button(popup, text="Back", command=abort_reset).pack(side="left", padx=50, pady=20)
    
    # 'Reset' button
    Button(popup, text="Reset", command=confirm_reset).pack(side="right", padx=50, pady=20)
    popup.grab_set()
    popup.wait_window()

