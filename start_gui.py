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
    import constants
    import get_raw_data_asc
    import get_raw_data_excel
    import get_raw_data_hamilton
    import blank_and_name_handling
    import quality
    print("\tDone.\n")


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.title("OCUTaF {}".format(__version__))

        menubar = TopBar(self, self.parent)

        self.nb = ttk.Notebook(parent)
        self.nb.grid()
        raw_data_widget = RawDataProcessing(self, self.parent)
        deconvolution_widget = IntegrateDeconvolutionAlgorithm(self, self.parent)
        reorder_widget = ReorderForSinglePointAnalysis(self, self.parent)


    def end_app(self):
        self.parent.destroy()



def read_raw_data(raw_data_dir, reporter_name):
    path_to_file_dir = raw_data_dir
    os.chdir(path_to_file_dir)
    all_files = [file for file in os.listdir()]
    for file in all_files:
        if ".asc" in file:
            logger.info("Found asc files. Expecting data from TECAN robot.")
            return get_raw_data_asc.read_raw_data(reporter_name)
        elif ".xlsx" in file:
            logger.info("Found xlsx files. Expecting data from TECAN reader in Excel format.")
            return get_raw_data_excel.read_raw_data(reporter_name)
        elif ".xls" in file:
            logger.info("Found xls files. Expecting data from Hamilton robot.")
            return get_raw_data_hamilton.read_raw_data(reporter_name)





class IntegrateDeconvolutionAlgorithm:
    def __init__(self, other, parent, *args, **kwargs):
        self.parent = parent
        self.frame = tk.Frame(parent)
        other.nb.add(self.frame, text="MatLab Conversions")


        welcome_label = tk.Label(
            self.frame,
            text="Incorporate the MatLab deconvultion "
            + "algorithm to OCUTaF.\n Chose your raw data folder "
            + "to generate MatLab compatible TECAN files.\n"
            + "Use the file from the MatLab analysis together "
            + "with optional naming files to generate standard output."
            )

        self.reporter_name = tk.StringVar()
        self.reporter_name.set("LUX")

        self.get_file_button = tk.Button(self.frame,
                                         text="Set File",
                                         command=self.get_file)
        self.input_file_name = tk.StringVar()
        self.input_file_path = tk.StringVar()
        self.input_file_label = tk.Label(self.frame,
                                         textvariable=self.input_file_name)



        self.subframe = tk.Frame(self.frame) # Subframe for symmetrical buttons
        self.run_button = tk.Button(self.subframe, text="Run", command=self.run)
        self.reset_button = tk.Button(self.subframe, text="Reset", command=self.reset)
        self.exit_button = tk.Button(self.subframe, text="Close", command=other.end_app)

        self.user_response = tk.StringVar()
        self.user_response.set("")
        self.response_label = tk.Label(self.frame, textvariable=self.user_response)

        # Register widgets.
        welcome_label.grid(row=0, columnspan=2, padx=5, pady=5)

        ttk.Separator(self.frame).grid(columnspan=5, sticky="ew", pady=10)

        self.input_file_label.grid(row=2, column=0, sticky="E", padx=5, pady=5)
        self.get_file_button.grid(row=2, column=1, sticky="W", padx=5, pady=5)

        self.response_label.grid(row=4, columnspan=2, padx=5, pady=15)

        self.subframe.grid(row=11, columnspan=2)
        self.run_button.grid(row=0, column=0, padx=5)
        self.reset_button.grid(row=0, column=1, padx=5)
        self.exit_button.grid(row=0, column=2, padx=5)


    def get_file(self):
        file_name = askopenfilename()
        self.input_file_name.set(os.path.basename(file_name))
        self.input_file_path.set(file_name)


    def reset(self):
        self.input_file_name.set("")
        self.input_file_path.set("")
        self.user_response.set("")


    def run(self):
        self.written_barcodes = read_raw_data(self.reporter_name.get())

        if not os.path.exists(self.input_file_path.get()):
            self.user_response.set("ERROR: INPUT FILE NOT DETECTED.")
            return
        out = self.reorder_csv_for_single_point_data(self.input_file_path.get(),
                                                self.num_replicates_value.get())
        output_file_name = self.input_file_name.get().split(sep=".")[0] + \
        "_reordered" + "." + self.input_file_name.get().split(sep=".")[1]



        output_file_path = os.path.dirname(self.input_file_path.get())
        output_file = os.path.join(output_file_path, output_file_name)
        with open(output_file, "w") as output_file:
            output_file.write(out)

        self.user_response.set("Successfully written {}.".format(output_file_name))









