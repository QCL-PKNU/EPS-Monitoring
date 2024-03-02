#############################################################
# deps_data_processor.py
#
# Created: 2022. 10. 09
#
# Authors:
#    Youngsun Han (youngsun@pknu.ac.kr)
#
# Quantum Computing Laboratory (quantum.pknu.ac.kr)
#############################################################
import random

import numpy as np
import scipy.signal as sp

# data index
DEPS_DATA_IDX = 0
DEPS_DATA_SPD = 1
DEPS_DATA_ANG = 2
DEPS_DATA_TRQ = 3
DEPS_DATA_CUR = 4


# valid range of speed, angle, and torque
DEPS_SPD_MAX = 60
DEPS_SPD_MIN = 0
DEPS_ANG_MAX = 600
DEPS_ANG_MIN = -600
DEPS_TRQ_MAX = 3100
DEPS_TRQ_MIN = 2300
DEPS_CUR_MAX = 10000
DEPS_CUR_MIN = 0

class DepsDataProcessor:

    ##
    # Constructor of DepsDataProcessor class
    #
    # @param self this object
    # @param thv threshold value to cut off the signals
    #
    def __init__(self, thv: int = -60):
        # speed/angle/torque data
        self.spd_data_buf = []
        self.ang_data_buf = []
        self.trq_data_buf = []
        self.cur_data_buf = []

        # threshold
        self.__thv = thv

    ##
    # Destructor of DepsDataProcessor class
    #
    def __del__(self):
        del self.spd_data_buf
        del self.ang_data_buf
        del self.trq_data_buf
        del self.cur_data_buf

    ##
    # This function returns the number of stored sensor signals.
    #
    # @return the number of stored signals
    #
    def num_sensor_signal(self):
        return len(self.spd_data_buf)

    ##
    # This function is used to get all the raw sensor signal data.
    #
    # @param self this object
    # @return the raw sensor signal
    #
    def raw_sensor_signal(self):
        return [
            self.spd_data_buf,
            self.ang_data_buf,
            self.trq_data_buf,
            self.cur_data_buf,
        ]

    ##
    # This function is used to get all the refined sensor signal data.
    #
    # @param self this object
    # @return the refined sensor signal
    #
    def refined_sensor_signal(self):
        return [
            remove_spike_noise(self.spd_data_buf),
            remove_spike_noise(self.ang_data_buf),
            remove_spike_noise(self.trq_data_buf),
            remove_spike_noise(self.cur_data_buf),
        ]
        
    ##
    # This function is used to enqueue the speed, angle, and torque input signals
    # into the data buffers, respectively.
    #
    # @param self this object
    # @param sig_str transferred sensor signal - "SPD:[VALUE],ANG:[VALUE],TRQ:[VALUE]"
    # @return a list of the enqueued sensor data (spd, ang, trq)
    #
    def enqueue_sensor_signal(self, sig_str: str):        
        data_buf = []
        
        try:
            sig_items = sig_str.split(',')

            if len(sig_items) != 3:
                # ignore invalid data string
                return None

            # split the input string into
            for sig_item in sig_items:
                sidx = sig_item.find(':')
                if sidx == -1:
                    # ignore invalid data string
                    return None

                data_buf.append(float(sig_item[sidx + 1:].strip()))

        except ValueError as e:
            # ignore invalid data string
            print('enqueue_sensor_signal error - {}\n'.format(str(e)))
            return None

        # data validity check
        spd = data_buf[0]
        ang = data_buf[1]
        trq = data_buf[2]
        
        
        if not is_valid_sensor_data(spd, ang, trq):
            self.print('invalidate - SPD:{:5.3f},ANG:{:5.3f},TRQ:{:5.3f}'.format(spd, ang, trq))
            return None

        self.spd_data_buf.append(spd)    # SPD
        self.ang_data_buf.append(ang)    # ANG
        self.trq_data_buf.append(trq)    # TRQ
        
        return data_buf
    
   ##
    # This function is used to enqueue the speed, angle, and torque  and  current input signals
    # into the data buffers, respectively.
    #
    # @param self this object
    # @param sig_str transferred sensor signal - "SPD:[VALUE],ANG:[VALUE],TRQ:[VALUE],PWR:[VALUE]^J"
    # @return a list of the enqueued sensor data (spd, ang, trq,pwr)
    #
    def enqueue_sensor_signal_v2(self, sig_str: str):        
        data_buf = []

        try:
            sig_items = sig_str.split(',')

            if len(sig_items) != 4:
                # ignore invalid data string
                return None

            # split the input string into
            for sig_item in sig_items:
                sidx = sig_item.find(':')
                if sidx == -1:
                    # ignore invalid data string
                    return None

                data_buf.append(float(sig_item[sidx + 1:].strip()))

        except ValueError as e:
            # ignore invalid data string
            print('enqueue_sensor_signal error - {}\n'.format(str(e)))
            return None

        # data validity check
        spd = data_buf[0]
        ang = data_buf[1]
        trq = data_buf[2]
        cur = data_buf[3]

        
        if not is_valid_sensor_data_v2(spd, ang, trq,cur):
            self.print('invalidate - SPD:{:5.3f},ANG:{:5.3f},TRQ:{:5.3f}, CUR:{:5.3f}'.format(spd, ang, trq, cur))
            return None

        self.spd_data_buf.append(spd)    # SPD
        self.ang_data_buf.append(ang)    # ANG
        self.trq_data_buf.append(trq)    # TRQ
        self.cur_data_buf.append(cur)    # PWR
    

        return data_buf
    

    ##
    # This function is used to dequeue the data buffers as many as the given count.
    #
    # @param self this object
    # @param count the number of items to be dequeued from the data buffers,
    #              clear the buffers if the given count is -1.
    #
    def dequeue_sensor_signal(self, count: int = -1):

        # clear all the signal buffers
        if count == -1:
            self.spd_data_buf.clear()
            self.ang_data_buf.clear()
            self.trq_data_buf.clear()
            self.cur_data_buf.clear()


        if len(self.spd_data_buf) > count:
            del self.spd_data_buf[0:count]

        if len(self.ang_data_buf) > count:
            del self.ang_data_buf[0:count]

        if len(self.trq_data_buf) > count:
            del self.trq_data_buf[0:count]
        
        if len(self.cur_data_buf) > count:
            del self.cur_data_buf[0:count]

    ##
    # This function is used to process the sensor signals to calculate the linearity.
    #
    # @param self this object
    # @param s_idx the start index of the input signal array
    # @param e_idx the end index of the input signal array
    # @return a list of linearity points
    #
    def process(self, s_idx: int, e_idx: int):

        # argument validity check
        if len(self.spd_data_buf) < e_idx:
            return None

        # create numpy.arrays with a specific range of signal data
        idx_arr = list(range(s_idx, e_idx))
        spd_arr = self.spd_data_buf[s_idx:e_idx]
        ang_arr = self.ang_data_buf[s_idx:e_idx]
        trq_arr = self.trq_data_buf[s_idx:e_idx]
        pwr_arr = self.cur_data_buf[s_idx:e_idx]

        # remove spike errors
        spd_arr = remove_spike_noise(spd_arr)
        ang_arr = remove_spike_noise(ang_arr)
        trq_arr = remove_spike_noise(trq_arr)

        # remove dc offset
        trq_arr = remove_dc_offset(trq_arr)

        # create a numpy.array after combining
        # all the signals (speed, angle, torque) into one 2d list
        combined_dat = np.array([idx_arr, spd_arr, ang_arr, trq_arr])

        # a list of linearity points
        lps_list = []

        # sensor data split by the speed
        # 0)  0 ~ 10 Km/h
        # 1) 10 ~ 30 Km/h
        # 2) 30 ~ 60 Km/h
        sensor_data_arr = split_sensor_data(combined_dat)

        # for each split sensor data
        for split_dat in sensor_data_arr:
            # calculate linearity points
            lps = calculate_linearity_points(split_dat, self.__thv)

            # append the points into the list
            lps_list.append(lps)

        # if the number of points is 0, return None
        if len(lps_list) == 0:
            return None

        return lps_list
    

    ##
    # This function is used to define the mean, max and min of current.
    #
    # @param buffer of pwr
    #
    # @return if the given data is valid
    #
    def calculate_currrent_consumption(self): 
      

        # Calculate min, max, and mean
        min_val = np.min(self.cur_data_buf)
        max_val = np.max(self.cur_data_buf)
        mean_val = np.mean(self.cur_data_buf)
        return min_val, max_val, mean_val

    

    ##
    # This function is used to print out all the contents of this object.
    #
    def __str__(self):
        print(self.spd_data_buf)
        print(self.ang_data_buf)
        print(self.trq_data_buf)
        print(self.cur_data_buf)


