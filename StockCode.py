import configparser
import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QLineEdit
from pandas import Series, DataFrame
import pandas as pd
import numpy as np

def ReadInI(Route):
    config = configparser.ConfigParser()
    config.read(Route)

    dictionary = {}
    for section in config.sections():
        dictionary[section] = {}
        for option in config.options(section):
            dictionary[section][option] = config.get(section,option)
    return dictionary

dicInitialInfo = ReadInI("Info.ini")
print(dicInitialInfo)

class IndiWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.setWindowTitle("IndiExample")

        # 일반 TR OCX
        self.IndiTR = QAxWidget("GIEXPERTCONTROL.GiExpertControlCtrl.1")

        # 신한i Indi 자동로그인
        while True:
            login = self.IndiTR.StartIndi('{}'.format(dicInitialInfo["info"]["id"]), '{}'.format(dicInitialInfo["info"]["pw"]), '', 'C:/SHINHAN-i/indi/giexpertstarter.exe')
            print(login)
            if login == True :
                break

if __name__ == "__main__":
    app = QApplication(sys.argv)
    IndiWindow = IndiWindow()
    # IndiWindow.show()
    app.exec_()
