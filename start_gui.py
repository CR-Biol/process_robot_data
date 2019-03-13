"""
Graphical version of data procession from TECAN readers.

12/2018.
Christian Rauch. Marburg.
"""

import os
import logging
import constants


__version__ = "alpha_0.9.2"
__author__ = "Christian Rauch"


# Initialize logger.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # DEBUG, INFO, WARNING, ERROR, CRITICAL
formatter = constants.LOG_FORMATTER
if not os.path.exists("logs"):
    os.makedirs("logs")
log_file_handler = logging.FileHandler(os.path.join("logs", "main.log"))
log_file_handler.setFormatter(formatter)
logger.addHandler(log_file_handler)




if __name__ == "__main__":
    print("Starting Robot Data Analysis Software version", __version__, "\n")
    print("Loading Python internal modules...")
    import os
    from statistics import mean, stdev
    print("\tDone.\n")
    print("Loading Graphical Interface...")
    import tkinter as tk
    from tkinter import ttk
    from tkinter.filedialog import askdirectory, askopenfilename
    from PIL import ImageTk, Image
    print("\tDone.\n")
    print("Loading additional software packages...")
    import raw_data
    import reorder
    import deconvolution
    import constants
    print("\tDone.\n")


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.title("OCUTaF {}".format(__version__))

        menubar = TopBar(self, self.parent)

        self.nb = ttk.Notebook(parent)
        self.nb.grid()
        raw_data_widget = raw_data.RawDataProcessing(self, self.parent)

        # BOTH THE REORDER AS WELL AS THE DECONVOLUTION WIDGET ARE BUGGY ATM. 

        # reorder_widget = reorder.ReorderForSinglePointAnalysis(self, self.parent)
        # deconvolution_widget = deconvolution.IntegrateDeconvolutionAlgorithm(self, self.parent)


    def end_app(self):
        self.parent.destroy()


class TopBar:
    """ Creates a topbar menu. Implementation of help menu."""
    def __init__(self, other, parent):
        self.parent = parent
        menubar = tk.Menu(self.parent)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=lambda: self.help("about.txt"))
        helpmenu.add_command(label="Reporter Name", command=lambda: self.help("reporter.txt"))
        helpmenu.add_command(label="Blank Wells", command=lambda: self.help("blanks.txt"))
        helpmenu.add_command(label="Raw Data", command=lambda: self.help("rawdata.txt"))
        helpmenu.add_command(label="Files for Naming", command=lambda: self.help("naming.txt"))
        helpmenu.add_separator()
        helpmenu.add_command(label="Exit", command=other.end_app)
        menubar.add_cascade(label="Help", menu=helpmenu)

        # display the menu
        self.parent.config(menu=menubar)


    def help(self, about):
        msg = ""
        path_to_files = os.path.join(os.path.dirname(os.path.realpath(__file__)),  "help")
        with open(os.path.join(path_to_files, about)) as file:
            for line in file:
                msg += line
        help_window = LabelWindow(self.parent, msg)



# Start GUI
if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).grid()
    logger.info("Started GUI session.")
    root.mainloop()
    logger.info("Ended GUI session.")
