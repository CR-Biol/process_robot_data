
import os
import logging
import datetime

import constants


# Initialize logger.
logger = constants.setup_logger(
    log_file_name = __name__ + ".log",
    log_level = logging.DEBUG,
    logger_name = __name__
    )



def time_from_asc(line):
    """Takes a line from the .asc file containing information about time.
    Returns a datetime-object with:
    (year, month, day, hour, min, sec)

    Requires datetime module.
    """
    try:
        date, time = line.split(sep=", ")
        date = date.split(sep = ": ")[1]
        time = time.split(sep = ": ")[1]
        year, month, day = date.split(sep="-")
        hour, min, sec = time.split(sep=":")
        year, month, day, hour, min, sec = [int(dummy) for dummy in (year, month, day, hour, min, sec)]
    except IndexError:
        raise ValueError("Cannot read time from line" + line + "\nPlease check if the format of the robot files has changed!")
    return datetime.datetime(year, month, day, hour, min, sec)


def read_raw_data(reporter_name, appendix="_results.txt"):

    written_barcodes = [] # List for user feedback

    # Iterating through data dict to get barcodes and file timestemps.
    all_files = [file for file in os.listdir() if file.endswith("asc")]
    barcodes = []
    before_barcodes = []
    highest_timepoint = 0
    for file in all_files:
        barcode = file.split(sep = "_")[2]
        before_barcode = file[:file.index(barcode)]
        timepoint = int(file.split(sep = "_")[3].split(sep = ".")[0])
        if not barcode in barcodes:
            barcodes.append(barcode)
            before_barcodes.append(before_barcode)
        if timepoint > highest_timepoint:
            highest_timepoint = timepoint # Note 0-indexing!

    # Determine data file read-out order to follow: A1, A2, ..., B1, B2, ...
    line_order = [1, 9, 17, 25, 33, 41, 49, 57, 65, 73, 81, 89, 2, 10, 18, 26, 34,
                  42, 50, 58, 66, 74, 82, 90, 3, 11, 19, 27, 35, 43, 51, 59, 67,
                  75, 83, 91, 4, 12, 20, 28, 36, 44, 52, 60, 68, 76, 84, 92, 5,
                  13, 21, 29, 37, 45, 53, 61, 69, 77, 85, 93, 6, 14, 22, 30, 38,
                  46, 54, 62, 70, 78, 86, 94, 7, 15, 23, 31, 39, 47, 55, 63, 71,
                  79, 87, 95, 8, 16, 24, 32, 40, 48, 56, 64, 72, 80, 88, 96]

    for barcode in barcodes:
        # Reading data files.
        first = True
        od_list = ["OD600\n", constants.header]
        od = ""

        fu_list = [reporter_name + "\n", constants.header]
        fu = ""

        for i in range(highest_timepoint + 1):
            # Iteration of each .asc file beginning at file 0.
            file = before_barcodes[barcodes.index(barcode)] \
                   + barcode \
                   + "_" \
                   + str(i) \
                   + ".asc"
            with open(file, "r") as f:
                file_lines = f.readlines()
                last_line = file_lines[-1]
                temperature = file_lines[-2].split(sep = ":")[-1].strip().split()[0]
                time_of_data = time_from_asc(last_line)
                if first:
                    first_time = time_of_data
                    first = False
                time_in_min = (time_of_data - first_time).total_seconds() / 60

                cyc_time_temp = str(i) + "\t" \
                                + str(round(time_in_min, 2)) + "\t" \
                                + temperature + "\t"
                od += cyc_time_temp
                fu += cyc_time_temp

                for line in line_order:
                    current_od = file_lines[line].split()[1].replace(",", ".")
                    current_fu = file_lines[line].split()[2].replace(",", ".")

                    # Removes exponential notation (e.g. "3.502e+003")
                    #  and writes decimal numbers or integers, respectively.
                    if "." in current_od:
                        od += str(float(current_od)) + "\t"
                    else:
                        od += str(int(current_od)) + "\t"
                    if "." in current_fu:
                        fu += str(float(current_fu)) + "\t"
                    else:
                        fu += str(int(current_fu)) + "\t"
                od += "\n"
                fu += "\n"

        od_list.append(od)
        od_list.append("\n") # Seperates OD and reporter
        fu_list.append(fu)

        # Writing output/results
        output_file = before_barcode + barcode + appendix
        with open(output_file, "w") as f:
            for entry in od_list:
                f.write(entry)
            for entry in fu_list:
                f.write(entry)

        written_barcodes.append(barcode)
    return written_barcodes
