#############################################################
# deps_main_window.py
#
# Created: 2022. 10. 09
#
# Authors:
#    Youngsun Han (youngsun@pknu.ac.kr)
#
# Quantum Computing Laboratory (quantum.pknu.ac.kr)
#############################################################

import os.path
import threading
import numpy as np
from datetime import datetime

from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot, QByteArray, QThread, pyqtSignal

from deps_error import DepsError
from deps_comm_conn import DepsCommConn
from deps_comm_file import DepsCommFile
from deps_config_parser import read_config_file
from deps_data_processor import DepsDataProcessor, calculate_linear_regression_v2, calculate_linear_regression

#######################################################################
# DepsMainWindow class
#######################################################################

# Main window, Main window UI
MW_Ui, MW_Base = uic.loadUiType("../res/deps_main_window.ui")

class DepsMainWindow(MW_Base, MW_Ui, QThread):
    CONFIG_FILE_NAME: str = 'config.ini'
    PREFIX_SAVE_FILE: str = '../dat/save_'
    PSTFIX_SAVE_FILE: str = '.txt'

    ##
    # Constructor of DepsMainWindow class
    #
    # @param self this object
    #
    def __init__(self):

        super().__init__()
        self.setupUi(self)

        #####################################################################
        # plot widget initialization
        plot_widgets = [
            self.pw_rawdat_spd,
            self.pw_rawdat_ang,
            self.pw_rawdat_trq
        ]

        for pw in plot_widgets:
            pw.getPlotItem().hideAxis('left')

        #####################################################################
        # signal/slot connections for gui components
        self.pb_evaluate.clicked.connect(self.slot_evaluate_clicked)
        self.pb_rawdat_save.clicked.connect(self.slot_rawdat_save_clicked)
        self.pb_rawdat_disp.clicked.connect(self.slot_rawdat_disp_clicked)

        #####################################################################
        # read config file
        self.__config = read_config_file('config.ini')
        self.__config_default = self.__config['DEFAULT']

        #####################################################################
        # message
        msg: str = self.__config_default['message']

        if msg == 'distance':
            self.lb_msg_title.setText('Distance:')
            self.lb_msg_content.setText('0 km')
        elif msg == 'time':
            self.lb_msg_title.setText('Time:')
            self.lb_msg_content.setText(datetime.now().strftime("%H:%M:%S"))

        #####################################################################
        # vehicle loading
        loading: int = int(self.__config_default['loading'])

        self.cb_loading_none.setChecked(False)
        self.cb_loading_heavy.setChecked(False)

        if loading == 0:
            self.cb_loading_none.setChecked(True)
        elif loading > 150:
            self.cb_loading_heavy.setChecked(True)

        #####################################################################
        # threshold value
        thv = int(self.__config_default['threshold'])

        # eps data processor
        self.processor = DepsDataProcessor(thv)

        #####################################################################
        # restore the saved sensor data
        fname: str = self.__config_default['saved']
        if fname != 'None':
            self.__load_rawdat_file(fname)
      
        # open a new save file
        self.save_fp = open(new_save_path(), 'w')
        self.__config_default['saved'] = self.save_fp.name

        # update the config file ('config.ini')
        if fname == 'None':
            config_file_name = DepsMainWindow.CONFIG_FILE_NAME
            with open(config_file_name, 'w') as configfile:
                self.__config.write(configfile)

        #####################################################################
        # refresh rate for signal buffers
        self.refresh_rate: int = int(self.__config_default['refreshrate'])

        # internal states for controlling the worker thread
        self.eval_state: bool = True
        self.disp_state: bool = True

        # start the worker thread of this main window
        self.__worker_event = threading.Event()
        self.__worker_thread = self.WorkerThread(self, self.__worker_event)
        self.__worker_thread.start()

        #####################################################################
        # initialize the uart communication
        # self.__conn = DepsCommConn()
        #
        # # baudrate
        # baudrate = int(self.__config_default['baudrate'])
        #
        # err = self.__conn.open(baudrate)
        # if err != DepsError.SUCCESS:
        #     self.print_log("EPS connection is not opened: " + err.name)
        #     return

        #####################################################################
        # initialize the uart communication
        self.__conn = DepsCommFile()

        # filename
        err = self.__conn.open('../dat/test_11.txt')
        if err != DepsError.SUCCESS:
            self.print_log("EPS connection is not opened: " + err.name)
            return

        # signal for receiving esp data
        self.__conn.sig_eps_recv_bytes.connect(
            lambda v=QByteArray: self.slot_esp_rawdat_received(v))
        
        # start to receive the eps data
        self.__conn.start_eps_recv_thread()

    ##
    # Destructor of DepsMainWindow class
    #
    # @param self this object
    #
    def __del__(self):
        # stop threading
        if self.__worker_thread.isRunning():
            self.__worker_event.set()

        # close the save file
        if self.save_fp is not None:
            self.save_fp.close()

            # delete the save file if it's size is 0
            fname = self.save_fp.name
            if os.path.getsize(fname) == 0:
                self.print_log("Delete the empty save file: " + fname)
                os.remove(fname)

        # close the uart connection
        if self.__conn is not None:
            self.__conn.close()

    ##
    # This is a function to restore the data signals from the saved file.
    #
    # @param self this object
    # @param filename the name of the saved file to be stored
    # @return if restoring is completed well or not
    #
    def __load_rawdat_file(self, filename: str) -> bool:
        # restore the data from the previously saved data file
        try:
            save_fp = open(filename, 'r')
        except FileNotFoundError as e:
            self.print_log('No file: ' + filename + str(e))
            return False

        # saved data read
        while True:
            line_str = save_fp.readline().rstrip()
            if not line_str:
                break

            # transfer the input signal into the data processor
            self.processor.enqueue_sensor_signal(line_str)

        # close the save file
        save_fp.close()
        return True

    ###################################################################
    # Slot functions
    ###################################################################

    ##
    # This is a slot function to handle the signal
    # when the evaluation start button is clicked.
    #
    # @param self this object
    #
    @pyqtSlot()
    def slot_evaluate_clicked(self):
        if self.eval_state:
            self.eval_state = False
            self.__conn.stop_eps_recv_thread()
            self.pb_evaluate.setText('Continue')
        else:
            self.eval_state = True
            self.__conn.start_eps_recv_thread()
            self.pb_evaluate.setText('Pause')

    ##
    # This is a slot function to handle the signal when the save and end button is clicked.
    #
    # @param self this object
    #
    @pyqtSlot()
    def slot_rawdat_save_clicked(self):
        # close the current save file
        if self.save_fp is not None:
            self.save_fp.close()

        # update the config file ('config.ini')
        config_file_name = DepsMainWindow.CONFIG_FILE_NAME
        with open(config_file_name, 'w') as configfile:
            self.__config.write(configfile)

        # open a new save file
        self.save_fp = open(new_save_path(), 'w')
        self.__config_default['Saved'] = self.save_fp.name

    ##
    # This is a slot function to handle the signal when the raw data display button is clicked.
    #
    # @param self this object
    #
    @pyqtSlot()
    def slot_rawdat_disp_clicked(self):
        if self.disp_state:
            self.disp_state = False
            self.pb_rawdat_disp.setText('Run')
        else:
            self.disp_state = True
            self.pb_rawdat_disp.setText('Stop')
        return

    ##
    # This is a slot function for handling the received eps data.
    #
    # @param self this object
    #
    @pyqtSlot()
    def slot_esp_rawdat_received(self, read_bytes: QByteArray):
        rawdat = read_bytes.decode('ISO-8859-1').rstrip()
        datbuf = self.processor.enqueue_sensor_signal(rawdat)

        # YOUNGSUN
        #print('received: ' + rawdat)
        
        if datbuf is not None:
            spd = datbuf[0]
            ang = datbuf[1]
            trq = datbuf[2]
        
            self.save_fp.write('SPD:{:5.3f},ANG:{:5.3f},TRQ:{:5.3f}\n'.format(spd, ang, trq))

    ##
    # This is an event handler function for handling the window close event.
    #
    # @param self this object
    #
    def closeEvent(self, event):
        self.__del__()

    ##
    # This function is used to append a message string to the log pane.
    #
    # @param self this object
    # @param msg a string message to be displayed on the log pane.
    #
    def print_log(self, msg):
        def __print_log_thread(_msg):
            self.lw_log_pane.addItem(_msg)
            self.lw_log_pane.scrollToBottom()

            # just for debugging
            print(_msg + '\n')

        # create new thread to execute the given target function
        threading.Thread(target=__print_log_thread, args=(msg,)).start()

    ##
    # This is a function to dump out all the received eps sensor data.
    #
    # @param self this object
    # @param path dump file path
    #
    def dump_file(self, path):
        # open a file of the given path
        fd = open(path, 'w')

        # print out all the list items into the file of the given path
        log_pane = self.lw_log_pane

        for i in range(0, log_pane.count()):
            fd.write(log_pane.item(i).text() + "\n")

        # close the file
        fd.close()

    #############################################################
    # WorkerThread class
    #############################################################

    ##
    # Constructor of WorkerThread inner class
    #
    # @param self this object
    #
    class WorkerThread(QThread):
        # UI update signale
        sig_update_graphs = pyqtSignal()

        def __init__(self, parent, event):
            super().__init__(parent)
            self.__parent = parent
            self.__stopped = event

            # a buffer of lps points
            self.__lps_buffer = []
            for i in range(3):
                self.__lps_buffer.append([])

            # signal-slot connection
            self.sig_update_graphs.connect(self.slot_update_graphs)

        ##
        # This is a slot function to update all the graphs.
        #
        def slot_update_graphs(self):
            if self.__parent.disp_state:
                self.__update_rawdat_graph(self.__parent.processor)

            if self.__parent.eval_state:
                self.__update_linearity_graph(self.__parent.processor)

        ##
        # This is a function to update the raw data graph.
        #
        # @param self this work thread object
        # @param proc the data processor for input signals
        #
        def __update_rawdat_graph(self, proc: DepsDataProcessor):
            # rawdat
            rawdat = proc.refined_sensor_signal()

            # speed, angle, torque
            self.__parent.pw_rawdat_spd.clear()
            self.__parent.pw_rawdat_spd.plot(rawdat[0], pen='r')

            self.__parent.pw_rawdat_ang.clear()
            self.__parent.pw_rawdat_ang.plot(rawdat[1], pen='g')

            self.__parent.pw_rawdat_trq.clear()
            self.__parent.pw_rawdat_trq.plot(rawdat[2], pen='b')

        ##
        # This is a function to update the linearity points graph.
        #
        # @param self this work thread object
        # @param proc the data processor for input signals
        #
        def __update_linearity_graph(self, proc: DepsDataProcessor):

            # pyqt widgets to plot the linearity points
            plot_widgets = [
                self.__parent.pw_linearity_lv1,
                self.__parent.pw_linearity_lv2,
                self.__parent.pw_linearity_lv3
            ]

            plot_labels = [
                self.__parent.lb_linearity_lv1,
                self.__parent.lb_linearity_lv2,
                self.__parent.lb_linearity_lv3
            ]

            # get the number of stored signals
            num_sig = proc.num_sensor_signal()

            # linearity calculation
            lps_list = proc.process(0, num_sig)

            if lps_list is None:
                self.__parent.print_log('There are no linearity points to be plot.')
                return

            try:
                # speed levels (0~10, 10~30, 30~60 km/h)
                for i in range(len(plot_widgets)):
                    # temporary lps list
                    points: list = self.__lps_buffer[i].copy()
                    points.extend(lps_list[i])

                    # a list of linearity points
                    x, y = zip(*points)

                    # linear regression (slope, intercept)
                    b1, b0 = calculate_linear_regression(x, y)

                    # calculate predicted y with the regression results
                    y_pred = b1 * np.array(x) + b0

                    # plot the points and regression line
                    plot_widgets[i].clear()
                    plot_widgets[i].plot(x, y, pen=None, symbol='o')
                    plot_widgets[i].plot(x, y_pred, pen='r')

                    # plot the linearity label
                    b1, b0 = calculate_linear_regression_v2(x, y)
                    plot_labels[i].setText('Linearity: {:5.3f}'.format(b1))

            except ValueError as e:
                print('__update_linearity_graph error: {}'.format(str(e)))

            print('test: ' + str(num_sig))

            # refresh sensor data buffer
            if num_sig >= self.__parent.refresh_rate:
                # store all the linearity points into the buffer
                for i in range(len(lps_list)):
                    self.__lps_buffer[i].extend(lps_list[i])

                # remove all the sensor data
                print('before reset buffer - ' + str(proc.num_sensor_signal()))
                proc.dequeue_sensor_signal()
                print('after reset buffer - ' + str(proc.num_sensor_signal()))

        ##
        # This is a run method of this worker thread.
        #
        # @param self this work thread object
        #
        def run(self):
            while not self.__stopped.wait(1):
                self.sig_update_graphs.emit()

###################################################################
# Utility functions
###################################################################

##
# This is a function to return the new path of the save file.
#
# @param prefix the prefix string to be inserted at the first of the new path
# @param pstfix the postfix string to be inserted at the last of the new path
# @return the new path
def new_save_path(prefix: str = DepsMainWindow.PREFIX_SAVE_FILE,
                  pstfix: str = DepsMainWindow.PSTFIX_SAVE_FILE):
    return prefix + datetime.now().strftime("%Y%m%d_%H%M%S") + pstfix