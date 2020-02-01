import os
import logging
import math
from statistics import mean

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilename

import constants

# Initialize logger.
logger = constants.setup_logger(
    log_level=logging.DEBUG,
    logger_name=__name__
)

INDUCTION_TIME_IN_MIN = 220
NUM_REPLICATES = 3
DATA_DIR = os.getcwd()


class GUIDoseResponseGUI:
    def __init__(self, parent, grand_parent, *args, **kwargs):
        self.grand_parent = grand_parent
        self.frame = tk.Frame(grand_parent)
        self.parent = parent
        self.parent.nb.add(self.frame, text="Dose Response")


class DoseResponseCurve:
    """Representation of data points measured during a dose-response curve.
    Is initialized from a headlined CSV file that contains information about
    a time point in the first column and data for different conditions in a
    number of replicates in the following columns. No additional meta
    information should be contained in these CSVs.
    """
    def __init__(
            self,
            input_csv_file,
            sep_in_csv=";",
            induction_time=INDUCTION_TIME_IN_MIN,
            num_replicates=NUM_REPLICATES):
        """Initialize DoseResponseCurve from a data CSV."""
        self.num_replicates = num_replicates
        self.name = os.path.splitext(os.path.basename(input_csv_file))[0]
        self.ind_time = induction_time
        self.__sep = sep_in_csv
        self.__path = input_csv_file
        self.data = self.__read_infile()

    def __repr__(self):
        return (f"DoseResponseCurve of {self.name} with {self.num_replicates} "
                + f"replicates and {len(self.data)} data points")

    def __read_infile(self):
        data_constructor = {}
        with open(self.__path) as infile:
            for i, line in enumerate(infile):
                if i == 0:  # Read Headline.
                    self.conditions = [any_string for any_string
                                       in line.strip().split(self.__sep)[1:]
                                       if any_string]
                    continue
                cells = line.split(self.__sep)
                current_time_point = constants.parse_number(cells[0])
                data_by_replicates = self.__get_values_from_cells(cells)

                data_constructor = self.__add_timepoint(data_constructor,
                                                        current_time_point,
                                                        data_by_replicates)
        return data_constructor

    def __get_values_from_cells(self, list_of_cells):
        """Takes a FULL list of cells read from the input CSV that is NOT the
        headline as input.
        Returns a list of lists where the inner lists correspond to biological
        replicates.
        """
        list_of_lists = []
        inner_list = []
        for i, cell in enumerate(list_of_cells[1:]):
            data_point = constants.parse_number(cell)
            inner_list.append(data_point)
            if (i + 1) % self.num_replicates == 0:  # self.num_replicates:
                list_of_lists.append(list(inner_list))
                inner_list = []
        self.__validate_inner_list(list_of_lists)
        return list_of_lists

    def __validate_inner_list(self, master_list):
        assert master_list
        for inner_list in master_list:
            assert len(inner_list) == self.num_replicates

    def __add_timepoint(self, data_dict, time_point, data_by_replicates):
        mod_dict = data_dict.copy()
        sub_dict = {condition: data for condition, data
                    in zip(self.conditions, data_by_replicates)}
        mod_dict[time_point] = sub_dict
        return mod_dict

    def dynamic_range_at(self, time_point):
        time_point_key = self.__select_closest_key_from_time_point(time_point)
        try:
            high = mean(self.data[time_point_key]["500 uM"])
            low = mean(self.data[time_point_key]["0 uM"])
        except KeyError:
            high = mean(self.data[time_point_key]["500"])
            low = mean(self.data[time_point_key]["0"])
        return self.__safe_divide(high, low)

    def __select_closest_key_from_time_point(self, time_point):
        min_diff = float("inf")
        for valid_time_point in self.data.keys():
            difference = abs(time_point - valid_time_point)
            if difference < min_diff:
                min_diff = difference
                closest = valid_time_point
        return closest

    def time_delay(self):
        """Calculates the time delay as defined by Pinto et al. (2018):
        'The time delay in gene induction was defined as the difference between
        the time at which the luciferase activity first exceeded its average
        pre-induction value by 2-fold, and the time point ofinducer addition.'
        """
        response_treshold = 2 * self.mean_before_induction()
        time_of_threshold_reached = None
        for time, measurement_point in self.data.items():
            try:
                response = mean(measurement_point["500 uM"])
            except KeyError:
                response = mean(measurement_point["500"])
            if response >= response_treshold and time > self.ind_time:
                time_of_threshold_reached = time
                break
        if time_of_threshold_reached is None:  # Happens with inactive switches
            time_delay = -1
        else:
            time_delay = time_of_threshold_reached - self.ind_time
        return time_delay

    def mean_before_induction(self):
        time_point_key = self.__select_closest_key_from_time_point(
            self.ind_time)
        # print(f"Instead of {self.ind_time}, showing dynamic range at {time_point_key}")
        at_ind_time = self.data[time_point_key]
        all_values_before_induction = []
        for data in at_ind_time.values():
            all_values_before_induction += data
        return mean(all_values_before_induction)

    def __safe_divide(self, divident, divisor):
        try:
            return divident / divisor
        except ZeroDivisionError:
            return math.nan


def data_in_directory():
    for file in get_all_csv_names():
        yield DoseResponseCurve(file)


def get_all_csv_names():
    return [os.path.join(DATA_DIR, file) for file in os.listdir(DATA_DIR)
            if ".csv" in file and not "all_relative_lux" in file]


def construct_csv(list_of_dose_responses, sep=";"):
    """Takes a list of DoseResponseCurve objects and returns data about them in 
    a human (sep="\t") or Excel (sep=";") readable format.
    """
    csv_constructor = sep.join((
        "Name",
        "Mean Before Induction",
        "Time Delay [min]",
        "Dynamic Range at t=840",
        "Dynamic Range at t=1120"))
    csv_constructor += "\n"
    for drc in list_of_dose_responses:
        csv_constructor += sep.join((
            drc.name,
            constants.num_to_str(round(drc.mean_before_induction())),
            constants.num_to_str(round(drc.time_delay())),
            constants.num_to_str(round(drc.dynamic_range_at(840), 2)),
            constants.num_to_str(round(drc.dynamic_range_at(1120), 2))))
        csv_constructor += "\n"
    return csv_constructor


if __name__ == "__main__":
    print(construct_csv([drc for drc in data_in_directory()], sep="\t"))


if __name__ != "__main__":
    print("\tInitialized dose-response curve functionality.")
