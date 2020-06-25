#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
route = os.path.dirname(os.path.abspath(__file__))
sys.path.append(route + "/src/widgets")
sys.path.append(route + "/src/providers")
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QWidget, QGridLayout, QAction, QDialog
from PyQt5.QtCore import QThread, QTimer,pyqtSignal, QObject
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
import widgets
import provider
import threading
import schedule

rutaProviders =route + "/src/providers"

class Estacion(QMainWindow):
    def __init__(self):
        super(Estacion,self).__init__()
        #--- Variables Ventana------
        self.sizeWindow = QDesktopWidget().availableGeometry()
        #print(sizeWindow)
        self.x = self.sizeWindow.x()
        self.y = self.sizeWindow.y()
        self.width = 900
        self.height = 550

        #----Inicializacion Ventana---
        self.setWindowTitle("Estación 1")
        self.setGeometry(self.y,self.x,self.width,self.height)
        self.setStyleSheet("QWidget {background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #9e9e9e, stop:1 #707070)}")
        self.centerWindow()
        
        #---Crear Widgets---
        self.createWidgets()

        #--- Inicio de Instacias de providers
        self.plot = provider.Plotter(self.graph.FIG,self.graph.ax1)
        self.data = provider.Data( self.temperaturaWidget.text, self.humedadWidget.text, self.irradWidget.text, self.velocidadWidget.text, self.direccionWidget.text, self.lluviaWidget.text)
        self.signals = provider.Signals()
        self.signals.signalServerUpdate.connect(self.updateServer)
        self.prefs = provider.LocalStorage()
        self.prefs.beginPrefs(route=rutaProviders)

        #Señal para actualizar Datos servidor
        self.updateServerPrefs = False
        
        #----Iniciar subproceso---
        self.initTask = True

        timer = QTimer(self)
        timer.timeout.connect(self.task2)
        timer.start(1000)
        #-- Mostrar Ventana---
        self.show()

    def centerWindow(self):
        S_Screen = QDesktopWidget().availableGeometry().center()
        S_Win = self.geometry()
        self.move(S_Screen.x()-S_Win.width()/2,S_Screen.y() - S_Win.height()/2)
    
    def createWidgets(self):
        # Datos Actuales
        self.temperaturaWidget = widgets.RoundedContainer("Temperatura","temperatura.svg","25 °C")
        self.humedadWidget = widgets.RoundedContainer("Humedad","humedad.svg","50 %")
        self.irradWidget = widgets.RoundedContainer("Irradiancia","irrad.png","200 W/m²")
        self.velocidadWidget = widgets.RoundedContainer("Velocidad\n Viento","velocidad.svg","10 km/h")
        self.direccionWidget = widgets.RoundedContainer("Dirección\n Viento","direccion.png","90 °")
        self.lluviaWidget = widgets.RoundedContainer("Lluvia","lluvia.png","50 cm/h")

        # Menu de visuzalización
        self.menuVis = widgets.MenuVisualizacion()
        # Grafica 
        self.graph = widgets.Graph()
        self.toolbarFig = NavigationToolbar(self.graph.FIG, self)
        self.toolbarFig.setStyleSheet("background:rgba(45,208,179,0); color:white; font:20; font-weight: bold")

        # Menu Bar
        self.menuBar = widgets.MenuBar(self.menuBar())

        widgetGrid = QWidget()      
        gridLayout = QGridLayout(widgetGrid)
        gridLayout.addWidget(self.temperaturaWidget,0,0)
        gridLayout.addWidget(self.humedadWidget,0,1)
        gridLayout.addWidget(self.irradWidget,0,2)
        gridLayout.addWidget(self.velocidadWidget,0,3)
        gridLayout.addWidget(self.direccionWidget,0,4)
        gridLayout.addWidget(self.lluviaWidget,0,5)
        gridLayout.addWidget(self.menuVis,1,0,1,2)
        gridLayout.addWidget(self.graph,1,2,1,4)
        gridLayout.addWidget(self.toolbarFig,2,0,1,6)
        self.setCentralWidget(widgetGrid)

    def updateServer(self, update):
        self.updateServerPrefs = update


    def task2(self):
        
        if self.initTask:
            self.thread = Thread(5,self.data)
            self.thread.updateSignal.connect(self.task3)
            self.thread.start()
            self.initTask = False

        if(self.updateServerPrefs):
            print(self.prefs.readPrefs()["server"])
            print(self.prefs.readPrefs()["topic"])
            print(self.prefs.readPrefs()["routeData"])
            self.updateServerPrefs = False
            
    def task3(self):
        # Graficar
        indexActual = self.menuVis.listaVariables.currentIndex()
        variableActual = self.menuVis.listaVariables.currentText()
        self.plot.plot(self.data.timeData, self.data.datos[indexActual],variableActual, indexActual)
    
class Thread(QThread):
    updateSignal = pyqtSignal()
    def __init__(self,time,data):
        super(Thread,self).__init__()
        self.time = time
        self.data = data

    def run(self):
        schedule.every(self.time).seconds.do(self.task)
        while True:
            schedule.run_pending()
            time.sleep(0.1)

    def task(self):
        self.data.readData()
        self.updateSignal.emit()

if __name__ == '__main__':
    App = QApplication(sys.argv)
    window = Estacion()
    sys.exit(App.exec_())