import sys
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QMessageBox
import matplotlib.pyplot as plt
from PyQt5 import QtCore
from Qt import QtGui

from main_window import Ui_MainWindow
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
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
wave_Mode = 0  #1 for TE, 2 for TM
curve_Mode = 0  #1 for reflection， 2 for transmission


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.set_callback()
        self.show()

        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.ui.figure_layout.addWidget(self.canvas)
        self.ax = self.figure.add_subplot(111)



    def set_callback(self):
        self.ui.write_data.clicked.connect(self.read_message)
        self.ui.te_wave.clicked.connect(self.set_module_TE)
        self.ui.tm_wave.clicked.connect(self.set_module_TM)
        self.ui.reflection_coefficient.clicked.connect(self.set_curve_Mode_reflective)
        self.ui.transmission_coefficient.clicked.connect(self.set_curve_Mode_transmission)


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
        global wave_Mode
        wave_Mode = 1
        self.ui.config1.setText('TE波')
        self.ui.config1.repaint()
        self.figure_plot()

    def set_module_TM(self):
        global wave_Mode
        wave_Mode = 2
        self.ui.config1.setText('TM波')
        self.ui.config1.repaint()
        self.figure_plot()

    def set_curve_Mode_reflective(self):
        global curve_Mode
        curve_Mode = 1
        self.ui.config2.setText('反射系数曲线')
        self.ui.config2.repaint()
        self.figure_plot()


    def set_curve_Mode_transmission(self):
        global curve_Mode
        curve_Mode = 2
        self.ui.config2.setText('透射系数曲线')
        self.ui.config2.repaint()
        self.figure_plot()

    def figure_plot(self):
        global wave_Mode, curve_Mode
        figure_final = []
        if wave_Mode == 0 or curve_Mode == 0:
            return
        if wave_Mode == 1:
            if curve_Mode == 1:
                x = [1, 2, 3, 4, 5]
                figure_final = R_TE
                figure_final = x
            elif curve_Mode == 2:
                t = [5, 4, 3, 2, 1]
                figure_final = T_TE
                figure_final = t

        elif wave_Mode == 2:
            if curve_Mode == 1:
                w = [6, 7, 8, 9, 10]
                figure_final = R_TM
                figure_final = w
            elif curve_Mode == 2:
                r = [10, 9, 8, 7, 6]
                # figure_final = T_TM
                figure_final = r
        print('current config', curve_Mode, wave_Mode)
        self.ax.clear()
        self.ax.plot(figure_final)
        self.canvas.draw_idle()

    def show_message(self, text):
        msg = QMessageBox()
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok)
        ret = msg.exec_()




app = QApplication(sys.argv)
w = AppWindow()
w.show()
sys.exit(app.exec_())
