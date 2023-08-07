#############################################################
# deps_config_parser.py
#
# Created: 2022. 10. 09
#
# Authors:
#    Youngsun Han (youngsun@pknu.ac.kr)
#
# Quantum Computing Laboratory (quantum.pknu.ac.kr)
#############################################################

import configparser

##
# This is a function to read a configuration file for initializing the EPS monitoring software.
#
# @param path file path of the configuration file
#
# [Usage]
# config = read_config_file('config.ini')['DEFAULT']
# print(config['Threshold'])
# print(config.get('Saved'))
def read_config_file(path):
    # config['DEFAULT'] = {
    #     'Message': 'distance',
    #     'Loading': '0',
    #     'Minspeed': '10',
    #     'Maxspeed': '30',
    #     'Linearity': '0.93',
    #     'Output': 'linearity',
    #     'Saved': 'none',
    #     'Threshold': '-60'
    # }
    config = configparser.ConfigParser()
    config.read(path)
    return config
