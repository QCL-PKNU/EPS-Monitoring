#############################################################
# deps_main.py
#
# Created: 2022. 10. 09
#
# Authors:
#    Youngsun Han (youngsun@pknu.ac.kr)
#
# Quantum Computing Laboratory (quantum.pknu.ac.kr)
#############################################################


import sys
import random

from PyQt5.QtWidgets import QApplication
from deps_main_window import DepsMainWindow
from PyQt5.uic import loadUi

#############################################################
# Main function for EPS monitoring software
#############################################################

if __name__ == '__main__':
   

    app = QApplication(sys.argv)
    # print(loadUi('/Users/huotnich/Desktop/EPS-Monitoring/deps_standalone/src/deps_main_window_test.ui'))
    window = DepsMainWindow()
    window.setWindowTitle("EPS Evaluation v2.0")
    window.show()
    sys.exit(app.exec_())
