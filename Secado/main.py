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

rutaProviders = route + "/src/providers"

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
        self.setWindowTitle("Estación Secado")
        self.setGeometry(self.yWindow,self.xWindow,self.width,self.height)
        self.setStyleSheet("QMainWindow {background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #9e9e9e, stop:1 #707070)}")
        self.centerWindow()
        # signals
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
                                  self.zone1.tempValue,
                                  self.zone1.humValue,
                                  self.zone2.tempValue,
                                  self.zone2.humValue,
                                  self.zone3.tempValue,
                                  self.zone3.humValue,
                                  self.humGrain.text)
        self.prefs = provider.LocalStorage(route=rutaProviders, name = 'prefs')

        #----Iniciar subproceso---
        self.initTask = True

        self.thread = Thread(self.data)
        self.thread.start()

        #-- Mostrar Ventana---
        self.show()
        self.setFocus()
    def restartApp(self):
        QCoreApplication.quit()
        QProcess.startDetached(sys.executable, sys.argv)

    def closeEvent(self, event):
        reply = QMessageBox.question(None,' ',"¿Realmente desea cerrar la aplicación?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
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
        self.environment = widgets.EnvironmentWidget("Ambiente","18 °C", "50 %")
        self.zone1 = widgets.EnvironmentWidget("Zona 1","15 °C", "50 %")
        self.zone2 = widgets.EnvironmentWidget("Zona 2","17 °C", "50 %")
        self.zone3 = widgets.EnvironmentWidget("Zona 3","17 °C", "50 %")
        self.humGrain = widgets.RoundedContainerInput("Humedad Grano","humedadpurpleSmall.svg","50 %")

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
        gridLayout.addWidget(self.zone1,0,1)
        gridLayout.addWidget(self.zone2,0,2)
        gridLayout.addWidget(self.zone3,0,3)
        gridLayout.addWidget(self.humGrain,0,4)
        gridLayout.addWidget(self.menuVis,1,0)
        gridLayout.addWidget(self.graph,1,1,1,4)
        gridLayout.addWidget(self.toolbarFig,2,0,1,5)
        self.setCentralWidget(widgetGrid)

        self.loading = widgets.Loading(self)

    def updateGraph(self):
        # Graficar
        indexActual = self.menuVis.listaVariables.currentIndex()
        variableActual = self.menuVis.listaVariables.currentText()
        self.plot.plot(self.data.getTime(indexActual), self.data.getData(indexActual),variableActual, indexActual)

class Thread(QThread):

    def __init__(self,data):
        super().__init__()
        self.threadactive = True
        self.data = data
        self.prefs = provider.LocalStorage(route=rutaProviders, name = 'prefs')
        self.samplingTimes = self.data.verifySamplingTimes()

    def run(self):
        schedule.every(int(self.samplingTimes["env"])).seconds.do(self.data.env)
        schedule.every(int(self.samplingTimes["env1"])).seconds.do(self.data.env1)
        schedule.every(int(self.samplingTimes["env2"])).seconds.do(self.data.env2)
        schedule.every(int(self.samplingTimes["env3"])).seconds.do(self.data.env3)

        while self.threadactive:
            schedule.run_pending()
            time.sleep(0.1)
    def stop(self):
        self.threadactive = False

if __name__ == '__main__':
    App = QApplication(sys.argv)
    window = Estacion()
    sys.exit(App.exec_())
