import sys
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QMessageBox
import matplotlib.pyplot as plt
from PyQt5 import QtCore
from main_window import Ui_MainWindow
import numpy as np
from threading import Thread
import time
import re


frequency = 0
level_number = 0
medium_original = []
type_of_wave = 0
#1 for TM , 2 for TE , 0 for none
figure_plot = []
yita = []
miu = []
ebuxiro = []
d_each_level = []
R_TE = []
R_TM = []
T_TE = []
T_TM = []


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.set_callback()
        self.show()

        #self.figure = plt.figure()

        #ProducerThread().start()

    def set_callback(self):
        self.ui.write_data.clicked.connect(self.read_message)




    def read_message(self):
        global medium_original, level_number, frequency, miu, ebuxiro, d_each_level

        medium_original = np.array(self.ui.textEdit_medium_matrix.toPlainText())
        level_number = self.ui.line_edit_level_number.text()
        frequency = self.ui.line_edit_frequency.text()
        # print(medium_original)
        medium_original_replace_space = str(medium_original).replace(" ", "").replace("\n", "")
        medium_matrix = re.findall(r"\d+\.?\d*", medium_original_replace_space)
        # print(medium_matrix)

        if (len(medium_matrix) == 0 or len(level_number) == 0 or len(frequency) == 0):
            self.show_message('请输入正确电磁参数。')
            return
        print(medium_matrix)
        level_number = int(level_number)
        frequency = int(frequency)

        if len(medium_matrix) != level_number * 3:
            self.show_message('请输入正确电磁参数。')
            return

        for i in range(level_number):
            miu.append(medium_matrix[i * 3])
            ebuxiro.append(medium_matrix[i * 3 + 1])
            d_each_level.append(medium_matrix[1 * 3 + 2])

        self.caculate()

    def caculate(self):
        print(miu)
        print(ebuxiro)
        print(d_each_level)

    def set_module_TE(self):
        figure_plot

    def show_message(self, text):
        msg = QMessageBox()
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok)
        ret = msg.exec_()


#class ProducerThread(Thread):



app = QApplication(sys.argv)
w = AppWindow()
w.show()
sys.exit(app.exec_())
