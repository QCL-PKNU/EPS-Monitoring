#############################################################
# DepsCommFile
#
# Created: 2022. 11. 05
#
# Authors:
#    Youngsun Han (youngsun@pknu.ac.kr)
#
# Quantum Computing Laboratory (quantum.pknu.ac.kr)
#############################################################

import sys

from deps_error import DepsError
from PyQt5.QtCore import QThread, pyqtSignal

#######################################################################
# DepsCommFile class
#######################################################################

class DepsCommFile(QThread):
    
    ##
    # Constructor of DepsCommFile class
    #
    def __init__(self):

        super().__init__()
        
        #file handle
        self.__file = None

        # eps read thread
        self.__eps_recv_flag = False

    ###################################################################
    # file connections
    ###################################################################

    def open(self, filename: str):

        try:
            self.__file = open(filename, 'r')
        except FileNotFoundError as e:
            self.print_log('No file: ' + filename + str(e))
            return False

        # start a thread for receiving uart data
        QThread.start(self)

        return DepsError.SUCCESS

    def close(self):
        if self.__file is not None:
            self.__file.close()

        # stop the file thread
        self.quit()
        
    ###################################################################
    # EPS sensor data 
    ###################################################################

    # eps read signal
    sig_eps_recv_bytes = pyqtSignal(bytearray)

    ##
    # This is a thread routine for receiving eps sensor data.
    #
    # @param self this object
    #
    def run(self):
        read_bytes = []
        while True:
            line_str = self.__file.readline().rstrip()
            if not line_str:
                break

            read_bytes = line_str.encode('ISO-8859-1')

            # just for debugging
            # print(">> Read Byte: " + str(read_bytes[0]) + "\n")

            if self.__eps_recv_flag and len(read_bytes) > 0:
                self.sig_eps_recv_bytes.emit(bytearray(read_bytes))

            # wait for 0.01 sec
            self.msleep(10)

        return

    ## 
    # This is a wrapper function to start a thread for receiving the eps sensor data.
    #
    # @param self this object
    #
    def start_eps_recv_thread(self):
        self.__eps_recv_flag = True
        
    ## 
    # This is a wrapper function to stop a thread for receiving the eps sensor data.
    #
    # @param self this object
    #
    def stop_eps_recv_thread(self):
        self.__eps_recv_flag = False