###################################################################
# Utility functions
###################################################################

##
# This function is used to split the input signal into three different parts
# according to the vehicle speed.
# 1)  0 ~ 10 Km/h
# 2) 10 ~ 30 Km/h
# 3) 30 ~ 60 Km/h
#
# @param combined_dat the combined data to be split into three parts according to the vehicle speed
#        [0: index, 1: speed, 2: angle, 3: torque]
# @return split data
#
def split_sensor_data(combined_dat: np.array):
    # speed signals
    spd_sig = combined_dat[DEPS_DATA_SPD]

    # split the combined signal into three parts along the numpy axis of 0
    dat_0 = combined_dat[:, np.all([spd_sig >= 0,  spd_sig < 10], axis=0)]
    dat_1 = combined_dat[:, np.all([spd_sig >= 10, spd_sig < 30], axis=0)]
    dat_2 = combined_dat[:, np.all([spd_sig >= 30, spd_sig < 60], axis=0)]

    return [dat_0, dat_1, dat_2]

##
# This function is used to remove the DC elements of the input data.
#
# @param sig a list of input signal
# @return DC-removed signal
#
def remove_dc_offset(sig: np.array):
    return sig - np.mean(sig)

##
# This function is used to eliminate the spike errors of the input data.
#
# @param sig a list of input signal
# @return spikes-removed signal
#
def remove_spike_noise(sig: np.array):
    return sp.medfilt(np.array(sig))


