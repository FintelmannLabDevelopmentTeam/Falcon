import tkinter as tk
import webbrowser
import os
from PIL import Image, ImageTk
icon_folder = os.path.join(os.path.dirname(__file__), '..', 'icons')

class ToolTip:
    """Creates a tooltip for a given widget and displays it near the mouse cursor."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.wraplength = 600
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
        self.widget.bind("<Motion>", self.move_tooltip)  # Bind mouse motion to move tooltip

    def show_tooltip(self, event=None):
        """Display the tooltip window near the mouse."""
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)  # Remove window decorations
        label = tk.Label(self.tooltip_window, text=self.text, relief="solid", borderwidth=1, 
                         background="lightyellow", fg="black", wraplength=self.wraplength)  # Set background and text color
        label.pack()
        self.move_tooltip(event)  # Position the tooltip near the mouse

    def move_tooltip(self, event):
        """Move the tooltip with the mouse."""
        if self.tooltip_window:
            # Position the tooltip near the mouse cursor
            x = event.x_root + 10  # Add some offset to avoid overlap with the mouse
            y = event.y_root + 10
            self.tooltip_window.wm_geometry(f"+{x}+{y}")

    def hide_tooltip(self, event=None):
        """Hide the tooltip window."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None





def resize_image(path, size):
    image = Image.open(path)

    # If size is a single integer, calculate height based on aspect ratio
    if isinstance(size, int):
        # Get the original width and height of the image
        original_width, original_height = image.size
        
        # Calculate the new height to preserve the aspect ratio
        aspect_ratio = original_height / original_width
        new_width = size
        new_height = int(new_width * aspect_ratio)  # Calculate height based on the width

        size = (new_width, new_height)  # Update size to a tuple of (width, height)
    
    try:
        image = image.resize(size, Image.LANCZOS)
    except:  # For newer versions of PIL
        try:
            from PIL import ImageResampling
            image = image.resize(size, ImageResampling.LANCZOS)
        except:
            print("Resizing icons failed!")
    
    return ImageTk.PhotoImage(image)


def get_info_icon(size=(16,16)):
    return resize_image(os.path.join(icon_folder, 'info.png'), size)

def get_fintelmann_logo(width=40):
    return resize_image(os.path.join(icon_folder, 'fintelmann_lab.png'), width)

def get_mgh_logo(width=20):
    return resize_image(os.path.join(icon_folder, 'harvard_mgh.png'), width)

def update_start_button(app, mode="Start"):
    app.start_canvas.delete("all")
    app.start_canvas.unbind("<Button-1>")
    if mode == "Start":
        triangle = app.start_canvas.create_polygon(5, 5, 5, 35, 32, 20, fill="green", outline="")
        app.start_canvas.bind("<Button-1>", lambda event: app.start_prediction())
        app.start_canvas.config(cursor="hand2")
    elif mode == "Pause":
        left_bar = app.start_canvas.create_rectangle(10, 5, 18, 35, fill="black", outline="")
        right_bar = app.start_canvas.create_rectangle(22, 5, 30, 35, fill="black", outline="")
        app.start_canvas.bind("<Button-1>", lambda event: app.start_prediction())
        app.start_canvas.config(cursor="hand2")
    elif mode == "Disabled":
        triangle = app.start_canvas.create_polygon(5, 5, 5, 35, 32, 20, fill="grey", outline="")
        app.start_canvas.config(cursor="arrow")
    else: raise Exception("INVALID MODE PASSED TO UPDATE_START_BUTTON!")
    app.root.update()

def update_reset_button(app, mode="Active"):
    app.reset_canvas.delete("all")
    if mode == "Active":
        app.reset_canvas.create_rectangle(10, 7, 15, 33, fill="#B22222", outline="")
        app.reset_canvas.create_polygon(15, 20, 35, 5, 35, 35, fill="#B22222", outline="")
        app.reset_allowed = True
        app.reset_canvas.config(cursor="hand2")
    elif mode == "Disabled":
        app.reset_canvas.create_rectangle(10, 7, 15, 33, fill="grey", outline="")
        app.reset_canvas.create_polygon(15, 20, 35, 5, 35, 35, fill="grey", outline="")
        app.reset_allowed = False
        app.reset_canvas.config(cursor="arrow")
    else: raise Exception("INVALID MODE PASSED TO UPDATE_RESET_BUTTON!")
    app.root.update()

def call_fintelmann_website():
    webbrowser.open("https://fintelmannlab.mgh.harvard.edu")

def get_font_size(size="large"):
    if size == "title": a = 20
    elif size == "huge": a = 10
    elif size == "xlarge": a = 4
    elif size == "large": a = 2
    else: a = 0
    b = tk.font.nametofont("TkDefaultFont").cget("size")
    return a + b