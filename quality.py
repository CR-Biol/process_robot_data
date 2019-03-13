"""Quality checks for for all input files."""

import os
import logging

import constants


# Initialize logger.
logger = constants.setup_logger(
    log_file_name = __name__ + ".log",
    log_level = logging.DEBUG,
    logger_name = __name__
    )



def check_name_file(name_file):
    pass


def is_name_file_csv(name_file):
    with open(name_file) as infile:
        for line in infile:
            if constants.SEP in line:
                return name_file
            elif "\t" in line:
                return rewrite_tsv(name_file)



def rewrite_tsv(name_file):
    """Takes a truncated CSV name file as input.
    Re-writes all Excel induced tab characters to valid seperators as specified
    in constants.py in a new file and returns that file name."""

    csv_file_name = name_file.split(sep=".")[:-1][0] + "_as_csv.csv"
    to_write = ""

    for corrected_line in tabs_to_seps(name_file):
        to_write += corrected_line
    with open(csv_file_name, "w") as outfile:
        outfile.write(to_write)

    return csv_file_name


def tabs_to_seps(file):
    with open(file, "r") as f:
	    for line in f:
		    yield line.replace("\t", constants.SEP)
