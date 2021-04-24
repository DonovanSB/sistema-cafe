import sys
import os
import time
import schedule
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QDesktopWidget, QWidget, QGridLayout
from PyQt5.QtCore import QThread, QCoreApplication, QProcess
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
route = os.path.dirname(os.path.abspath(__file__))
sys.path.append(route + "/src/widgets")
sys.path.append(route + "/src/providers")
import widgets
import provider

rutaProviders =route + "/src/providers"

class Estacion(QMainWindow):
    def __init__(self):
        super().__init__()
        #--- Variables Ventana------
        self.sizeWindow = QDesktopWidget().availableGeometry()
        #print(sizeWindow)
        self.xWindow = self.sizeWindow.x()
        self.yWindow = self.sizeWindow.y()
        self.width = 900
        self.height = 550

        #----Inicializacion Ventana---
        self.setWindowTitle("Estación Fermentación")
        self.setGeometry(self.yWindow,self.xWindow,self.width,self.height)
        self.setStyleSheet("QMainWindow {background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #9e9e9e, stop:1 #707070)}")
        self.centerWindow()
        # Signals
        self.signals = provider.Signals()
        self.signals.signalUpdateGraph.connect(self.updateGraph)
        self.signals.signalAlert.connect(self.alerts)
        self.signals.signalMessages.connect(self.messages)
        self.signals.signalUpdatePrefs.connect(self.restartApp)
        #---Crear Widgets---
        self.createWidgets()

        #--- Inicio de Instacias de providers
        self.plot = provider.Plotter(self.graph.figure,self.graph.ax1)
        self.data = provider.Data(self.loading,
                                  self.environment.tempValue,
                                  self.environment.humValue,
                                  self.temperature1.text,
                                  self.temperature2.text,
                                  self.temperature3.text,
                                  self.temperature4.text,
                                  self.refractometer.text,
                                  self.phWidget.text)
        self.prefs = provider.LocalStorage(route=rutaProviders, name = 'prefs')

        #Señal para actualizar Datos servidor
        self.updateServerPrefs = False
        #----Iniciar subproceso---
        self.initTask = True

        self.thread = Thread(self.data)
        self.thread.start()

        #-- Mostrar Ventana---
        self.showMaximized()
        self.setFocus()

    def restartApp(self):
        QCoreApplication.quit()
        QProcess.startDetached(sys.executable, sys.argv)

    def closeEvent(self, event):
        reply = QMessageBox.question(None,'',"¿Realmente desea cerrar la aplicación?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.thread.stop()
            self.data.threadForever.stop()
            self.data.sqlite.con.close()
            self.data.client.sqlite.con.close()
            event.accept()
        else:
            event.ignore()

    def alerts(self, message):
        QMessageBox.critical(None,'Alerta',message, QMessageBox.Ok)

    def messages(self, message):
        self.menuBar.state.setText(message)

    def centerWindow(self):
        sizeScreen = QDesktopWidget().availableGeometry().center()
        sizeWindow = self.geometry()
        self.move(sizeScreen.x()-sizeWindow.width()/2,sizeScreen.y() - sizeWindow.height()/2)

    def createWidgets(self):
        # Datos Actuales
        self.environment = widgets.EnvironmentWidget("Ambiente","18.15 °", "50.85 %")
        self.temperature1 = widgets.RoundedContainer("Temp 1","temperaturayellow.svg","18.23 °C")
        self.temperature2 = widgets.RoundedContainer("Temp 2","temperaturayellow.svg","20.15 °C")
        self.temperature3 = widgets.RoundedContainer("Temp 3","temperaturayellow.svg","22.13 °C")
        self.temperature4 = widgets.RoundedContainer("Temp 4","temperaturayellow.svg","21.13 °C")
        self.refractometer = widgets.RoundedContainerInput("Brix","refractometrosmall.png","50.25 Bx")
        self.phWidget = widgets.RoundedContainerInput("PH","ph.svg","7")

        # Menu de visuzalización
        self.menuVis = widgets.MenuVisualizacion()
        self.menuVis.listaVariables.currentIndexChanged.connect(self.signals.signalUpdateGraph.emit)
        # Grafica
        self.graph = widgets.Graph()
        self.toolbarFig = NavigationToolbar(self.graph.figure, self)
        self.toolbarFig.setStyleSheet("background:rgba(45,208,179,0); color:white; font:20; font-weight: bold")

        # Menu Bar
        self.menuBar = widgets.MenuBar(self.menuBar())

        widgetGrid = QWidget()
        gridLayout = QGridLayout(widgetGrid)
        gridLayout.addWidget(self.environment,0,0)
        gridLayout.addWidget(self.temperature1,0,1)
        gridLayout.addWidget(self.temperature2,0,2)
        gridLayout.addWidget(self.temperature3,0,3)
        gridLayout.addWidget(self.temperature4,0,4)
        gridLayout.addWidget(self.refractometer,0,5)
        gridLayout.addWidget(self.phWidget,0,6)
        gridLayout.addWidget(self.menuVis,1,0)
        gridLayout.addWidget(self.graph,1,1,1,6)
        gridLayout.addWidget(self.toolbarFig,2,0,1,7)
        self.setCentralWidget(widgetGrid)

        self.loading = widgets.Loading(self)

    def updateGraph(self):
        # Graficar
        indexActual = self.menuVis.listaVariables.currentIndex()
        variableActual = self.menuVis.listaVariables.currentText()
        self.plot.plot(self.data.getTime(indexActual), self.data.getData(indexActual),variableActual, indexActual)

class Thread(QThread):
    def __init__(self, data):
        super().__init__()
        self.threadactive = True
        self.data = data
        self.prefs = provider.LocalStorage(route=rutaProviders, name = 'prefs')
        self.samplingTimes = self.data.verifySamplingTimes()
        self.signals = provider.Signals()

    def run(self):
        schedule.every(5).seconds.do(self.data.readAndUpdate)
        schedule.every(int(self.samplingTimes["env"])).seconds.do(self.data.env)
        schedule.every(int(self.samplingTimes["temp1"])).seconds.do(self.data.temp1)
        schedule.every(int(self.samplingTimes["temp2"])).seconds.do(self.data.temp2)
        schedule.every(int(self.samplingTimes["temp3"])).seconds.do(self.data.temp3)
        schedule.every(int(self.samplingTimes["temp4"])).seconds.do(self.data.temp4)
        while self.threadactive:
            schedule.run_pending()
            time.sleep(0.1)

    def stop(self):
        self.threadactive = False

if __name__ == '__main__':
    App = QApplication(sys.argv)
    window = Estacion()
    sys.exit(App.exec_())
