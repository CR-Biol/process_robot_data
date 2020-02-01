import os
import logging

import tkinter as tk
# from tkinter import ttk
from tkinter.filedialog import askdirectory

import constants
import get_raw_data_asc
import get_raw_data_excel
import get_raw_data_hamilton
import blank_and_name_handling
import quality

# Initialize logger.
logger = constants.setup_logger(
    log_level=logging.DEBUG,
    logger_name=__name__
    )


def read_raw_data(raw_data_dir, reporter_name):
    path_to_file_dir = raw_data_dir
    os.chdir(path_to_file_dir)
    all_files = [file for file in os.listdir()]
    for file in all_files:
        if ".asc" in file:
            logger.info("Found asc files. Expecting data from TECAN robot.")
            return get_raw_data_asc.read_raw_data(reporter_name)
        elif ".xlsx" in file:
            logger.info("Found xlsx files. Expecting data from TECAN reader"
                        + " in Excel format.")
            return get_raw_data_excel.read_raw_data(
                reporter_name=reporter_name)
        elif ".xls" in file:
            logger.info("Found xls files. Expecting data from Hamilton robot.")
            return get_raw_data_hamilton.read_raw_data(reporter_name)


class GUIRawDataProcessing():
    def __init__(self, parent, grand_parant, *args, **kwargs):
        self.parent = parent
        self.grand_parant = grand_parant
        self.frame = tk.Frame(grand_parant)
        self.parent.nb.add(self.frame, text="Raw Data")

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

        self.fixed_blank = tk.BooleanVar()
        self.fixed_blank.set(False)
        self.exclude_reporter_blank = tk.BooleanVar()
        self.exclude_reporter_blank.set(False)

        # Variables filled within program flow
        self.has_datadir = tk.IntVar()
        self.has_namedir = tk.IntVar()

        self.first_step_complete = tk.StringVar()
        self.second_step_complete = tk.StringVar()
        self.third_step_complete = tk.StringVar()

        self.intro_label = tk.Label(
            self.frame, text="Welcome to One Click to Tabular Format."
                             + "\nPlease chose configuration as appropriate."
                             + " Make sure to define all data files as needed."
                             + "\nLastly, start by hitting 'run'.")

        # Define widgets WITHOUT positioning
        self.raw_data_button = tk.Button(
            self.frame,
            text="Set Raw Data Folder",
            command=lambda: self.set_dir(self.raw_data_dir, self.has_datadir)
            )
        self.names_button = tk.Button(
            self.frame,
            text="Set Name Files Folder (Optional)",
            command=lambda: self.set_dir(self.path_to_namefiles,
                                         self.has_namedir)
            )
        self.subframe = tk.Frame(self.frame)  # Subframe for symmetric buttons
        self.reset_button = tk.Button(
            self.subframe,
            text="Reset",
            command=self.reset
            )
        self.run_button = tk.Button(
            self.subframe,
            text="Run",
            command=self.run
            )
        self.exit_button = tk.Button(
            self.subframe,
            text="Close",
            command=self.parent.end_app
            )
        self.reporter_entry = tk.Entry(self.frame,
                                       textvariable=self.reporter_name)
        self.reporter_label = tk.Label(self.frame, text="Reporter Name:")
        self.blank_entry = tk.Entry(self.frame, textvariable=self.blank_wells)
        self.blank_label = tk.Label(self.frame, text="Blank Wells:")
        self.has_datadir_check = tk.Checkbutton(
            self.frame,
            text="Has Data Directory",
            variable=self.has_datadir,
            state=tk.DISABLED
            )
        self.has_namedir_check = tk.Checkbutton(
            self.frame,
            text="Has Name File Directory",
            variable=self.has_namedir,
            state=tk.DISABLED
            )
        self.fixed_blank_button = tk.Checkbutton(
            self.frame,
            text="Use fixed blank for OD values",
            variable=self.fixed_blank,
            onvalue=True,
            offvalue=False
            )
        self.exclude_reporter_blank_button = tk.Checkbutton(
            self.frame,
            text="Do not use blank-correction for reporter",
            variable=self.exclude_reporter_blank,
            onvalue=True,
            offvalue=False
            )

        self.dummy_label = tk.Label(self.frame, text="")
        self.label_organize_raw_data = tk.Label(self.frame, textvariable=self.first_step_complete)
        self.label_perform_blank_correction = tk.Label(self.frame, textvariable=self.second_step_complete)
        self.label_name_columns_and_merge_files = tk.Label(self.frame, textvariable=self.third_step_complete)

        # Defining tooltips
        constants.ToolTip(
            self.raw_data_button,
            "Set your raw data directory."
            )
        constants.ToolTip(
            self.names_button,
            "Set your name file directory.\nThe directory may only contain "
            + "name files in CSV format (see Help/Files for Naming)"
            )
        constants.ToolTip(
            self.exclude_reporter_blank_button,
            "Do not use blank correction on raw reporter values."
            + "\nThis option is NOT recommended when using fluorescence!"
            )
        constants.ToolTip(
            self.fixed_blank_button,
            f"Use a fixed value ({constants.FIXED_OD_BLANK_VALUE}) for OD "
            + "blank correction.\nThis option is intended for use when "
            + "analysing imperfect runs.\nNote that the assumed value of the "
            + "OD blank is based on experience.\n\nThis option is generally "
            + "NOT RECOMMENDED."
            )

        # Positioning widgets
        self.intro_label.grid(row=0, column=0, rowspan=3, columnspan=5,
                              ipady=10, ipadx=5)

        self.dummy_label.grid(row=3)

        self.reporter_label.grid(row=4, column=0, stick=tk.E)
        self.reporter_entry.grid(row=4, column=1, columnspan=2)
        self.configure_btn(self.raw_data_button,
                           btn_width=constants.BTN_WIDTH_BIG)
        self.raw_data_button.grid(row=4, column=3, padx=5, pady=10)
        self.has_datadir_check.grid(row=4, column=4, sticky=tk.W)

        self.blank_label.grid(row=5, column=0, stick=tk.E)
        self.blank_entry.grid(row=5, column=1, columnspan=2)
        self.configure_btn(self.names_button,
                           btn_width=constants.BTN_WIDTH_BIG)
        self.names_button.grid(row=5, column=3, padx=5)
        self.has_namedir_check.grid(row=5, column=4, sticky=tk.W)

        self.fixed_blank_button.grid(row=6, column=2, columnspan=2, pady=7,
                                     sticky=tk.W)
        self.exclude_reporter_blank_button.grid(row=7, column=2, columnspan=2,
                                                pady=5, sticky=tk.W)

        self.label_organize_raw_data.grid(row=8, columnspan=5)
        self.label_perform_blank_correction.grid(row=9, columnspan=5)
        self.label_name_columns_and_merge_files.grid(row=10, columnspan=5)

        self.subframe.grid(row=11, columnspan=5)
        self.configure_btn(self.run_button)
        self.run_button.grid(row=0, column=0, pady=5, padx=5)
        self.configure_btn(self.reset_button)
        self.reset_button.grid(row=0, column=1, pady=5, padx=5)
        self.configure_btn(self.exit_button)
        self.exit_button.grid(row=0, column=2, pady=5, padx=5)

    def configure_btn(self, btn_widget, btn_width=constants.BTN_WIDTH_NORMAL):
        btn_widget.configure(
            width=btn_width,
            font=(constants.FONT_FAMILY, constants.FONT_SIZE, "bold"),
            cursor="hand2",
            background="#bbb",
            activebackground="#4c4c4c"
        )

    def set_dir(self, dir_var, corresponding_bool_var):
        path = askdirectory()
        dir_var.set(path)
        if dir_var.get() not in ("", "not_defined"):
            corresponding_bool_var.set(1)
            logger.debug("Set a path to {}".format(path))
        else:
            logger.debug("Tried to set a path variable, but received invalid"
                         + " input.")

    def organize_raw_data(self):
        """Read Data. Corresponds to Stephan's original Perl script."""
        logger.info("Started reordering data into uniform TSV (Stephan's "
                    + "script.")
        self.written_barcodes = read_raw_data(self.raw_data_dir.get(),
                                              self.reporter_name.get())
        if not self.written_barcodes:
            logger.error("Could not read barcodes in data files.")
            error_msg = "ERROR:DID NOT RETRIEVED ANY BARCODES. ANALYSIS ENDED."
            self.first_step_complete.set(error_msg)
            return False

        written_barcodes_as_str = ", ".join(self.written_barcodes)
        logger.info("Written uniform TSV for barcodes "
                    + f"{written_barcodes_as_str}")
        msg = f"Successfully written barcodes for: {written_barcodes_as_str}"
        self.first_step_complete.set(msg)
        return True

    def perform_blank_correction(self):
        """Blank Correction."""
        blanks = blank_and_name_handling.process_well_input(
            self.blank_wells.get())
        logger.info(
            f"Started blank correction using {blanks} as blank(s).")
        raw_files = [file for file in os.listdir() if "results.txt" in file]
        has_written_blank_corrected_file = False
        for file in raw_files:
            file_basename = file.split(sep=".")[0]
            od, rru = blank_and_name_handling.get_wrappers(
                file,
                blanks,
                self.fixed_blank.get(),
                self.exclude_reporter_blank.get()
                )
            blank_and_name_handling.write_blank_corrected(
                od, file_basename + "_OD_corrected.csv"
                )
            blank_and_name_handling.write_blank_corrected(
                rru,
                file_basename
                + f"_relative_{self.reporter_name.get()}_corrected.csv"
                )
            if not has_written_blank_corrected_file:
                has_written_blank_corrected_file = True

        if not has_written_blank_corrected_file:
            logger.error("Unable to write blank corrected files.")
            error_msg = "ERROR: NO BLANK CORRECTED FILES WERE WRITTEN." \
                + "ANALYSIS ENDED."
            self.second_step_complete.set(error_msg)
            return False
        logger.info("Sucessfully written blank corrected files.")
        self.second_step_complete.set("All blank corrected files written.")
        return True

    def name_columns_and_merge_files(self):
        """Optional step: Naming and merging with specified naming CSVs."""
        logger.info("Started optional naming and merging of blank corrected"
                    + " files.")
        namefiles = [os.path.join(self.path_to_namefiles.get(), file)
                     for file in os.listdir(self.path_to_namefiles.get())
                     ]
        # Correct Excel TAB character bug:
        temp = [quality.is_name_file_csv(name_file) for name_file in namefiles]
        if (not temp == namefiles) and self.name_files_are_csv:
            logger.warning(
                "Name files are not formatted as expected (CSVs with"
                + f"{constants.SEP} as seperator)."
                + "Expecting TSV format, trying to resolve name files."
                )
            self.name_files_are_csv = False
            constants.LabelWindow(
                self.frame,
                "Your name files have been TSV formatted due to an Excel bug."
                + "\nThe bug has been caught and corrected for this run.\n"
                + "\nPlease clean up your name file directory before the next"
                + "run!",
                title="Warning: Error in Name File!"
                )

        namefiles = temp

        corrected_files = [file for file in os.listdir()
                           if "corrected" in file and "bap" not in file]

        if len(self.written_barcodes) != len(namefiles):
            logger.error("Encountered unequal numbers of corrected data files"
                         + " and name files.")
            self.third_step_complete.set(
                "ERROR: More or less encountered"
                + "barcodes than name files!\n"
                + "ANALYSIS ENDED!"
                )
            return False

        barcode_to_file = {
            self.written_barcodes[i]: namefiles[i] for i in range(
                len(self.written_barcodes))
            }
        for barcode in barcode_to_file:
            for file in corrected_files:
                if barcode in file:
                    blank_and_name_handling.baptize(
                        data_file=file,
                        name_csv=barcode_to_file[barcode],
                        remove_quatation_marks_from_namefile=self.parent.remove_quotation_marks.get()
                        )
                    logger.debug("Baptized data for {}".format(barcode))

        # Merge and Sort final output files
        od = [file for file in os.listdir() if "OD" in file and "bap" in file]
        rfu = [file for file in os.listdir()
               if "relative" in file and "bap" in file]
        if len(od) > 1:
            blank_and_name_handling.merge(
                od,
                outfile="all_OD.csv",
                write=True
                )
            blank_and_name_handling.merge(
                rfu,
                outfile="all_relative_{}.csv".format(self.reporter_name.get()),
                write=True
                )
            logger.info("Merged and sorted all corrected data files.")
        else:
            od_dataframe = blank_and_name_handling.sort_df(od[0])
            od_dataframe.to_csv("sorted_OD.csv", sep=constants.SEP)
            rfu_dataframe = blank_and_name_handling.sort_df(rfu[0])
            rfu_dataframe.to_csv(
                "sorted_relative_{}.csv".format(self.reporter_name.get()),
                sep=constants.SEP
                )
            logger.info("Sorted corrected data file.")
        self.third_step_complete.set("Naming and sorting of data complete.")
        return True

    def run(self):
        # Read Data
        logger.debug("Started read raw data run.")
        first_step_completed = self.organize_raw_data()
        if not first_step_completed:
            logger.error("Could not finish raw data read-out (step 1).")
            return
        if " " in self.reporter_name.get():
            self.reporter_name.set(self.reporter_name.get().replace(" ", "_"))
            logger.info("Removed whitespace from reporter name: "
                        + f"{self.reporter_name.get()}")
        second_step_completed = self.perform_blank_correction()
        if not second_step_completed:
            logger.error("Could not finish blank-correction (step 2).")
            return

        # This step is entirely optional. If no path to naming files is set,
        #  this part will be skipped without raising any errors.
        if self.path_to_namefiles.get() != "not_defined":
            third_step_completed = self.name_columns_and_merge_files()
            if not third_step_completed:
                logger.error("Could not finish baptizing and merging files"
                             + " (step 3).")
                return
        self.name_files_are_csv = True
        logger.debug("Finished read raw data run.")

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
        logger.debug("Reset internal information to default values.")


if __name__ != "__main__":
    print("\tInitialized raw data handling module.")
