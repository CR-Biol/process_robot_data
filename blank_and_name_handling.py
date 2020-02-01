import os
import logging
import re
from statistics import mean

import pandas as pd

import constants


# Initialize logger.
logger = constants.setup_logger(
    log_level=logging.DEBUG,
    logger_name=__name__
)

# ==============================================================================
# WRITE BLANK CORRECTED DATA
# ==============================================================================


class DataHandler:
    def __init__(self, path_to_file, blank_wells, use_fixed_od_blank,
                 exclude_blank_correction_for_reporter):
        self.od = {name: [] for name in constants.col_names}
        self.fu = {name: [] for name in constants.col_names}
        self.file = path_to_file
        self.blank_wells = blank_wells
        self.use_fixed_od_blank = use_fixed_od_blank
        self.exclude_blank_correction_for_reporter = \
            exclude_blank_correction_for_reporter

    def process(self):
        self.determine_shape_of_input_file()
        self.read_data_from_input_file()
        self.collect_blanks()
        self.calculate_relative_reporter_units()

    def determine_shape_of_input_file(self):
        """Read the input file to determine its shape.
        Sets the fields lines_od and lines_fu used by other methods.
        """
        seen_cycle = False
        total_cycle_number = 0
        with open(self.file) as file:
            for line in file:
                if seen_cycle:
                    try:
                        # dummy_curr_cycle_num assignment should fail after
                        # reading  OD data in the first "Stephan's" data sheet.
                        # dummy_curr_cycle_num = int(line.split(sep="\t")[0])
                        int(line.split(sep="\t")[0])
                        total_cycle_number += 1
                    except ValueError:
                        first_od = 2  # MAGIC NUMBER!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        last_od = first_od + total_cycle_number
                        self.lines_od = range(first_od, last_od + 1)
                        first_fu = last_od + 3
                        last_fu = first_fu + total_cycle_number
                        self.lines_fu = range(first_fu, last_fu + 1)
                        seen_cycle = False
                if line.startswith("Cycle"):
                    seen_cycle = True

    def read_data_from_input_file(self):
        with open(self.file) as file:
            for line_idx, line in enumerate(file):
                if line_idx in self.lines_od:
                    # Finds lines that correspond to OD data.
                    vals = line.strip().split()
                    for val_idx, val in enumerate(vals):
                        self.od[constants.col_names[val_idx]].append(
                            constants.parse_number(val))
                elif line_idx in self.lines_fu:
                    # Finds lines that correspond to reporter data.
                    vals = line.strip().split()
                    for val_idx, val in enumerate(vals):
                        self.fu[constants.col_names[val_idx]].append(
                            constants.parse_number(val))

    def collect_blanks(self):
        blanks_od = []
        blanks_fu = []
        for well in self.blank_wells:
            blanks_od += list(self.od[well])
            blanks_fu += list(self.fu[well])
        self.blank_mean_od = mean(blanks_od)
        self.blank_mean_fu = mean(blanks_fu)
        self.__handle_blank_exclusion()

    def __handle_blank_exclusion(self):
        if self.use_fixed_od_blank:
            logger.info(
                "Using fixed value for OD correction"
                + f"({constants.FIXED_OD_BLANK_VALUE})"
                + " instead of blank from data.")
            self.blank_mean_od = constants.FIXED_OD_BLANK_VALUE
        else:
            logger.info(f"Determined {self.blank_mean_od} as blank for OD.")

        if self.exclude_blank_correction_for_reporter:
            logger.info("Excluded blank correction for reporter values")
            self.blank_mean_fu = 0
        else:
            logger.info(f"Determined {self.blank_mean_fu} as blank for "
                        + "reporter values.")

    def blank_correct(self):
        for data_col in constants.data_names:
            self.od[data_col] = [constants.blank_correct(val,
                                                         self.blank_mean_od)
                                 for val in self.od[data_col]]
            self.fu[data_col] = [constants.blank_correct(val,
                                                         self.blank_mean_fu)
                                 for val in self.od[data_col]]

    def calculate_relative_reporter_units(self):
        for data_col in constants.data_names:
            self.fu[data_col] = [val for val in map(
                constants.relative,
                self.od[data_col],
                self.fu[data_col]
            )]


def get_wrappers(path_to_file, blank_wells, use_fixed_od_blank=False,
                 exclude_blank_correction_for_reporter=False):
    """Takes a preprocessed raw data file handler and a list of wells containing
    blank control as input. Returns a tuple containing wrapper dictionaries for
    OD and relative reporter units.
    """
    data_handler = DataHandler(path_to_file, blank_wells, use_fixed_od_blank,
                               exclude_blank_correction_for_reporter)
    data_handler.process()
    return data_handler.od, data_handler.fu


def write_blank_corrected(wrapper_dict, outfile):
    """Takes a wrapper dictionary containing data of OD or relative reporter
    units as input and writes it to Excel readible CSV outfile. Returns True
    to indicate successful completion for debugging purposes.
    """
    to_write = ""
    for key in wrapper_dict:
        to_write += key
        to_write += constants.SEP
        length_of_datapoints = len(wrapper_dict[key])
    to_write += "\n"
    for i in range(length_of_datapoints):
        for key in wrapper_dict:
            to_write += str(wrapper_dict[key][i]).replace(".", ",")
            to_write += constants.SEP
        to_write += "\n"

    with open(outfile, "w") as out:
        out.write(to_write)

    return True


