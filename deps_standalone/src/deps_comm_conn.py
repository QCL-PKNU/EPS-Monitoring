#############################################################
# DepsCommConn
#
# Created: 2021. 05. 11
#
# Authors:
#    Youngsun Han (youngsun@pknu.ac.kr)
#
# Quantum Computing Laboratory (quantum.pknu.ac.kr)
#############################################################

import sys
import serial
#import RPi.GPIO as GPIO

from deps_error import DepsError
from PyQt5.QtCore import QThread, pyqtSignal

#######################################################################
# DepsCommConn class
#######################################################################

class DepsCommConn(QThread):
    
    ##
    # Constructor of DepsCommConn class
    #
    def __init__(self):

        super().__init__()
        
        #uart handle
        self.__uart = None

        # eps read thread
        self.__eps_recv_flag = False

    ###################################################################
    # gpio & uart connections
    ###################################################################

    ##
    # This is a function to open gpio & uart connections.
    #
    # @param self this object
    # @param baud the baudrate of the uart connection
    # @return error information
    #
    def open(self, baud: int):

        # # gpio initialization
        # GPIO.setmode(GPIO.BOARD)
        #
        # # mode pins: 11, 12, 13
        # self.modePinNums = [11, 12, 13]
        # GPIO.setup(self.modePinNums, GPIO.OUT, initial=GPIO.LOW)
        #
        # # speed pins: 15, 16
        # self.speedPinNums = [15, 16]
        # GPIO.setup(self.speedPinNums, GPIO.OUT, initial=GPIO.LOW)
        #
        # # uart initialization (TX: 8, RX: 10)
        # try:
        #     self.__uart = serial.Serial('/dev/ttyS0', baudrate=baud, timeout=1)
        #     self.__uart.flush()
        # except ValueError:
        #     return DepsError.ERROR_UART_PARAM
        # except serial.SerialException as e:
        #     print("UART OPEN ERROR: " + str(e))
        #     return DepsError.ERROR_UART_OPEN
        #
        # # start a thread for receiving uart data
        # QThread.start(self)

        return DepsError.SUCCESS

    ## 
    # This is a function to close gpio & uart connections.
    #
    # @param self this object
    #
    def close(self):
        # # gpio finalization
        # GPIO.cleanup()
        #
        # # uart finialization
        # if self.__uart is not None:
        #     self.__uart.close()
        #
        # stop the uart thread
        self.quit()

    ## 
    # This is a function to configure the test mode of the eps sensor.
    #
    # @param self this object
    # @param mode test mode (0, 1, 2, 3, 4, 5)
    # @return false if the input mode is wrong, otherwise true
    #
    def set_test_mode(self, mode):
        # pinout = []
        #
        # if mode == 0:
        #     pinout = [0, 0, 0]
        # elif mode == 1:
        #     pinout = [0, 0, 1]
        # elif mode == 2:
        #     pinout = [0, 1, 0]
        # elif mode == 3:
        #     pinout = [0, 1, 1]
        # elif mode == 4:
        #     pinout = [1, 0, 0]
        # elif mode == 5:
        #     pinout = [1, 0, 1]
        # else:
        #     print("invalid mode: ", mode)
        #     return False
        #
        # #print("mode: ", pinout)
        #
        # pinnum = self.modePinNums;
        #
        # for i in range(0, len(pinout)):
        #     if pinout[i] == 1:
        #         GPIO.output(pinnum[i], GPIO.HIGH);
        #     else:
        #         GPIO.output(pinnum[i], GPIO.LOW);

        return True

    ## 
    # This is a function to configure the vehicle speed of the eps sensor.
    #
    # @param self this object
    # @param speed vehicle speed (0, 1, 2, 3)
    # @return false if the input speed is wrong, otherwise true
    #
    def set_vehicle_speed(self, speed):
        # pinout = []
        #
        # if speed == 0:
        #     pinout = [0, 0]
        # elif speed == 1:
        #     pinout = [0, 1]
        # elif speed == 2:
        #     pinout = [1, 0]
        # elif speed == 3:
        #     pinout = [1, 1]
        # else:
        #     print("invalid speed: ", speed)
        #     return False
        #
        # #print("speed: ", pinout)
        #
        # pinnum = self.speedPinNums;
        #
        # for i in range(0, len(pinout)):
        #     if pinout[i] == 1:
        #         GPIO.output(pinnum[i], GPIO.HIGH);
        #     else:
        #         GPIO.output(pinnum[i], GPIO.LOW);

        return True
        
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
            # read the eps sensor data byte one by one
            try:
                read_bytes = self.__uart.read_until(b'\x0A')
            except serial.SerialException as e:
                print('UART read exception occurs...' + str(e))
                self.msleep(1000)
                continue

            # just for debugging
            # print(">> Read Byte: " + str(read_bytes[0]) + "\n")

            if self.__eps_recv_flag and len(read_bytes) > 0:
                self.sig_eps_recv_bytes.emit(bytearray(read_bytes))
            else:
                # wait for 0.001 sec
                self.msleep(1)
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
