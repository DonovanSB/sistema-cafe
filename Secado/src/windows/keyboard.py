import sys
import os
parent = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir)
route = os.path.abspath(parent)
sys.path.append(route + "/src/providers")
from PyQt5.QtWidgets import QApplication, QLineEdit, QPushButton, QDesktopWidget, QGridLayout, QDialog
from PyQt5 import QtGui, QtCore
import provider

rutaAssets = route + "/assets/"
class Keyboard(QDialog):
    def __init__(self):
        super(Keyboard,self).__init__()
        self.setWindowTitle("Teclado")

        self.setFixedSize(300,350)
        self.centerWindow()
        
        #Inicializaciones
        self.displayList = []
        self.signals = provider.Signals()

        self.createWidgets()
        self.show()
    def createWidgets(self):
        
        self.display = QLineEdit()
        self.display.setStyleSheet("font:20px;margin-left: 30px; margin-right: 30px; padding: 5px")
        
        self.buttom0 = Buttoms()
        self.buttom0.raisedButton("0")
        self.buttom0.clicked.connect(lambda: self.updateDisplay("0"))
        
        self.buttom1 = Buttoms()
        self.buttom1.raisedButton("1")
        self.buttom1.clicked.connect(lambda:self.updateDisplay("1"))
        
        self.buttom2 = Buttoms()
        self.buttom2.raisedButton("2")
        self.buttom2.clicked.connect(lambda:self.updateDisplay("2"))
        
        self.buttom3 = Buttoms()
        self.buttom3.raisedButton("3")
        self.buttom3.clicked.connect(lambda:self.updateDisplay("3"))
        
        self.buttom4 = Buttoms()
        self.buttom4.raisedButton("4")
        self.buttom4.clicked.connect(lambda:self.updateDisplay("4"))
        
        self.buttom5 = Buttoms()
        self.buttom5.raisedButton("5")
        self.buttom5.clicked.connect(lambda:self.updateDisplay("5"))
        
        self.buttom6 = Buttoms()
        self.buttom6.raisedButton("6")
        self.buttom6.clicked.connect(lambda:self.updateDisplay("6"))
        
        self.buttom7 = Buttoms()
        self.buttom7.raisedButton("7")
        self.buttom7.clicked.connect(lambda:self.updateDisplay("7"))
        
        self.buttom8 = Buttoms()
        self.buttom8.raisedButton("8")
        self.buttom8.clicked.connect(lambda:self.updateDisplay("8"))
        
        self.buttom9 = Buttoms()
        self.buttom9.raisedButton("9")
        self.buttom9.clicked.connect(lambda:self.updateDisplay("9"))
        
        self.buttomP = Buttoms()
        self.buttomP.raisedButton(".")
        self.buttomP.clicked.connect(lambda:self.updateDisplay("."))

        self.backspaceButtom = Buttoms()
        self.backspaceButtom.backspace()
        self.backspaceButtom.clicked.connect(self.popList)
        
        self.sendButtom = Buttoms()
        self.sendButtom.send()
        self.sendButtom.clicked.connect(self.sendValue)
        
        grid = QGridLayout(self)
        grid.addWidget(self.display,0,0,1,3)
        grid.addWidget(self.buttom1,1,0)
        grid.addWidget(self.buttom2,1,1)
        grid.addWidget(self.buttom3,1,2)
        grid.addWidget(self.buttom4,2,0)
        grid.addWidget(self.buttom5,2,1)
        grid.addWidget(self.buttom6,2,2)
        grid.addWidget(self.buttom7,3,0)
        grid.addWidget(self.buttom8,3,1)
        grid.addWidget(self.buttom9,3,2)
        grid.addWidget(self.buttomP,4,0)
        grid.addWidget(self.buttom0,4,1)
        grid.addWidget(self.backspaceButtom,4,2)
        grid.addWidget(self.sendButtom,5,1)


    def centerWindow(self):
        S_Screen = QDesktopWidget().availableGeometry().center()
        S_Win = self.geometry()
        self.move(S_Screen.x()-S_Win.width()/2,S_Screen.y() - S_Win.height()/2)
    
    def updateDisplay(self, num):
        self.displayList.append(num)
        self.display.setText("".join(self.displayList))
    
    def popList(self):
        if self.displayList:
            self.displayList.pop()
            self.display.setText("".join(self.displayList))
    
    def sendValue(self):
        try:
            valueDisplay = round(float(self.display.text()),2)
            self.signals.signalUpdateInputValue.emit(valueDisplay)
            self.close()
        except:
            print("ingrese un numero valido")
    

class Buttoms(QPushButton):
    def __init__(self):
        super(Buttoms,self).__init__()
        
    def raisedButton(self,name):
        self.setText(name)
        self.styleButtom ="QPushButton {background-color:#0d47a1; color: white; border-radius: 15px;font: 15px bold; margin: 5px 5px 5px 5px ; padding: 10px;}" "QPushButton:hover { background-color: #5472d3}" "QPushButton:pressed { background-color: #002171}"
        self.setStyleSheet(self.styleButtom)
        
    def backspace(self):
        self.styleButtom ="QPushButton {background-color:rgba(0,0,0,0); color: white; border-radius: 15px;font: 15px bold; margin: 5px 5px 5px 5px }" "QPushButton:hover { background-color: #cfcfcf}" "QPushButton:pressed { background-color: #484848}"
        self.setStyleSheet(self.styleButtom)
        self.setIcon(QtGui.QIcon(rutaAssets + "backspace.svg"))
        self.setIconSize(QtCore.QSize(40,40))
   
    def send(self):
        self.styleButtom ="QPushButton {background-color:#00c853; color: white; border-radius: 15px;font: 15px bold; margin: 5px 5px 5px 5px }" "QPushButton:hover { background-color: #5efc82}" "QPushButton:pressed { background-color: #009624}"
        self.setStyleSheet(self.styleButtom)
        self.setIcon(QtGui.QIcon(rutaAssets + "send.svg"))
        self.setIconSize(QtCore.QSize(40,40))