class RawDataProcessing:
    def __init__(self, other, parent, *args, **kwargs):
        self.parent = parent
        self.frame = tk.Frame(parent)
        other.nb.add(self.frame, text="Raw Data")

        self.name_files_are_csv = True

        # User provided variables with default values
        self.reporter_name = tk.StringVar()
        self.reporter_name.set("lux")

        self.blank_wells = tk.StringVar()
        self.blank_wells.set("H10, H11, H12")

        self.raw_data_dir = tk.StringVar()
        self.raw_data_dir.set("not_defined")

        self.path_to_namefiles = tk.StringVar()
        self.path_to_namefiles.set("not_defined")

        self.fixed_blank = tk.BooleanVar() # Use fixed blank for OD
        self.fixed_blank.set(False)
        self.exclude_reporter_blank = tk.BooleanVar() # Do not blank correct reporter
        self.exclude_reporter_blank.set(False)

        # Variables filled within program flow
        self.has_datadir = tk.IntVar()
        self.has_namedir = tk.IntVar()

        self.first_step_complete = tk.StringVar()
        self.second_step_complete = tk.StringVar()
        self.third_step_complete = tk.StringVar()


        # Welcome Label Text
        self.intro_label = tk.Label(
            self.frame, text="Welcome to One Click to Tabular Format."
            + "\nPlease chose configuration as appropriate."
            + " Make sure to define all data files as needed."
            + "\nLastly, start by hitting 'run'."
            )

        # Define widgets WITHOUT positioning
        self.raw_data_button = tk.Button(self.frame,
                                    text="Set Raw Data Folder",
                                    command=lambda: self.set_dir(self.raw_data_dir,
                                                                 self.has_datadir))
        self.names_button = tk.Button(self.frame,
                                 text="Set Name Files Folder (Optional)",
                                 command = lambda:
                                   self.set_dir(self.path_to_namefiles,
                                                self.has_namedir))
        self.subframe = tk.Frame(self.frame) # Subframe for symmetrical buttons
        self.reset_button = tk.Button(self.subframe, text="Reset", command=self.reset)
        self.run_button = tk.Button(self.subframe, text="Run", command=self.run)
        self.exit_button = tk.Button(self.subframe,
                                 text="Close",
                                 command=other.end_app)
        self.reporter_entry = tk.Entry(self.frame, textvariable=self.reporter_name)
        self.reporter_label = tk.Label(self.frame, text="Reporter Name:")
        self.blank_entry = tk.Entry(self.frame, textvariable=self.blank_wells)
        self.blank_label = tk.Label(self.frame, text="Blank Wells:")
        self.has_datadir_check = tk.Checkbutton(self.frame,
                                           text="Has Data Directory",
                                           variable=self.has_datadir,
                                           state=tk.DISABLED)
        self.has_namedir_check =  tk.Checkbutton(self.frame,
                                           text="Has Name File Directory",
                                           variable=self.has_namedir,
                                           state=tk.DISABLED)
        self.fixed_blank_button = tk.Checkbutton(self.frame,
                                                 text = "Use fixed blank for OD values",
                                                 variable = self.fixed_blank,
                                                 onvalue = True,
                                                 offvalue = False)#,
                                                 # height=5,
                                                 # width = 20)
        self.exclude_reporter_blank_button = tk.Checkbutton(self.frame,
                              text = "Do not use blank-correction for reporter",
                              variable = self.exclude_reporter_blank,
                              onvalue = True,
                              offvalue = False)

        self.dummy_label = tk.Label(self.frame, text="") #fills empty row on grid
        self.label_step1 = tk.Label(self.frame, textvariable=self.first_step_complete)
        self.label_step2 = tk.Label(self.frame, textvariable=self.second_step_complete)
        self.label_step3 = tk.Label(self.frame, textvariable=self.third_step_complete)


        # Positioning widgets
        self.intro_label.grid(row=0, column=0, rowspan=3, columnspan=5)

        self.dummy_label.grid(row=3)

        self.reporter_label.grid(row=4, column=0, stick=tk.E)
        self.reporter_entry.grid(row=4, column=1, columnspan=2)
        self.raw_data_button.grid(row=4, column=3, padx=5)
        self.has_datadir_check.grid(row=4, column=4, sticky=tk.W)

        self.blank_label.grid(row=5, column=0, stick=tk.E)
        self.blank_entry.grid(row=5, column=1, columnspan=2)
        self.names_button.grid(row=5, column=3, padx=5)
        self.has_namedir_check.grid(row=5, column=4, sticky=tk.W)

        self.fixed_blank_button.grid(row=6, column=2, columnspan = 2, pady = 7, sticky = tk.W)
        self.exclude_reporter_blank_button .grid(row = 7, column=2, columnspan = 2, pady = 5, sticky = tk.W)

        self.label_step1.grid(row=8, columnspan=5)
        self.label_step2.grid(row=9, columnspan=5)
        self.label_step3.grid(row=10, columnspan=5)

        self.subframe.grid(row=11, columnspan=5)
        self.run_button.grid(row=0, column=0, pady=5, padx=5)
        self.reset_button.grid(row=0, column=1, pady=5, padx=5)
        self.exit_button.grid(row=0, column=2, pady=5, padx=5)


    def set_dir(self, dir_var, corresponding_bool_var):
        path = askdirectory()
        dir_var.set(path)
        if dir_var.get() not in ("", "not_defined"):
            corresponding_bool_var.set(1)
            logger.debug("Set a path to {}".format(path))
        else:
            logger.debug("Tried to set a path variable, but received invalid input.")


    def step1(self):
        """Read Data. Corresponds to Stephan's original Perl script."""
        self.written_barcodes = read_raw_data(self.raw_data_dir.get(), self.reporter_name.get())
        if self.written_barcodes:
            # Any barcodes have been returned by read_raw_data()
            written_barcodes_as_str = ", ".join(self.written_barcodes)
            msg = "Successfully written barcodes for: {}".format(
                                                        written_barcodes_as_str)
            self.first_step_complete.set(msg)
        else: # No barcodes have been returned by read_raw_data()
            error_msg = "ERROR: DID NOT RETRIEVED ANY BARCODES. ANALYSIS ENDED."
            self.first_step_complete.set(error_msg)
            return False
        return True


    def step2(self):
        """Blank Correction."""
        blanks = self.blank_wells.get()
        blanks = blank_and_name_handling.process_well_input(blanks)
        raw_files = [file for file in os.listdir() if "results.txt" in file]
        has_written_blank_corrected_file = False
        for file in raw_files:
            file_basename = file.split(sep=".")[0]
            od, rru = blank_and_name_handling.get_wrappers(file,
                                                           blanks,
                                                           self.fixed_blank.get())
            blank_and_name_handling.write_blank_corrected(od,
                                            file_basename + "_OD_corrected.csv")
            blank_and_name_handling.write_blank_corrected(rru, file_basename
                + "_relative_{}_corrected.csv".format(self.reporter_name.get()))
            if not has_written_blank_corrected_file:
                has_written_blank_corrected_file = True
        if has_written_blank_corrected_file:
            self.second_step_complete.set("All blank corrected files written.")
        else:
            error_msg = "ERROR: NO BLANK CORRECTED FILES WERE WRITTEN." \
                        + "ANALYSIS ENDED."
            self.second_step_complete.set(error_msg)
            return False
        return True


    def step3(self):
        """Optional step: Naming and merging with specified naming CSVs."""
        namefiles = [os.path.join(self.path_to_namefiles.get(), file) for
                     file in os.listdir(self.path_to_namefiles.get())]
        # Correct Excel TAB character bug:
        temp = [quality.is_name_file_csv(name_file) for name_file in namefiles]
        if (not temp == namefiles) and self.name_files_are_csv:
            self.name_files_are_csv = False
            LabelWindow(self.frame,
                        "Your name files have been TSV formatted due to an Excel bug.\n" +\
                        "The bug has been caught and corrected for this run.\n" +\
                        "\nPlease clean up your name file directory before the next run!",
                        title = "Warning: Error in Name File!")

        namefiles = temp

        corrected_files = [file for file in os.listdir()
                           if "corrected" in file and not "bap" in file]

        if len(self.written_barcodes) != len(namefiles):
            self.third_step_complete.set("ERROR: More or less encountered"
                                         + "barcodes than name files!\n"
                                         + "ANALYSIS ENDED!")
            return False

        barcode_to_file = {self.written_barcodes[i]: namefiles[i] for
                           i in range(len(self.written_barcodes))}
        for barcode in barcode_to_file:
            for file in corrected_files:
                if barcode in file:
                    blank_and_name_handling.baptize(file, barcode_to_file[barcode])

        # Merge and Sort final output files
        od = [file for file in os.listdir() if "OD" in file and "bap" in file]
        rfu = [file for file in os.listdir() if "relative" in file
                                                and "bap" in file]
        if len(od) > 1:
            blank_and_name_handling.merge(od, "all_OD.csv", True)
            blank_and_name_handling.merge(rfu, "all_relative_{}.csv".format(
                                                self.reporter_name.get()), True)
        else:
            od_dataframe = blank_and_name_handling.sort_df(od[0])
            od_dataframe.to_csv("sorted_OD.csv", sep=constants.SEP)
            rfu_dataframe = blank_and_name_handling.sort_df(rfu[0])
            rfu_dataframe.to_csv("sorted_relative_{}.csv".format(
                                   self.reporter_name.get()), sep=constants.SEP)
        self.third_step_complete.set("Naming and sorting of data complete.")
        return True


    def run(self):
        # Read Data
        first = self.step1()
        if not first:
            return

        if " " in self.reporter_name.get():
            self.reporter_name.set(self.reporter_name.get().replace(" ", "_"))

        second = self.step2()
        if not second:
            return

        # This step is entirely optional. If no path to naming files is set, this
        #  part will be skipped without raising any errors.
        if not self.path_to_namefiles.get() == "not_defined":
            third = self.step3()
            if not third:
                return

        self.name_files_are_csv = True


    def reset(self):
        self.reporter_name.set("lux")
        self.blank_wells.set("H10, H11, H12")
        self.raw_data_dir.set("not_defined")
        self.path_to_namefiles.set("not_defined")

        self.has_datadir.set(0)
        self.has_namedir.set(0)

        self.first_step_complete.set("")
        self.second_step_complete.set("")
        self.third_step_complete.set("")

        self.name_files_are_csv = True


