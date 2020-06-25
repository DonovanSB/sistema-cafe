#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
parent = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir)
route = os.path.abspath(parent)
sys.path.append(route + "/src/providers")
sys.path.append(route + "/src/windows")
from PyQt5.QtWidgets import QFrame, QLineEdit, QPushButton, QGroupBox,QLabel, QGridLayout, QVBoxLayout,QComboBox, QAction, QDialog, QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QColor, QIcon
import matplotlib.dates as dates
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import provider
import prefs
import keyboard
import login

rutaAssets = route + "/assets/"
class Shadow(QGraphicsDropShadowEffect):
    def __init__(self):
        super(Shadow,self).__init__()
        self.setBlurRadius(5)
        self.setXOffset(0)
        self.setYOffset(3)
        self.setColor(QColor(0,0,0,100))

class RoundedContainer(QFrame):
    def __init__(self,title,iconName,initialValue):
        super(RoundedContainer,self).__init__()
        # Estilo del Frame
        self.setStyleSheet("background-color: white; border-radius:10px; margin:0px 0px 0px 0px")
        self.setFixedHeight(200)
        self.setGraphicsEffect(Shadow())
        #--- Titulo----
        labelTitle = QLabel(title)
        labelTitle.setStyleSheet("background: #0d47a1; color: white; font: 20px; font-weight:bold;border-top-left-radius: 10px; border-top-right-radius: 10px; border-bottom-right-radius: 0px; border-bottom-left-radius: 0px; margin:0px 0px 0px 0px")
        labelTitle.setAlignment(Qt.AlignCenter)
        
        #---Icono---
        icon = QLabel(self)
        pixmapIcon = QPixmap(rutaAssets + iconName)
        icon.setPixmap(pixmapIcon)
        icon.setStyleSheet("background: rgba(0,0,0,0); margin: 0px 0px 0px 0x")    
        icon.setAlignment(Qt.AlignCenter)
        icon.resize(pixmapIcon.width(),pixmapIcon.height())
        
        self.text = QLabel(initialValue)
        self.text.setAlignment(Qt.AlignCenter)
        self.text.setStyleSheet("background: rgba(0,0,0,0);color: black; font: 20px; margin: 0px 0px 0px 0px")


        vbox = QVBoxLayout(self)
        vbox.addWidget(labelTitle)
        vbox.addWidget(icon)
        vbox.addWidget(self.text)
        vbox.setContentsMargins(0,0,0,0)

class RoundedContainerInput(QFrame):
    def __init__(self,title,iconName,initialValue):
        super(RoundedContainerInput,self).__init__()
        self.name = title
        # Estilo del Frame
        self.setStyleSheet("background-color: white; border-radius:10px; margin:0px 0px 0px 0px")
        self.setFixedHeight(200)
        shadow = Shadow()
        self.setGraphicsEffect(shadow)
        
        #--- Titulo----
        labelTitle = QLabel(title)
        labelTitle.setStyleSheet("background: #0d47a1; color: white; font: 20px; font-weight:bold;border-top-left-radius: 10px; border-top-right-radius: 10px; border-bottom-right-radius: 0px; border-bottom-left-radius: 0px; margin:0px 0px 0px 0px")
        labelTitle.setAlignment(Qt.AlignCenter)
        
        #---Icono---
        icon = QLabel(self)
        pixmapIcon = QPixmap(rutaAssets + iconName)
        icon.setPixmap(pixmapIcon)
        icon.setStyleSheet("background: rgba(0,0,0,0); margin: 0px 0px 0px 0px")    
        icon.setAlignment(Qt.AlignCenter)
        icon.resize(pixmapIcon.width(),pixmapIcon.height())
        
        self.text = QLabel(initialValue)
        self.text.setAlignment(Qt.AlignCenter)
        self.text.setStyleSheet("background: rgba(0,0,0,0);color: black; font: 20px; margin: 0px 0px 0px 0px")

        self.styleBottoms = "QPushButton {background-color:#0d47a1; color: white; border-radius: 20px;font: 15px bold; margin: 0px 5px 5px 5px ; padding: 10px;}" "QPushButton:hover { background-color: #5472d3}" "QPushButton:pressed { background-color: #002171}"
        buttomIngresar = QPushButton()
        buttomIngresar.setIcon(QIcon(rutaAssets + "dialpad.svg"))
        buttomIngresar.setIconSize(QSize(30,30))
        buttomIngresar.setStyleSheet(self.styleBottoms)
        buttomIngresar.clicked.connect(self.loadValue)

        grid = QGridLayout(self)
        grid.addWidget(labelTitle,0,0,1,3)
        grid.addWidget(icon,1,0,1,3)
        grid.addWidget(self.text,2,0,1,3)
        grid.addWidget(buttomIngresar,3,1)
        grid.setContentsMargins(0,0,0,0)
    
    def loadValue(self):
        self.keyboard = keyboard.Keyboard(self.name)

