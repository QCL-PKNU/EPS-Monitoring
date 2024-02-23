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

#############################################################
# Main function for EPS monitoring software
#############################################################


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DepsMainWindow()
    window.setWindowTitle("EPS Evaluation v2.0")
    window.show()
    sys.exit(app.exec_())