class ReorderForSinglePointAnalysis:
    def __init__(self, other, parent, *args, **kwargs):
        self.parent = parent
        self.frame = tk.Frame(parent)
        other.nb.add(self.frame, text="Re-order")

        self.background_keyword = "only"

        welcome_label = tk.Label(self.frame, text="Welcome to the reorder"
                               + "functionality of OCUTaF!\n Chose your file "
                               + "you want to reorder for single point analysis,"
                               + " insert the number of replicates and hit run.")

        # What I want in future:
        # Automatically format output file with specified time point.

        self.num_replicates_value = tk.IntVar()
        self.num_replicates_value.set(3)

        self.num_replicates_label = tk.Label(self.frame,
                                        text="Number of biological replicates:")
        self.num_replicates_entry = tk.Entry(self.frame,
                                         textvariable=self.num_replicates_value)

        self.get_file_button = tk.Button(self.frame,
                                         text="Set File",
                                         command=self.get_file)
        self.input_file_name = tk.StringVar()
        self.input_file_path = tk.StringVar()
        self.input_file_label = tk.Label(self.frame,
                                         textvariable=self.input_file_name)

        self.background_subtraction = tk.BooleanVar()
        self.background_subtraction.set(False)
        self.background_subtraction_checkbutton = tk.Checkbutton(self.frame,
                                          text="Perform Background Subtraction",
                                          variable=self.background_subtraction,
                                          onvalue=True,
                                          offvalue=False)

        self.subframe = tk.Frame(self.frame) # Subframe for symmetrical buttons
        self.run_button = tk.Button(self.subframe, text="Run", command=self.run)
        self.reset_button = tk.Button(self.subframe, text="Reset", command=self.reset)
        self.exit_button = tk.Button(self.subframe, text="Close", command=other.end_app)

        self.user_response = tk.StringVar()
        self.user_response.set("")
        self.response_label = tk.Label(self.frame, textvariable=self.user_response)

        # Register widgets.
        welcome_label.grid(row=0, columnspan=2, padx=5, pady=5)
        self.num_replicates_entry.grid(row=1, column=1, sticky="W", padx=5, pady=5)
        self.num_replicates_label.grid(row=1, column=0, sticky="E", padx=5, pady=5)

        self.input_file_label.grid(row=2, column=0, sticky="E", padx=5, pady=5)
        self.get_file_button.grid(row=2, column=1, sticky="W", padx=5, pady=5)
        self.background_subtraction_checkbutton.grid(row=3, column=0, sticky="E")

        self.response_label.grid(row=4, columnspan=2, padx=5, pady=15)

        self.subframe.grid(row=11, columnspan=2)
        self.run_button.grid(row=0, column=0, padx=5)
        self.reset_button.grid(row=0, column=1, padx=5)
        self.exit_button.grid(row=0, column=2, padx=5)


    def get_file(self):
        file_name = askopenfilename()
        self.input_file_name.set(os.path.basename(file_name))
        self.input_file_path.set(file_name)


    def reset(self):
        self.input_file_name.set("")
        self.input_file_path.set("")
        self.user_response.set("")
        self.num_replicates_value.set(3)


    def reorder_csv_for_single_point_data(self, input_file, num_replicates):
        """Reorders an Excel CSV for easier data analysis for single time point
        measurements/analysis.
        Input: An Excel CSV containing two rows: First, column-wise names of certain
        condition in the form "Name of the Construct, Condition". Conditions
        usually refers to inducer concentrations. The ',' character may appear
        only once. Second, corresponding values to the construct/condition pairs.
        Return: A string representing the reorder Excel CSV.
        """
        all_conditions = []
        all_background = []
        idx_to_name = {}
        data_wrapper = {}
        to_print = ""

        with open(input_file) as input_file:
            first_line = input_file.readline()
            for idx, name in enumerate(first_line.split(sep=constants.SEP)):
                construct, condition = name.split(sep=",")
                condition = condition.split(sep=".")[0].strip()
                all_conditions.append(condition)
                idx_to_name[idx] = (construct, condition)

            for condition in all_conditions:
                data_wrapper[condition] = {}

            second_line = input_file.readline()

            if self.background_subtraction.get():
                # Gather data about statistical background (if chosen)
                for idx, value in enumerate(second_line.split(sep=constants.SEP)):
                    construct, condition = idx_to_name[idx]
                    if self.background_keyword in construct:
                        all_background.append(float(value.replace(",", ".")))
                bg_mean = mean(all_background)
                bg_stdev = stdev(all_background)

            for idx, value in enumerate(second_line.split(sep=constants.SEP)):
                construct, condition = idx_to_name[idx]
                # if not construct in printed:
                #     print(construct)
                #     printed.append(construct)
                if not construct in data_wrapper[condition]:
                    data_wrapper[condition][construct] = []

                if not len(data_wrapper[condition][construct]) >= num_replicates:
                    # Prevents overflow with background controls
                    data_wrapper[condition][construct].append(value)

        # Assemble Headline. CURRENTLY (10/2018) MAY MISS THE EMPTY VECTOR CONTROL
        header = ";"
        for _ in data_wrapper:
            for construct in data_wrapper[_]:
                header += construct + num_replicates * ";"
            break
        header += "\n"
        to_print += header

        if self.background_subtraction.get():
            # If background subtraction is chosen, the evaluation writes a
            #  different format than the non-corrected version. The output file
            #  will contain 3 columns per construct in the form: (mean, S.D., N)
            for condition in data_wrapper:
                current_line = condition + ";"
                for any_value_list in data_wrapper[condition]:
                    values = data_wrapper[condition][any_value_list]
                    values = [float(val.replace(",", ".")) for val in values]
                    val_mean = str(mean(values) - bg_mean).replace(".", ",")
                    val_stdev = str(stdev(values) + bg_stdev).replace(".", ",")
                    val_num_rep = str(len(values)).replace(".", ",")
                    current_line += ";".join((val_mean, val_stdev, val_num_rep)) + ";"
                current_line += "\n"
                to_print += current_line
            return to_print


        # Prints values sorted by condition.
        for condition in data_wrapper:
            current_line = condition + ";"
            for _ in data_wrapper[condition]:
                values = data_wrapper[condition][_]
                for val in values:
                    current_line += val + ";"
            current_line += "\n"
            to_print += current_line

        print([condition for condition in data_wrapper["0 uM IPTG"].keys()])
        return to_print


    def run(self):
        printed = []
        if not os.path.exists(self.input_file_path.get()):
            self.user_response.set("ERROR: INPUT FILE NOT DETECTED.")
            return
        out = self.reorder_csv_for_single_point_data(self.input_file_path.get(),
                                                self.num_replicates_value.get())
        output_file_name = self.input_file_name.get().split(sep=".")[0] + \
        "_reordered" + "." + self.input_file_name.get().split(sep=".")[1]


        if self.background_subtraction.get():
            output_file_name = output_file_name.replace("_reordered",
                                                  "_reordered_and_bg_corrected")

        output_file_path = os.path.dirname(self.input_file_path.get())
        output_file = os.path.join(output_file_path, output_file_name)
        with open(output_file, "w") as output_file:
            output_file.write(out)

        self.user_response.set("Successfully written {}.".format(output_file_name))


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


class LabelWindow:
    def __init__(self, parent, message, title=None):
        self.parent = parent
        self.window = tk.Toplevel(self.parent)
        if title is not None:
            self.window.title(title)
        help_text = tk.Label(self.window, text=message, justify=tk.LEFT)
        ok_button = tk.Button(self.window, text="OK", command=self.close)
        help_text.pack(padx=5, pady=5)
        ok_button.pack(padx=5, pady=5)


    def close(self):
        self.window.destroy()


# Start GUI
if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).grid()
    logger.info("Started GUI session.")
    root.mainloop()
    logger.info("Ended GUI session.")
