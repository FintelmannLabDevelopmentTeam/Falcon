# © 2024 Philipp Kaess. All rights reserved.
# Licensed under the MIT License. See LICENSE file in the project root for more information

from src.gui import CTScanSeriesPredictionApp
from tkinter import Tk

if __name__ == "__main__":
    root = Tk()
    app = CTScanSeriesPredictionApp(root)
    root.mainloop()