def process_well_input(inp):
    """Prossses an input string of well IDs into a list.

    Syntax consists of using ',' as seperator and ':' for a series of wells.
    For example, the input string 'A1, B2, C1:C3' is processed to the list
    ['A1', 'B2', 'C1', 'C2', 'C3'].

    Another possibility is the integer-only notation. E.g., the input '12'
    will select wells A12, B12, ..., H12. This notation CANNOT BE COMBINED with
    other notations!
    """
    inp_list = parse_blank_well_entry_widget(inp)
    if not is_valid_well_input(inp_list):
        logger.error(f"Tried to use '{inp}' as input for blank wells.")
        raise ValueError(f"{inp} is no valid input for blank wells!")
    if (len(inp_list) == 1) and (":" not in inp_list[0]):
        return process_single_entry(inp_list[0])
    else:
        return process_multi_entry(inp_list)


def parse_blank_well_entry_widget(entry_input):
    return entry_input.replace(" ", "").upper().split(sep=",")


def is_valid_well_input(well_input_list):
    """Checks a list of strings representing wells whether they are valid wells
    of a 96well micro titer plate. Allows input shortcuts defined in
    process_well_input()."""
    valid_patterns = get_list_of_valid_compiled_patterns()
    for well_input in well_input_list:
        if not match_iterable(well_input, valid_patterns):
            return False
        if ":" in well_input:
            first, last = well_input.split(":")
            if int(first[1:]) >= int(last[1:]):
                return False
        try:
            row = int(well_input)
            if row > 12:
                return False
        except ValueError:
            pass
    return True


def get_list_of_valid_compiled_patterns():
    return [
        re.compile("[A-Ha-h][1-9]"),
        re.compile("[A-Ha-h]1[0-2]"),
        re.compile("[1-9]"),
        re.compile("1[0-2]"),
        re.compile("[A-Ha-h][1-9]:[A-Ha-h][1-9]|[A-Ha-h][1-9]:[A-Ha-h]1[0-2]"),
        re.compile("[A-Ha-h]1[0-2]:[A-Ha-h][1-9]|[A-Ha-h][1-9]:[A-Ha-h]1[0-2]")
    ]


def process_single_entry(well_input):
    try:  # Tries to parse the integer-only input variant.
        row = int(well_input)
        cols = "ABCDEFGH"
        selected = [col + str(row) for col in cols]
    except ValueError:  # Only a single well but no full column is intended.
        selected = [well_input]
    return selected


def process_multi_entry(inp_list):
    for input_ in list(inp_list):
        if ":" in input_:
            start, stop = input_.split(":")
            inp_list.remove(input_)
            start_idx = int(constants.data_names.index(start))
            stop_idx = int(constants.data_names.index(stop))
            all_ = constants.data_names[start_idx:stop_idx + 1]
            inp_list += all_
    return inp_list

# ==============================================================================
# BAPTIZE AND MERGE
# ==============================================================================


def baptize(data_file, name_csv, remove_quatation_marks_from_namefile):
    if remove_quatation_marks_from_namefile:
        constants.remove_double_quotest_from_file(name_csv)
    out_file = "".join(
        [os.path.basename(data_file).split(sep=".")[0], "_bap.csv"])
    label_dict = generate_label_dict(name_csv)
    to_write = get_baptized_file_content(data_file, label_dict)
    with open(out_file, "w") as out:
        out.write(to_write)


def generate_label_dict(name_csv):
    label_dict = {}
    with open(name_csv) as names:
        # Reads name_csv to generate label_dict
        for line in names.readlines():
            cell = line.split(sep=constants.SEP)
            if cell[0] in "ABCDEFGH" and cell[0] != "":
                starting_letter = cell[0]
                for i in range(1, 12+1):
                    coord = starting_letter + str(i)
                    elem = cell[i].strip()
                    label_dict[coord] = elem
    return label_dict


def get_baptized_file_content(data_file, label_dict):
    to_write = ""
    with open(data_file, "r") as data:
        for line in data.readlines():
            for cell in line.split(sep=constants.SEP):
                if cell in label_dict:
                    to_write += label_dict[cell]
                else:
                    to_write += cell.strip()
                to_write += constants.SEP
            to_write += "\n"
    return to_write


def merge(csv_file_list, outfile="merge_default_name.csv", write=False):
    """Takes a list of CSV files (Excel generated) as input and returns a
    pandas dataframe containing all data. If write is set to True, writes
    Excel readible CSV file as outfile.
    """
    frames = [pd.read_csv(f, sep=constants.SEP) for f in csv_file_list]
    result = pd.concat(frames, axis=1)
    result = sort_df(result)
    if write:
        result.to_csv(outfile, sep=constants.SEP)
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
    Returns a sorted DataFrame with "cycle", "time", and "temp" as first
    columns and all other columns sorted lexographically. Entries containing
    the strings "Unnamend", "medium", and "blank" are removed from the returned
    DataFrame.

    This function is supposed to be called upon a baptized DataFrame.
    """
    primary_df = process_input_to_primary_dataframe(dataframe_or_csv_file)
    to_keep = generate_filtering_list(primary_df)
    secondary_df = primary_df[to_keep]
    secondary_df.drop_duplicates()
    return secondary_df


def process_input_to_primary_dataframe(dataframe_or_csv_file):
    if isinstance(dataframe_or_csv_file, pd.DataFrame):
        primary_df = dataframe_or_csv_file
    elif isinstance(dataframe_or_csv_file, str):
        primary_df = pd.read_csv(
            dataframe_or_csv_file, delimiter=constants.SEP)
    else:
        raise ValueError("".join([
            "Input for dataframe_or_csv_file must be a ",
            "DataFrame or path to a CSV file"
        ]))
    return primary_df


def generate_filtering_list(primary_df):
    # Define what entries to remove from the CSV file and compiling REs
    discard_from_df = ["Unnamed", "medium", "blank"]  # , "empty"]
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
    return to_keep


if __name__ != "__main__":
    print("\tInitialized blank correction module.")