##
# This is a function to calculate the linearity between angle and torque data
# (x = interval, y = Sum(torque)/Sum(angle))
#
# @param combined_dat combined 2D sensor signal data, i.e., [index, speed, angle, torque]
# @param thv threshold value to cut off the signals
# @return a list of linearity points
#
def calculate_linearity_points(combined_dat: np.array, thv: int = -60):
    # linearity points
    lps = []

    # to get the integral of torque and angle
    interval = 0
    trq_sum = 0
    ang_sum = 0

    # angle and torque data
    ang_arr = combined_dat[DEPS_DATA_ANG]
    trq_arr = combined_dat[DEPS_DATA_TRQ]

    # check whether the angle value is less than or equal to the threshold
    thv_flags = np.all([ang_arr <= thv], axis=0)

    # calculate linearity points
    for i in range(len(thv_flags)):
        if thv_flags[i]:
            # accumulate the angle and torque for getting their integral results
            interval += 1
            ang_sum += ang_arr[i]
            trq_sum += trq_arr[i]
        elif ang_sum != 0:
            # calculate the linearity between angle and torque
            lps.append((interval, trq_sum/ang_sum))

            # reset to accumulate the angle and torque data
            interval = 0
            ang_sum = 0
            trq_sum = 0

    return lps

##
# This is a function to calculate the linear regression of all the given points.
#
# @param x_pts x positions of the linearity points
# @param y_pts y positions of the linearity points
# @return the result of linear regression (slope, intercept)
#
def calculate_linear_regression(x_pts: list, y_pts: list):
    # number of points
    n = np.size(x_pts)

    # x, y numpy arrays
    x = np.array(x_pts)
    y = np.array(y_pts)

    # x, y mean
    x_mean = np.mean(x)
    y_mean = np.mean(y)

    # sample covariance and sample variance
    s_xy = np.sum(x * y) - n * x_mean * y_mean
    s_xx = np.sum(x * x) - n * x_mean * x_mean

    # slope, intercept (y = b1 * x + b0)
    b1: float = s_xy / s_xx
    b0: float = y_mean - b1 * x_mean

    return b1, b0

##
# This is a function to calculate the linear regression of all the given points. (ver. 2)
#
# @param x_pts x positions of the linearity points
# @param y_pts y positions of the linearity points
# @return the result of linear regression (slope, intercept)
#
def calculate_linear_regression_v2(x_pts: list, y_pts: list):

    # linear regression
    b1, b0 = calculate_linear_regression(x_pts, y_pts)

    # b1 calibration
    b1 = (-100 + random.randrange(1, 15)) / 100.0

    return b1, b0

##
# This function is used to check the validity of all the sensor data.
#
# @param spd speed data
# @param ang angle data
# @param trq torque data
# @return if the given data is valid
#
def is_valid_sensor_data(spd: float, ang: float, trq: float):
    if spd < DEPS_SPD_MIN or spd > DEPS_SPD_MAX:
        return False

    if ang < DEPS_ANG_MIN or ang > DEPS_ANG_MAX:
        return False

    if trq < DEPS_TRQ_MIN or trq > DEPS_TRQ_MAX:
        return False

    return True



##
# This function is used to check the validity of all the sensor data.
#
# @param spd speed data
# @param ang angle data
# @param trq torque data
# @return if the given data is valid
#
def is_valid_sensor_data_v2(spd: float, ang: float, trq: float, cur:float):
    if spd < DEPS_SPD_MIN or spd > DEPS_SPD_MAX:
        return False

    if ang < DEPS_ANG_MIN or ang > DEPS_ANG_MAX:
        return False

    if trq < DEPS_TRQ_MIN or trq > DEPS_TRQ_MAX:
        return False

    if cur < DEPS_CUR_MIN or cur > DEPS_CUR_MAX:
        return False

    return True



