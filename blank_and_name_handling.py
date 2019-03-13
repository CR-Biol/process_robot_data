import os
import logging
import re
import datetime
from statistics import mean, stdev

import pandas as pd
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



#==============================================================================
# WRITE BLANK CORRECTED DATA
#==============================================================================

def process_well_input(inp):
    """Prossses an input string of well IDs into a list.

    Syntax consists of using ',' as seperator and ':' for a series of wells.
    For example, the input string 'A1, B2, C1:C3' is processed to the list
    ['A1', 'B2', 'C1', 'C2', 'C3'].
    """
    inp_list = inp.replace(" ", "").upper().split(sep = ",")

    if len(inp_list) == 1:
        try:
            row = int(inp_list[0])
            cols = "ABCDEFGH"
            selected = [col + str(row) for col in cols]
            return selected
        except ValueError:
            pass

    for i in list(inp_list):
        if ":" in i:
            start, stop = i.split(":")
            inp_list.remove(i)
            start_idx = int(constants.data_names.index(start))
            stop_idx = int(constants.data_names.index(stop))
            all = constants.data_names[start_idx:stop_idx + 1]
            inp_list += all

    for elem in inp_list:
        if elem not in constants.data_names:
            raise ValueError
    if inp_list is None:
        raise ValueError

    return inp_list


def get_wrappers(path_to_file, blank_wells, use_fixed_od_blank=False):
    """Takes a preprocessed raw data file handler and a list of wells containing
    blank control as input. Returns a tuple containing wrapper dictionaries for
    OD and relative reporter units.

    Processing in this function includes blank substraction and calculation of
    relative reporter units.
    """
    # Wrapper dictionaries for data storage.
    wrapper_od = {name: [] for name in constants.col_names}
    wrapper_fu = {name: [] for name in constants.col_names}

    with open(path_to_file) as file:
        # Opens data sheet for the first time to determine size of data points
        seen_cycle = False
        total_cycle_number = 0
        for line in file:
            if seen_cycle:
                try:
                    curr_cycle_num = int(line.split(sep = "\t")[0])
                    total_cycle_number += 1
                except ValueError:
                    first_od = 2 # MAGIC NUMBER!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

                    last_od = first_od + total_cycle_number
                    lines_od = range(first_od, last_od + 1)

                    first_fu = last_od + 3
                    last_fu = first_fu + total_cycle_number
                    lines_fu = range(first_fu, last_fu + 1)
                    seen_cycle = False

            if line.startswith("Cycle"):
                seen_cycle = True


    with open(path_to_file) as file:
        for line_idx, line in enumerate(file):
            if line_idx in lines_od:
                # Finds lines that correspond to OD data.
                vals = line.strip().split()
                for val_idx, val in enumerate(vals):
                    wrapper_od[constants.col_names[val_idx]].append(float(val.replace(",", ".")))
            elif line_idx in lines_fu:
                # Finds lines that correspond to reporter data.
                vals = line.strip().split()
                for val_idx, val in enumerate(vals):
                    wrapper_fu[constants.col_names[val_idx]].append(float(val.replace(",", ".")))

    # Collecting all blank values for blank correction
    all_blanks_od = []
    all_blanks_fu = []

    for well in blank_wells:
        all_blanks_od += list(wrapper_od[well])
        all_blanks_fu += list(wrapper_fu[well])

    # Mean over all blank values
    blank_mean_od = mean(all_blanks_od)
    blank_mean_fu = mean(all_blanks_fu)

    if use_fixed_od_blank:
        # Value given by experience. Use this option only for testing or if there
        #  is a strong reason behind not using measured blanks!!
        blank_mean_od = 0.039

    
    def relative(od_val, fu_val):
        """Mapping function needed to catch ZeroDivisionErrors."""
        try:
            return fu_val / od_val
        except ZeroDivisionError:
            return 0

    def cap_negative_values_to_zero(list):
        for item in list:
            if item > 0:
                yield item
            else:
                yield 0

    for data_col in constants.data_names:
        # Substracting mean blank from all values (including the blank itself).
        wrapper_od[data_col] = [val for val in map(
            lambda x: x - blank_mean_od, 
            wrapper_od[data_col]
            )]
        wrapper_fu[data_col] = [val for val in map(
            lambda x: x - blank_mean_fu, 
            wrapper_fu[data_col]
            )]
        wrapper_od[data_col] = [item for item in cap_negative_values_to_zero(wrapper_od[data_col])]
        wrapper_fu[data_col] = [item for item in cap_negative_values_to_zero(wrapper_fu[data_col])]
        # Calculating relative reporter units
        wrapper_fu[data_col] = [val for val in map(
            relative,
            wrapper_od[data_col],
            wrapper_fu[data_col]
            )]
    return wrapper_od, wrapper_fu


