import tkinter as tk
from PIL import Image, ImageTk

class ToolTip:
    """Creates a tooltip for a given widget."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        """Display the tooltip window near the widget."""
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip_window, text=self.text, relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event=None):
        """Hide the tooltip window."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


def resize_image(path, size):
    image = Image.open(path)
    try:
        image = image.resize(size, Image.LANCZOS)
    except: #newer version of PIL
        try:
            from PIL import ImageResampling
            image = image.resize(size, ImageResampling.LANCZOS)
        except:
            print("Resizing icons failed!")
    return ImageTk.PhotoImage(image)

def get_info_icon(size=(16,16)):
    return resize_image("/Users/philipp/prediction_gui/src/icons/info.png", size)

def get_start_icon (size=(16,16)):
    return resize_image("/Users/philipp/prediction_gui/src/icons/start.png", size)

def update_start_button(app, mode="Start"):
    app.start_canvas.delete("all")
    try: app.start_canvas.unbind("<Button-1>")
    except: pass
    try: app.start_canvas.tag_unbind(triangle, "<Button-1>")
    except: pass
    if mode == "Start":
        triangle = app.start_canvas.create_polygon(5, 5, 5, 35, 32, 20, fill="green", outline="")
        app.start_canvas.tag_bind(triangle, "<Button-1>", lambda event: app.start_prediction())
    elif mode == "Pause":
        left_bar = app.start_canvas.create_rectangle(10, 5, 18, 35, fill="black", outline="")
        right_bar = app.start_canvas.create_rectangle(22, 5, 30, 35, fill="black", outline="")
        app.start_canvas.bind("<Button-1>", lambda event: app.start_prediction())
    else: raise Exception("INVALID MODE PASSED TO UPDATE_START_BUTTON!")
    app.root.update()

def update_reset_button(app, mode="Active"):
    app.reset_canvas.delete("all")
    if mode == "Active":
        app.reset_canvas.create_rectangle(10, 7, 15, 33, fill="#B22222", outline="")
        app.reset_canvas.create_polygon(15, 20, 35, 5, 35, 35, fill="#B22222", outline="")
        app.reset_allowed = True
    elif mode == "Disabled":
        app.reset_canvas.create_rectangle(10, 7, 15, 33, fill="grey", outline="")
        app.reset_canvas.create_polygon(15, 20, 35, 5, 35, 35, fill="grey", outline="")
        app.reset_allowed = False
    else: raise Exception("INVALID MODE PASSED TO UPDATE_RESET_BUTTON!")
    app.root.update()