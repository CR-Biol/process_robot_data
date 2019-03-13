import os
import logging

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory, askopenfilename

import constants


# Initialize logger.
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # DEBUG, INFO, WARNING, ERROR, CRITICAL
formatter = constants.LOG_FORMATTER
if not os.path.exists("logs"):
    os.makedirs("logs")
log_file_handler = logging.FileHandler(os.path.join("logs", "deconvolution.log"))
log_file_handler.setFormatter(formatter)
logger.addHandler(log_file_handler)



class IntegrateDeconvolutionAlgorithm:
    def __init__(self, other, parent, *args, **kwargs):
        self.parent = parent
        self.frame = tk.Frame(parent)
        other.nb.add(self.frame, text="MatLab Conversions")


        welcome_label = tk.Label(
            self.frame,
            text = "Incorporate the MatLab deconvultion " \
            + "algorithm to OCUTaF.\n Chose your raw data folder " \
            + "to generate MatLab compatible TECAN files.\n" \
            + "Use the file from the MatLab analysis together " \
            + "with optional naming files to generate standard output."
            )

        self.reporter_name = tk.StringVar()
        self.reporter_name.set("LUX")

        self.get_file_button = tk.Button(
            self.frame,
            text = "Set File",
            command = self.get_file
            )
        self.input_file_name = tk.StringVar()
        self.input_file_path = tk.StringVar()
        self.input_file_label = tk.Label(
            self.frame,
            textvariable = self.input_file_name
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
        self.response_label = tk.Label(self.frame, textvariable = self.user_response)

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
        out = self.reorder_csv_for_single_point_data(
            self.input_file_path.get(),
            self.num_replicates_value.get()
            )
        output_file_name = "".join([
            os.path.splitext(self.input_file_name.get())[0], 
            "_reordered", 
            os.path.splitext(self.input_file_name.get())[1]
            ])
        output_file_path = os.path.dirname(self.input_file_path.get())
        output_file = os.path.join(output_file_path, output_file_name)
        with open(output_file, "w") as output_file:
            output_file.write(out)

        self.user_response.set("Successfully written {}.".format(output_file_name))