def write_blank_corrected(wrapper_dict, outfile):
    """Takes a wrapper dictionary containing data of OD or relative reporter
    units as input and writes it to Excel readible CSV outfile. Returns True for
    debugging purposes.
    """
    to_write = ""
    for key in wrapper_dict:
        to_write += key
        to_write += ";"
        length_of_datapoints = len(wrapper_dict[key])
    to_write += "\n"
    for i in range(length_of_datapoints):
        for key in wrapper_dict:
            to_write += str(wrapper_dict[key][i]).replace(".", ",")
            to_write += ";"
        to_write += "\n"

    with open(outfile, "w") as out:
        out.write(to_write)

    return True


#==============================================================================
# BAPTIZE AND MERGE
#==============================================================================

def baptize(data_file, name_csv):
    label_dict = {}

    to_write = ""
    out_file = "".join([os.path.basename(data_file).split(sep=".")[0], "_bap.csv"])

    with open(name_csv) as names:
        # Reads name_csv to generate label_dict
        for line in names.readlines():
            items = line.split(sep = constants.SEP)
            if items[0] in "ABCDEFGH" and items[0] != "": # '"" in string' is always 'True'
                starting_letter = items[0]
                for i in range(1, 12+1):
                    coord = starting_letter + str(i)
                    elem = items[i].strip()
                    label_dict[coord] = elem

    with open(data_file, "r") as data:
        for line in data.readlines():
            for item in line.split(sep = constants.SEP):
                if item in label_dict:
                    to_write += label_dict[item]
                else:
                    to_write += item.strip()
                to_write += ";"
            to_write += "\n"

    with open(out_file, "w") as out:
        out.write(to_write)


def merge(csv_file_list, outfile="merge_default_name.csv", write=False):
    """Takes a list of CSV files (Excel generated) as input and returns a
    pandas dataframe containing all data. If write is set to True, writes
    Excel readible CSV file as outfile.
    """
    frames = [pd.read_csv(f, sep = constants.SEP) for f in csv_file_list]
    result = pd.concat(frames, axis=1)
    result = sort_df(result)
    if write:
        result.to_csv(outfile, sep = constants.SEP)
    return result


def match_iterable(string, pattern_list):
    """Matches a string to a list of compiled regex patterns.
    Returns True if the input string matches any pattern in pattern_list.
    Retunrs False otherwise.
    """
    for compiled_pattern in pattern_list:
        if compiled_pattern.match(string):
            return True
    return False


def sort_df(dataframe_or_csv_file):
    """Takes a DataFrame or an Excel CSV file handler as input.
    Returns a sorted DataFrame with "cycle", "time", and "temp" as first columns
    and all other columns sorted lexographically. Entries containing the strings
    "Unnamend", "medium", "blank", and "empty" are removed from the returned
    DataFrame.

    This function is supposed to called upon a baptized DataFrame.
    """
    # Get primary_df from input: Either from a DataFrame directly or a path string.
    if isinstance(dataframe_or_csv_file, pd.DataFrame):
        primary_df = dataframe_or_csv_file
    elif isinstance(dataframe_of_csv_file, str):
        primary_df = pd.read_csv(dataframe_or_csv_file, delimiter = constants.SEP)
    else:
        raise ValueError("".join([
            "Input for dataframe_or_csv_file must be a ",
            "DataFrame or path to a CSV file"
            ]))

    # Define what entries to remove from the CSV file and compiling respective RE
    discard_from_df = ["Unnamed", "medium", "blank"]#, "empty"]
    discard_patterns = [re.compile(entry) for entry in discard_from_df]
    keep_once = ["cycle", "time", "temp"]
    keep_patterns = [re.compile(string) for string in keep_once]
    for pattern in discard_patterns:
        keep_patterns.append(pattern)

    # CREATE SORTER LIST
    # Remove unwanted entries and duplications from primary_df
    to_keep = [entry for entry in primary_df
              if not match_iterable(entry, keep_patterns)
              ]
    # Sort indeces in to_keep
    to_keep.sort()

    # Insert entries that should be kept once to the beginning of to_keep
    for entry in keep_once:
        to_keep.insert(0, entry)

    # Create and return secondary_df
    secondary_df = primary_df[to_keep] # Filters and sorts columns according to to_keep
    secondary_df.drop_duplicates()
    return secondary_df
