import time
from tkinter import Tk, Toplevel, Label, ttk
from src.user_interface.ui_utils import get_fintelmann_logo, get_mgh_logo, get_font_size, get_falcon
VERSION = "v1.0.0"


def show_loading_popup():
    """ Displays a loading popup window """
    loading_window = Toplevel()
    loading_window.geometry("")
    loading_window.title("Loading FALCON")

    Label(loading_window, text="FALCON", font=("", get_font_size("title"), "bold")).grid(row=0,column=0, pady=(10,20))

    falcon_logo = get_falcon(width=400)
    falcon = Label(loading_window, image=falcon_logo)
    falcon.grid(row=1, column=0, padx=30)

    label = Label(loading_window, text="Loading... ", font=("", get_font_size("huge"), "bold"), pady=20)
    label.grid(row=2, column=0)

    logo_frame = ttk.Frame(loading_window)
    logo_frame.grid(row=4, column=0, sticky="ew", pady=(20,10))
    finti_logo = get_fintelmann_logo(width=150)
    finti = Label(logo_frame, image=finti_logo)
    finti.grid(row=0, column=0, sticky="w")
    mgh_logo = get_mgh_logo(width=65)
    mgh = Label(logo_frame, image = mgh_logo)
    mgh.grid(row=0, column=2, sticky="e")
    txt = Label(logo_frame, text=f"© 2024 Philipp Kaess - {VERSION}", font=("", 10, ""))
    txt.grid(row=0, column=1,padx=50)

    loading_window.update()
    loading_window.geometry("")

    return loading_window

if __name__ == "__main__":
    root = Tk()
    root.withdraw()  # Hide the main window initially

    # Show loading window
    loading_popup = show_loading_popup()

    # Delay a bit to simulate loading (if necessary, remove this)
    #time.sleep(5)

    # Now, import the potentially time-consuming module after showing the loading popup
    from src.gui import CTScanSeriesPredictionApp

    # Destroy the loading popup after the import and setup
    loading_popup.destroy()

    # Show the main application
    root.deiconify()  # Show the main window
    app = CTScanSeriesPredictionApp(root, VERSION)
    root.mainloop()
