#==============================================================================
# CONSTANT VARIABLES
#==============================================================================

import os
import logging
import tkinter as tk

# Common seperator for output files. 
#   ";" makes CSV files readible for German version of Excel.
SEP = ";"

# Assumed value to use when fixed OD correction is chosen.
FIXED_OD_BLANK_VALUE = 0.039

# Font used in the GUI.
FONT_FAMILY = "Nirmala UI"

# Sizes must be integers >= 4
FONT_SIZE = 10 
BTN_WIDTH_NORMAL = 11
BTN_WIDTH_BIG = 30
BTN_WIDTH_SMALL = 7

col_names = ['cycle', 'time', 'temp', 'A1', 'A2', 'A3', 'A4',
                'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12', 'B1', 'B2',
                'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'B12',
                'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10',
                'C11', 'C12', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8',
                'D9', 'D10', 'D11', 'D12', 'E1', 'E2', 'E3', 'E4', 'E5', 'E6',
                'E7', 'E8', 'E9', 'E10', 'E11', 'E12', 'F1', 'F2', 'F3', 'F4',
                'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'G1', 'G2',
                'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'G10', 'G11', 'G12',
                'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10',
                'H11', 'H12']

data_names = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10',
              'A11', 'A12', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8',
              'B9', 'B10', 'B11', 'B12', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6',
              'C7', 'C8', 'C9', 'C10', 'C11', 'C12', 'D1', 'D2', 'D3', 'D4',
              'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12', 'E1', 'E2',
              'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9', 'E10', 'E11', 'E12',
              'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10',
              'F11', 'F12', 'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8',
              'G9', 'G10', 'G11', 'G12', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6',
              'H7', 'H8', 'H9', 'H10', 'H11', 'H12']

# Header line for primary TSV results file.
header = "Cycle\tTime [min]\tTemp. [deg. C]\tA1\tA2\tA3\tA4\tA5\tA6\tA7\tA8\tA9\tA10\
         \tA11\tA12\tB1\tB2\tB3\tB4\tB5\tB6\tB7\tB8\tB9\tB10\tB11\tB12\tC1\tC2\tC3\
         \tC4\tC5\tC6\tC7\tC8\tC9\tC10\tC11\tC12\tD1\tD2\tD3\tD4\tD5\tD6\tD7\tD8\tD9\
         \tD10\tD11\tD12\tE1\tE2\tE3\tE4\tE5\tE6\tE7\tE8\tE9\tE10\tE11\tE12\tF1\tF2\
         \tF3\tF4\tF5\tF6\tF7\tF8\tF9\tF10\tF11\tF12\tG1\tG2\tG3\tG4\tG5\tG6\tG7\tG8\
         \tG9\tG10\tG11\tG12\tH1\tH2\tH3\tH4\tH5\tH6\tH7\tH8\tH9\tH10\tH11\tH12\n"


class LabelWindow:
    """Simple pop-up widget displaying a message.
    """
    def __init__(self, parent, message, title=None):
        self.parent = parent
        self.window = tk.Toplevel(self.parent)
        if title is not None:
            self.window.title(title)
        help_text = tk.Label(self.window, text=message, justify=tk.LEFT)
        ok_button = tk.Button(self.window, text="OK", command=self.close)
        help_text.pack(padx = 5, pady = 5, ipadx = 5, ipady = 15)
        ok_button.configure(
            width = 5,
            font = (FONT_FAMILY, FONT_SIZE, "bold"),
            cursor = "hand2",
            background = "#bbb",
            activebackground = "#4c4c4c"
        )
        ok_button.pack(padx = 5, pady = 5)

    def close(self):
        self.window.destroy()


class ToolTip(object):
    """
    Create a tooltip for a given widget.
    Taken from https://www.daniweb.com/programming/software-development/code/484591/a-tooltip-class-for-tkinter
    (2019/03/13) with slight modifications.
    """
    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.close)


    def enter(self, event=None):
        x = y = 0
        # x, y, cx, cy = self.widget.bbox("insert")
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 10 #+ 25
        y += self.widget.winfo_rooty() + 35 #+ 20
        # creates a toplevel window
        self.tw = tk.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(
            self.tw, 
            text=self.text, 
            justify = 'left',
            relief = 'solid', 
            borderwidth = 1,
            background = "white"
            )
        label.pack(ipadx=1)

    def close(self, event=None):
        if self.tw:
            self.tw.destroy()


def setup_logger(log_level, logger_name):
    """Returns a logger with default setup callable for each module."""
    if not os.path.exists("logs"):
        os.makedirs("logs")
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level) # DEBUG, INFO, WARNING, ERROR, CRITICAL
    formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s")
    log_file_handler = logging.FileHandler(os.path.join("logs", "OCUTaF.log"))
    log_file_handler.setFormatter(formatter)
    logger.addHandler(log_file_handler)
    return logger


def remove_double_quotest_from_file(file):
    """Takes a file handle as input.
    Overrides the files content with all double quotation marks (' " ') removed.
    """
    clean_string = ""
    with open(file) as infile:
        for line in infile:
            clean_string += line.replace('"', '')
    with open(file, "w") as newfile:
        newfile.write(clean_string)


if __name__ != "__main__":
    print("\tInitialized constants and helper functions.")
