"""
TO DO:

- Improved User communication
    - Pop-Up LabelWindow listing all constructs
    - Pop-Up LabelWindow listing all conditions

- More Quality Controls
    - Auto-check for consistency: all constructs should share the same conditions
    - Auto format output file from raw_data widget
"""



import os
import logging
from statistics import mean, stdev
from math import sqrt

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilename

import constants

# Initialize logger.
logger = constants.setup_logger(
    log_file_name = __name__ + ".log",
    log_level = logging.DEBUG,
    logger_name = __name__
    )


class ReorderForSinglePointAnalysis:
    def __init__(self, other, parent, *args, **kwargs):
        self.parent = parent
        self.frame = tk.Frame(parent)
        other.nb.add(self.frame, text = "Re-order")

        welcome_label = tk.Label(
            self.frame, 
            text = "Welcome to the reorder" \
            + "functionality of OCUTaF!\n Chose your file " \
            + "you want to reorder for single point analysis," \
            + " insert the number of replicates and hit run." \
            )

        # What I want in future:
        # Automatically format output file with specified time point.

        self.num_replicates_value = tk.IntVar()
        self.num_replicates_value.set(3)

        self.num_replicates_label = tk.Label(
            self.frame,
            text = "Number of biological replicates:"
            )
        self.num_replicates_entry = tk.Entry(
            self.frame,
            textvariable = self.num_replicates_value
            )
        self.get_file_button = tk.Button(
            self.frame,
            text = "Set File",
            command=self.get_file
            )
        self.input_file_name = tk.StringVar()
        self.input_file_path = tk.StringVar()
        self.input_file_label = tk.Label(
            self.frame,
            textvariable = self.input_file_name
            )

        self.background_keyword = tk.StringVar()
        self.background_keyword.set("only")
        self.change_background_keyword_label = tk.Label(
            self.frame, 
            text = "Background Keyword:"
            )
        self.change_background_keyword_entry = tk.Entry(
            self.frame, 
            textvariable = self.background_keyword
            )
        self.background_subtraction = tk.BooleanVar()
        self.background_subtraction.set(False)
        self.background_subtraction_checkbutton = tk.Checkbutton(
            self.frame,
            text = "Perform Background Subtraction",
            variable = self.background_subtraction,
            onvalue = True,
            offvalue = False
            )

        self.subframe = tk.Frame(self.frame) # Subframe for symmetrical buttons
        self.run_button = tk.Button(
            self.subframe, 
            text = "Run", 
            command = self.run
            )
        self.reset_button = tk.Button(
            self.subframe, 
            text = "Reset", 
            command = self.reset
            )
        self.exit_button = tk.Button(
            self.subframe, 
            text = "Close", 
            command = other.end_app
            )

        self.user_response = tk.StringVar()
        self.user_response.set("")
        self.response_label = tk.Label(
            self.frame, 
            textvariable = self.user_response
            )

        # Add tooltips.
        constants.ToolTip(
            self.get_file_button,
            "Chose file for grouping by different conditions, e.g. inductor concentrations."
            )
        constants.ToolTip(
            self.background_subtraction_checkbutton,
            "Perform background subtraction. Will alter output to"
            + "\nthe form (mean, standard deviation, number of replicates)"
            )
        constants.ToolTip(
            self.change_background_keyword_label,
            "Keyword in naming file that indicates background control."
            + "\nOnly necessary if background subtraction is performed."
            )

        # Register widgets.
        welcome_label.grid(row = 0, columnspan = 2, padx = 5, pady = 5)
        self.num_replicates_entry.grid(row = 1, column = 1, sticky = "W", padx = 5, pady = 5)
        self.num_replicates_label.grid(row = 1, column = 0, sticky = "E", padx = 5, pady = 5)

        self.input_file_label.grid(row = 2, column = 0, sticky = "E", padx = 5, pady = 5)
        self.get_file_button.grid(row = 2, column = 1, sticky = "W", padx = 5, pady = 5)
        self.background_subtraction_checkbutton.grid(row = 3, column = 0, sticky = "E")
        self.change_background_keyword_label.grid(row = 4, column = 0, sticky = "E", padx = 5, pady = 5)
        self.change_background_keyword_entry.grid(row = 4, column = 1, sticky = "W", padx = 5, pady = 5)

        self.response_label.grid(row=5, columnspan=2, padx=5, pady=15)

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


    def reorder_csv_for_single_point_data(self, in_file, num_replicates):
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

        with open(in_file) as input_file:
            first_line = input_file.readline()
            for idx, name in enumerate(first_line.split(sep = constants.SEP)):
                construct, condition = name.split(sep = ",")
                condition = condition.split(sep=".")[0].strip() # Replicates are marked with ".1", ".2", ...
                all_conditions.append(condition)
                idx_to_name[idx] = (construct, condition)

            for condition in all_conditions:
                data_wrapper[condition] = {}

            second_line = input_file.readline()

            if self.background_subtraction.get():
                # Gather data about statistical background (if chosen)
                for idx, value in enumerate(second_line.split(sep = constants.SEP)):
                    construct, condition = idx_to_name[idx]
                    if self.background_keyword.get() in construct:
                        logger.debug("Added {} to background constructs.")
                        all_background.append(float(value.replace(",", ".")))
                bg_mean = mean(all_background)
                bg_stdev = stdev(all_background)

            for idx, value in enumerate(second_line.split(sep = constants.SEP)):
                construct, condition = idx_to_name[idx]
                if not construct in data_wrapper[condition]:
                    data_wrapper[condition][construct] = []

                if not len(data_wrapper[condition][construct]) >= num_replicates:
                    # Prevents overflow with background controls
                    data_wrapper[condition][construct].append(value)
                else:
                    logger.warning("Overflow in data_wrapper for {0}, {1}".format(construct, condition))
        
        captured_conditions = []
        _length = -1
        for condition in data_wrapper:
            captured_conditions.append(condition)
            if _length == -1:
                _length = len(data_wrapper[condition])
            else:
                if not _length == len(data_wrapper[condition]):
                    error_msg = "The condition {0} contained {1} constructs, but others contain {2}".format(
                        condition,
                        len(data_wrapper[condition]),
                        _length
                        )
                    logger.critical(error_msg)
                    raise ValueError(error_msg)
        logger.info("Reordered data from {0}. Captured the conditions {1}".format(
            os.path.basename(in_file),
            ", ".join(captured_conditions)
            ))

        # Assemble Headline. CURRENTLY (10/2018) MAY MISS THE EMPTY VECTOR CONTROL
        header = constants.SEP # Initialize header line with empty cell
        for any_condition in data_wrapper:
            # This loop must be executed only once to write a correct header.
            for construct in data_wrapper[any_condition]:
                header += construct + num_replicates * constants.SEP # Creates num_replicate cells in header.s
            break
        header += "\n"
        to_print += header

        if self.background_subtraction.get():
            # If background subtraction is chosen, the evaluation writes a
            #  different format than the non-corrected version. The output file
            #  will contain 3 columns per construct in the form: (mean, S.D., N)
            for condition in data_wrapper:
                current_line = condition + constants.SEP # Name for current row.
                for value_list in data_wrapper[condition]:
                    values = data_wrapper[condition][value_list]
                    values = [float(val.replace(",", ".")) for val in values]
                    val_mean = str(mean(values) - bg_mean).replace(".", ",")
                    val_stdev = str(
                        sqrt(stdev(values)**2 + bg_stdev**2)
                        ).replace(".", ",")
                    val_num_rep = str(len(values)).replace(".", ",")
                    current_line += ";".join((val_mean, val_stdev, val_num_rep)) + constants.SEP
                current_line += "\n"
                to_print += current_line
            return to_print


        # Prints values sorted by condition.
        for condition in data_wrapper:
            current_line = condition + constants.SEP
            for construct in data_wrapper[condition]:
                values = data_wrapper[condition][construct]
                for val in values:
                    current_line += val + constants.SEP
            current_line += "\n"
            to_print += current_line

        return to_print


    def run(self):
        printed = []
        if not os.path.exists(self.input_file_path.get()):
            self.user_response.set("ERROR: INPUT FILE NOT DETECTED.")
            return
        out = self.reorder_csv_for_single_point_data(
            self.input_file_path.get(),
            self.num_replicates_value.get()
            )
        output_file_name = "".join([
            os.path.splitext(self.input_file_name.get())[0], 
            "_reordered", 
            os.path.splitext(self.input_file_name.get())[1]
            ])

        if self.background_subtraction.get():
            output_file_name = output_file_name.replace(
                "_reordered",
                "_reordered_and_bg_corrected"
                )

        output_file_path = os.path.dirname(self.input_file_path.get())
        output_file = os.path.join(output_file_path, output_file_name)
        with open(output_file, "w") as output_file:
            output_file.write(out)

        self.user_response.set("Successfully written {}.".format(output_file_name))

