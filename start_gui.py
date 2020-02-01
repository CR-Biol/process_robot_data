"""
Graphical version of data procession from TECAN readers.

12/2018.
Christian Rauch. Marburg.
"""


__version__ = "0.9.4"
__author__ = "Christian Rauch"


if __name__ == "__main__":
    print("Starting Robot Data Analysis Software version", __version__, "\n")
    print("Loading Python internal modules...")
    import os
    import logging
    from statistics import mean, stdev
    print("\tDone.\n")
    print("Loading Graphical Interface...")
    import tkinter as tk
    import tkinter.font as tkFont
    from tkinter import ttk
    from tkinter.filedialog import askdirectory, askopenfilename
    # from PIL import ImageTk, Image
    print("\tDone.\n")
    print("Loading additional software packages...")
    import constants
    import raw_data
    import reorder
    import dose_response
    print("\tDone.\n")


# Initialize logger.
logger = constants.setup_logger(
    log_level=logging.DEBUG,
    logger_name=__name__
)


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.title("OCUTaF {}".format(__version__))
        self.remove_quotation_marks = tk.BooleanVar()
        self.remove_quotation_marks.set(True)

        InsertTopBar(self, self.parent)

        self.nb = ttk.Notebook(parent)
        self.nb.grid()
        # Register main widgets as notebook pages.
        raw_data.GUIRawDataProcessing(self, self.parent)
        reorder.GUIReorderForSinglePointAnalysis(self, self.parent)
        dose_response.GUIDoseResponseGUI(self, self.parent)
        # deconvolution.IntegrateDeconvolutionAlgorithm(self, self.parent)

        self.copyright = tk.Label(
            self.parent,
            text=f"Written by Christian Rauch, version {__version__}"
        )
        # Apply Styling
        self.__style_fonts()
        self.__make_small(self.copyright)
        self.copyright.grid(pady=(0, 10))

    def __style_fonts(self):
        self.font_size = constants.FONT_SIZE
        self.font_family = constants.FONT_FAMILY
        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(
            size=self.font_size,
            family=self.font_family
        )

    def __make_small(self, widget):
        widget.configure(
            font=(
                constants.FONT_FAMILY,
                str(int(int(constants.FONT_SIZE) * 0.75))
            )
        )

    def end_app(self):
        self.parent.destroy()


class InsertTopBar:
    """ Creates a topbar menu. Implementation of help menu."""

    def __init__(self, parent, grand_parent):
        self.grand_parent = grand_parent
        self.parent = parent
        self.menubar = tk.Menu(self.grand_parent)
        self.add_helpmenu()
        self.add_optionmenu()
        self.grand_parent.config(menu=self.menubar)  # display the menu

    def add_optionmenu(self):
        optionmenu = tk.Menu(self.menubar, tearoff=0)
        optionmenu.add_command(
            label="dummy",
            command=lambda: None
        )
        optionmenu.add_checkbutton(
            label="Remove double quotation marks from input CSV files",
            onvalue=True,
            offvalue=False,
            variable=self.parent.remove_quotation_marks
        )
        self.menubar.add_cascade(label="Options", menu=optionmenu)

    def add_helpmenu(self):
        helpmenu = tk.Menu(self.menubar, tearoff=0)
        helpmenu.add_command(
            label="About",
            command=lambda: self.help("about.txt")
        )
        helpmenu.add_command(
            label="Reporter Name",
            command=lambda: self.help("reporter.txt")
        )
        helpmenu.add_command(
            label="Blank Wells",
            command=lambda: self.help("blanks.txt")
        )
        helpmenu.add_command(
            label="Raw Data",
            command=lambda: self.help("rawdata.txt")
        )
        helpmenu.add_command(
            label="Files for Naming",
            command=lambda: self.help("naming.txt")
        )
        helpmenu.add_separator()
        helpmenu.add_command(label="Exit", command=self.parent.end_app)
        self.menubar.add_cascade(label="Help", menu=helpmenu)

    def help(self, about):
        msg = ""
        path_to_files = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "help"
        )
        with open(os.path.join(path_to_files, about)) as file:
            for line in file:
                msg += line
        constants.LabelWindow(self.grand_parent, msg)


if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).grid()
    logger.info("Started GUI session.")
    root.mainloop()
    logger.info("Ended GUI session.")
