#==============================================================================
# CONSTANT VARIABLES
#==============================================================================

import logging

LOG_FORMATTER = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s")

SEP = ";"

col_names = ['cycle', 'time', 'temp', 'A1', 'A2', 'A3', 'A4',
                'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12', 'B1', 'B2',
                'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'B12',
                'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10',
                'C11', 'C12', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8',
                'D9', 'D10', 'D11', 'D12', 'E1', 'E2', 'E3', 'E4', 'E5', 'E6',
                'E7', 'E8', 'E9', 'E10', 'E11', 'E12', 'F1', 'F2', 'F3', 'F4',
                'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'G1', 'G2',
                'G3', 'G4', 'G5', 'G6', 'G7', 'G8', 'G9', 'G10', 'G11', 'G12',
                'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'H7', 'H8', 'H9', 'H10',
                'H11', 'H12']

data_names = ['A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10',
              'A11', 'A12', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8',
              'B9', 'B10', 'B11', 'B12', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6',
              'C7', 'C8', 'C9', 'C10', 'C11', 'C12', 'D1', 'D2', 'D3', 'D4',
              'D5', 'D6', 'D7', 'D8', 'D9', 'D10', 'D11', 'D12', 'E1', 'E2',
              'E3', 'E4', 'E5', 'E6', 'E7', 'E8', 'E9', 'E10', 'E11', 'E12',
              'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10',
              'F11', 'F12', 'G1', 'G2', 'G3', 'G4', 'G5', 'G6', 'G7', 'G8',
              'G9', 'G10', 'G11', 'G12', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6',
              'H7', 'H8', 'H9', 'H10', 'H11', 'H12']

# Header line for primary TSV results file.
header = "Cycle\tTime [min]\tTemp. [deg. C]\tA1\tA2\tA3\tA4\tA5\tA6\tA7\tA8\tA9\tA10\
         \tA11\tA12\tB1\tB2\tB3\tB4\tB5\tB6\tB7\tB8\tB9\tB10\tB11\tB12\tC1\tC2\tC3\
         \tC4\tC5\tC6\tC7\tC8\tC9\tC10\tC11\tC12\tD1\tD2\tD3\tD4\tD5\tD6\tD7\tD8\tD9\
         \tD10\tD11\tD12\tE1\tE2\tE3\tE4\tE5\tE6\tE7\tE8\tE9\tE10\tE11\tE12\tF1\tF2\
         \tF3\tF4\tF5\tF6\tF7\tF8\tF9\tF10\tF11\tF12\tG1\tG2\tG3\tG4\tG5\tG6\tG7\tG8\
         \tG9\tG10\tG11\tG12\tH1\tH2\tH3\tH4\tH5\tH6\tH7\tH8\tH9\tH10\tH11\tH12\n"
