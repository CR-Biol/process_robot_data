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


from pprint import pprint


# Initialize logger.
logger = constants.setup_logger(
    log_level = logging.DEBUG,
    logger_name = __name__
    )


class ReorderForSinglePointAnalysis:
    def __init__(self, parent, grand_parent, *args, **kwargs):
        self.grand_parent = grand_parent
        self.frame = tk.Frame(grand_parent)
        self.parent = parent
        self.parent.nb.add(self.frame, text = "Re-order")

        self.welcome_label = tk.Label(
            self.frame, 
            text = "Welcome to the reorder" \
            + "functionality of OCUTaF!\n Chose your file " \
            + "you want to reorder for single point analysis," \
            + " insert the number of replicates and hit run." \
            )

        # What I want in future:
        # Automatically format output file with specified time point.

        self.remove_whitespaces_from_input_file = self.parent.remove_quotation_marks.get()

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
            command = parent.end_app
            )

        self.user_response = tk.StringVar()
        self.user_response.set("")
        self.response_label = tk.Label(
            self.frame, 
            textvariable = self.user_response
            )

        self.add_tooltips()
        self.register_widgets()

    def add_tooltips(self):
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

    def register_widgets(self):
        self.welcome_label.grid(row = 0, columnspan = 2, padx = 5, pady = 5)
        self.num_replicates_entry.grid(row = 1, column = 1, sticky = "W", padx = 5, pady = 5)
        self.num_replicates_label.grid(row = 1, column = 0, sticky = "E", padx = 5, pady = 5)

        self.input_file_label.grid(row = 2, column = 0, sticky = "E", padx = 5, pady = 5)
        self.configure_btn(self.get_file_button, btn_width=constants.BTN_WIDTH_SMALL)
        self.get_file_button.grid(row = 2, column = 1, sticky = "W", padx = 5, pady = 5)
        self.background_subtraction_checkbutton.grid(row = 3, column = 0, sticky = "E")
        self.change_background_keyword_label.grid(row = 4, column = 0, sticky = "E", padx = 5, pady = 5)
        self.change_background_keyword_entry.grid(row = 4, column = 1, sticky = "W", padx = 5, pady = 5)

        self.response_label.grid(row=5, columnspan=2, padx=5, pady=15)

        self.subframe.grid(row=11, columnspan=2)
        self.configure_btn(self.run_button)
        self.run_button.grid(row=0, column=0, padx=5)
        self.configure_btn(self.reset_button)
        self.reset_button.grid(row=0, column=1, padx=5)
        self.configure_btn(self.exit_button)
        self.exit_button.grid(row=0, column=2, padx=5)

    def configure_btn(self, btn_widget, btn_width=constants.BTN_WIDTH_NORMAL):
        btn_widget.configure(
            width = btn_width,
            font = (constants.FONT_FAMILY, constants.FONT_SIZE, "bold"),
            cursor = "hand2",
            background = "#bbb",
            activebackground = "#4c4c4c"
        )

    def get_file(self):
        file_name = askopenfilename()
        if self.remove_whitespaces_from_input_file:
            constants.remove_double_quotest_from_file(file_name)
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
        processed_file_as_str = self.get_single_data_point_info_from_file(in_file)
        first_line, second_line = processed_file_as_str.split("\n")
        data_wrapper = self.initialize_data_wrapper_dict(first_line, second_line)
        if self.background_subtraction.get():
            return self.create_bg_corrected_csv_string(data_wrapper)
        else:
            return self.create_csv_string(data_wrapper)
        
    def initialize_data_wrapper_dict(self, first_line, second_line):
        data_wrapper_dict, idx_to_name = self.initialize_from_first_line(
            first_line)
        data_wrapper_dict = self.initialize_from_second_line(
            second_line,
            data_wrapper_dict,
            idx_to_name)
        data_wrapper_dict = self.fill_data_wrapper_with_conditions_as_keys(
            data_wrapper_dict)
        return data_wrapper_dict
  
    def initialize_from_first_line(self, first_line):
        idx_to_name = {}
        data_wrapper_dict = {}
        all_conditions = []
        for idx, name in enumerate(first_line.split(sep=constants.SEP)):
            if not name:
                continue
            try:
                construct, condition = name.split(sep=",")
            except ValueError:
                print(
                    f"The name {name} is invalid! Make sure to conform to (construct, condition) format!")
                raise ValueError
            # Replicates are marked with ".1", ".2", ...
            condition = condition.split(sep=".")[0].strip()
            all_conditions.append(condition)
            idx_to_name[idx] = (construct, condition)
            
        for condition in all_conditions:
            data_wrapper_dict[condition] = {}
        
        return data_wrapper_dict, idx_to_name

    def initialize_from_second_line(self, second_line, data_wrapper_dict, idx_to_name):
        for idx, value in enumerate(second_line.split(sep=constants.SEP)):
            if not value:
                continue
            construct, condition = idx_to_name[idx]
            if not construct in data_wrapper_dict[condition]:
                data_wrapper_dict[condition][construct] = []

            if not len(data_wrapper_dict[condition][construct]) >= self.num_replicates_value.get():
                # Prevents overflow with background controls
                data_wrapper_dict[condition][construct].append(value)
            else:
                logger.warning("Overflow in data_wrapper for {0}, {1}".format(
                    construct, condition))
        return data_wrapper_dict

    def fill_data_wrapper_with_conditions_as_keys(self, data_wrapper_dict):
        captured_conditions = []
        _length = None
        for condition in data_wrapper_dict:
            captured_conditions.append(condition)
            if _length is None:
                _length = len(data_wrapper_dict[condition])
            else:
                if not _length == len(data_wrapper_dict[condition]):
                    error_msg = "The condition {0} contained {1} constructs, but parents contain {2}".format(
                        condition,
                        len(data_wrapper_dict[condition]),
                        _length
                    )
                    logger.critical(error_msg)
                    raise ValueError(error_msg)
        logger.info("Reordered data from {0}. Captured the conditions {1}".format(
            self.input_file_name.get(),
            ", ".join(captured_conditions)
        ))
        return data_wrapper_dict

    def assemble_headline(self, data_wrapper_dict):
        header = constants.SEP  # Initialize header line with empty cell
        for any_condition in data_wrapper_dict:
            for construct in data_wrapper_dict[any_condition]:
                # Creates num_replicate cells in header
                header += construct + self.num_replicates_value.get() * constants.SEP
            break # This loop must be executed exactly once to write a correct header.
        header += "\n"
        return header

    def create_csv_string(self, final_data_wrapper_dict):
        to_print = self.assemble_headline(final_data_wrapper_dict)
        for condition in final_data_wrapper_dict:
            current_line = condition + constants.SEP
            for construct in final_data_wrapper_dict[condition]:
                values = final_data_wrapper_dict[condition][construct]
                for val in values:
                    current_line += val + constants.SEP
            current_line += "\n"
            to_print += current_line
        return to_print

    def create_bg_corrected_csv_string(self, final_data_wrapper_dict):
        # Gather data about statistical background (if chosen)
        processed_file_as_str = self.get_single_data_point_info_from_file(
            self.input_file_path.get())
        first_line, second_line = processed_file_as_str.split("\n")
        idx_to_name = self._get_idx_to_name(first_line)
        all_background = []
        for idx, value in enumerate(second_line.split(sep=constants.SEP)):
            construct, condition = idx_to_name[idx]
            if self.background_keyword.get() in construct:
                logger.debug(
                    f"Added {construct} to background constructs.")
                all_background.append(float(value.replace(",", ".")))
        bg_mean = mean(all_background)
        bg_stdev = stdev(all_background)    
        # If background subtraction is chosen, the evaluation writes a
        #  different format than the non-corrected version. The output file
        #  will contain 3 columns per construct in the form: (mean, S.D., N)
        to_print = self.assemble_headline(final_data_wrapper_dict)
        for condition in final_data_wrapper_dict:
            current_line = condition + constants.SEP # Name for current row.
            for value_list in final_data_wrapper_dict[condition]:
                values = final_data_wrapper_dict[condition][value_list]
                values = [float(val.replace(",", ".")) for val in values]
                val_mean = str(mean(values) - bg_mean).replace(".", ",")
                val_stdev = str(
                    sqrt(stdev(values)**2 + bg_stdev**2)
                    ).replace(".", ",")
                val_num_rep = str(len(values)).replace(".", ",")
                current_line += ";".join((val_mean, val_stdev, val_num_rep)) \
                                + constants.SEP
            current_line += "\n"
            to_print += current_line
        return to_print

    def _get_idx_to_name(self, first_line):
        return self.initialize_from_first_line(first_line)[1]

    def get_single_data_point_info_from_file(self, in_file, timepoint_idx=4):
        """Uses the merged and baptized data file from the raw_data module and
        returns data from a single measurement timepoint necessary for the 
        reordering functionalities.
        """
        with open(in_file) as file:
            for row_idx, line in enumerate(file):
                if row_idx == 0:  # Read head_line
                    head_line, start_col_idx = self.read_headline_and_start_col_idx(
                        line)
                elif row_idx == timepoint_idx:  # read data_line
                    dataline = self.read_dataline(line, start_col_idx)
        return head_line.strip() + "\n" + dataline

    def read_headline_and_start_col_idx(self, line):
        to_ignore = ["", "temp", "time", "cycle"]  # non-data column titles
        start_col_idx = None
        headline = ""
        for col_idx, cell in enumerate(line.split(constants.SEP)):
            if cell.strip() in to_ignore:
                continue
            elif start_col_idx is None:
                start_col_idx = col_idx
            if start_col_idx and cell:
                headline += cell.strip() + constants.SEP
        return headline, start_col_idx

    def read_dataline(self, line, start_col_idx):
        dataline = ""
        for col_idx, cell in enumerate(line.split(constants.SEP)):
            if col_idx >= start_col_idx and cell:
                dataline += cell.strip() + constants.SEP
        return dataline

    def run(self):
        if not os.path.exists(self.input_file_path.get()):
            self.user_response.set("ERROR: INPUT FILE NOT DETECTED.")
            return
        out = self.reorder_csv_for_single_point_data(
            self.input_file_path.get(),
            self.num_replicates_value.get()
            )
        output_file_name = self.input_file_name.get().replace(".csv", "_reordered.csv")
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


if __name__ != "__main__":
    print("\tInitialized data reorganization functionality.")
