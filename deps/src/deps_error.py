#############################################################
# deps_error.py
#
# Created: 2022. 10. 09
#
# Authors:
#    Youngsun Han (youngsun@pknu.ac.kr)
#
# Quantum Computing Laboratory (quantum.pknu.ac.kr)
#############################################################

import enum

#######################################################################
# DepsError enum class
#######################################################################

class DepsError(enum.Enum):
    SUCCESS = 0
    INVALID_PARAMETER = 1
    INVALID_FILE_PATH = 2

    # UART
    ERROR_UART_OPEN = 3
    ERROR_UART_PARAM = 4

    # DATA FORMAT
    ERROR_SENSOR_DATA_FORMAT = 5
