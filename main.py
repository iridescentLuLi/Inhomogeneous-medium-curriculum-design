import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
import matplotlib.pyplot as plt

from main_window import Ui_MainWindow
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import re


frequency = 0
level_number = 0
medium_original = []
figure_plot = []
yita = []
miu = []
ebuxiro = []
d_each_level = []
wave_Mode = 0  #1 for TE, 2 for TM, 0 for none
curve_Mode = 0  #1 for reflection， 2 for transmission, 0 for none
R_TE_current = 0
R_TM_current = 0
T_TE_current = 0
T_TM_current = 0
Z_n1 = 0

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
            miu.append(float(medium_matrix[i * 3]))
            ebuxiro.append(float(medium_matrix[i * 3 + 1]))
            d_each_level.append(float(medium_matrix[1 * 3 + 2]))

        self.caculate()

    def caculate(self):
        global R_TE_current, R_TM_current, T_TE_current, T_TM_current, Z_n1
        f = frequency
        pi = 3.1416
        theta1 = np.arange(1, 90)
        theta = theta1 / 360 * 2 * pi
        w = f / (2 * pi)
        k_x = np.sqrt(w**2 * miu[0] * ebuxiro[0]) * np.sin(theta)
        k_iz = []
        for i in range(0, level_number):
            k_i = np.sqrt(w**2 * miu[i] * ebuxiro[i])
            k_iz.append(np.sqrt(k_i**2 - k_x**2))

        R_TE = []
        T_TE = []
        R_TM = []
        T_TM = []

        for i in range(0, level_number - 1):

            R_TE.append((miu[i + 1] * k_iz[i] - miu[i] * k_iz[i + 1]) / (miu[i + 1] * k_iz[i] + miu[i] * k_iz[i + 1]))
            T_TE.append((2 * miu[i + 1] * k_iz[i]) / (miu[i + 1] * k_iz[i] + miu[i] * k_iz[i + 1]))
            R_TM.append((ebuxiro[i + 1] * k_iz[i] - ebuxiro[i] * k_iz[i + 1]) / (ebuxiro[i + 1] * k_iz[i] + ebuxiro[i] * k_iz[i + 1]))
            T_TM.append((2 * ebuxiro[i + 1] * k_iz[i]) / (ebuxiro[i + 1] * k_iz[i] + ebuxiro[i] * k_iz[i + 1]))
            if i == 0:
                R_TE_current = R_TE[0]
                R_TM_current = R_TM[0]
                T_TE_current = T_TE[0]
                T_TM_current = T_TM[0]
                continue
            R_TE_current = (R_TE[i] + R_TE_current * np.exp(2 * complex(0, 1) * k_iz[i + 1] * (d_each_level[i] - d_each_level[i - 1]))) / (1 + R_TE[i] * R_TE_current * np.exp(2 * complex(0, 1) * k_iz[i + 1] * (d_each_level[i] - d_each_level[i - 1])))
            R_TM_current = (R_TM[i] + R_TM_current * np.exp(2 * complex(0, 1) * k_iz[i + 1] * (d_each_level[i] - d_each_level[i - 1]))) / (1 + R_TM[i] * R_TM_current * np.exp(2 * complex(0, 1) * k_iz[i + 1] * (d_each_level[i] - d_each_level[i - 1])))

        T_TM_current = R_TM_current + 1
        T_TE_current = R_TE_current + 1

        R_zn = R_TM_current[88]
        Z_n1 = np.sqrt(miu[0] / ebuxiro[0]) * (1 + R_zn * np.exp(k_iz[0] * (-1) * complex(0, 1)))/ (1 - R_zn * np.exp(k_iz[0] * (-1) * complex(0, 1)))
        Z_ni = np.sqrt(Z_n1[0].real**2 + Z_n1[0].imag**2)
        print(Z_ni)
        self.ui.surface_impedance_2.setText(str(Z_ni))
        self.ui.surface_impedance_2.repaint()

        print("miu = ", miu)
        print("ebuxiro = ", ebuxiro)
        print("d each level = ", d_each_level)

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
        global wave_Mode, curve_Mode, R_TM, R_TE, T_TM, T_TE, R_TE_current
        figure_final = []
        if wave_Mode == 0 or curve_Mode == 0:
            return
        if wave_Mode == 1:
            if curve_Mode == 1:
                figure_final = R_TE_current
            elif curve_Mode == 2:
                figure_final = T_TE_current

        elif wave_Mode == 2:
            if curve_Mode == 1:
                figure_final = R_TM_current
            elif curve_Mode == 2:
                figure_final = T_TM_current
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