class EnvironmentWidget(QFrame):
    def __init__(self,title,initialValue1,initialValue2):
        super(EnvironmentWidget,self).__init__()
        # Estilo del Frame
        self.setStyleSheet("background-color: white; border-radius:10px; margin:0px 0px 0px 0px")
        self.setFixedHeight(200)
        self.setGraphicsEffect(Shadow())
        #--- Titulo----
        labelTitle = QLabel(title)
        labelTitle.setStyleSheet("background: #0d47a1; color: white; font: 20px; font-weight:bold;border-top-left-radius: 10px; border-top-right-radius: 10px; border-bottom-right-radius: 0px; border-bottom-left-radius: 0px; margin:0px 0px 0px 0px")
        labelTitle.setAlignment(Qt.AlignCenter)
        
        #---Icono---
        icon = QLabel(self)
        pixmapIcon = QPixmap(rutaAssets + "temperaturasmall.svg")
        icon.setPixmap(pixmapIcon)
        icon.setStyleSheet("background: rgba(0,0,0,0); margin: 0px 0px 0px 0px")    
        icon.setAlignment(Qt.AlignCenter)
        icon.resize(pixmapIcon.width(),pixmapIcon.height())

        #---Icono---
        icon2 = QLabel(self)
        pixmapIcon2 = QPixmap(rutaAssets + "humedadsmall.svg")
        icon2.setPixmap(pixmapIcon2)
        icon2.setStyleSheet("background: rgba(0,0,0,0); margin: 0px 0px 0px 0px")    
        icon2.setAlignment(Qt.AlignCenter)
        icon2.resize(pixmapIcon2.width(),pixmapIcon2.height())

        #--- Labels--
        labelTemperature = QLabel("Temperatura")
        labelTemperature.setAlignment(Qt.AlignCenter)
        labelTemperature.setStyleSheet("background: rgba(0,0,0,0);color: black; font: 15px; font-weight:bold; margin: 10px 30px 0px 0px")

        self.tempValue = QLabel(initialValue1)
        self.tempValue.setAlignment(Qt.AlignCenter)
        self.tempValue.setStyleSheet("background: rgba(0,0,0,0);color: black; font: 20px; margin: 0px 0px 10px 0px")
        
        labelHumidity = QLabel("Humedad")
        labelHumidity.setAlignment(Qt.AlignCenter)
        labelHumidity.setStyleSheet("background: rgba(0,0,0,0);color: black; font: 15px; font-weight:bold; margin: 10px 30px 0px 0px")
        
        self.humValue = QLabel(initialValue2)
        self.humValue.setAlignment(Qt.AlignCenter)
        self.humValue.setStyleSheet("background: rgba(0,0,0,0);color: black; font: 20px; margin: 0px 0px 10px 0px")

        grid = QGridLayout(self)
        grid.addWidget(labelTitle,0,0,1,2)
        grid.addWidget(icon,1,0,2,1)
        grid.addWidget(labelTemperature,1,1)
        grid.addWidget(self.tempValue,2,1)
        grid.addWidget(icon2,3,0,2,1)
        grid.addWidget(labelHumidity,3,1)
        grid.addWidget(self.humValue,4,1)
        grid.setContentsMargins(0,0,0,0)



class MenuVisualizacion(QFrame):
    def __init__(self):
        super(MenuVisualizacion,self).__init__()
         # Estilo del Frame
        self.setStyleSheet("background-color: white; border-radius:10px; margin:0px 0px 0px 0px")
        self.setFixedHeight(200)
        self.setGraphicsEffect(Shadow())
        #--- Titulo----
        labelTitle = QLabel("Visualización")
        labelTitle.setStyleSheet("background: #0d47a1; color: white; font: 20px; font-weight:bold;border-top-left-radius: 10px; border-top-right-radius: 10px; border-bottom-right-radius: 0px; border-bottom-left-radius: 0px; margin:0px 0px 0px 0px")
        labelTitle.setAlignment(Qt.AlignCenter)

        labelSelecionar = QLabel("Selecionar:")
        labelSelecionar.setStyleSheet("background:rgba(0,0,0,0);color:black;margin: 30px 0px 0px 0px")
        labelSelecionar.setAlignment(Qt.AlignCenter)
        
        #---Lista--
        self.listaVariables = QComboBox()
        self.listaVariables.setStyleSheet("background:#5472d3;color:black; font:18px; padding: 5px 0px 5px 10px; selection-background-color: #0d47a1; margin: 0px 0px 0px 10px; border-radius:10px")
        self.sensores = ["Temperatura R","Humedad R","Temperatura 1", "Temperatura 2", "Temperatura 3","Brix", "PH"]
        self.listaVariables.addItems(self.sensores)

        box = QLabel("")
        box.setStyleSheet("background: transparent;margin: 20px")

        vbox = QVBoxLayout(self)
        vbox.addWidget(labelTitle)
        vbox.addWidget(labelSelecionar)
        vbox.addWidget(self.listaVariables)
        vbox.addWidget(box)
        
        vbox.setContentsMargins(0,0,0,0)
class MenuBar:
    def __init__(self,menuBar):
        self.menuBar = menuBar
        self.menuBar.setStyleSheet("background: #002171; color:white") #263238
        archivoMenu = self.menuBar.addMenu('Archivo')
        preferenciasAction = QAction('Preferencias',self.menuBar, triggered=self.showDialog)
        archivoMenu.addAction(preferenciasAction)
    def showDialog(self):
        self.loginWindow = login.Login()

class Graph(QFrame):
    def __init__(self):
        super(Graph,self).__init__()
        self.setStyleSheet("background-color:white;border-radius:10px")
        self.setGraphicsEffect(Shadow())
        self.FIG = FigureCanvas(Figure(figsize=(2, 12),dpi = 100))
        self.FIG.setStyleSheet("background-color: rgba(60,60,60,150)")

        self.ax1 = self.FIG.figure.add_subplot(111)
        self.formato = dates.DateFormatter("%H:%M")

        vboxFigura = QVBoxLayout(self)
        vboxFigura.addWidget(self.FIG)


