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
        self.setWindowTitle("Estación 1")
        self.setGeometry(self.yWindow,self.xWindow,self.width,self.height)
        self.setStyleSheet("QWidget {background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 #9e9e9e, stop:1 #707070)}")
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
                                  self.temperaturaWidget.text,
                                  self.humedadWidget.text,
                                  self.irradWidget.text,
                                  self.velocidadWidget.text,
                                  self.direccionWidget.text,
                                  self.lluviaWidget.text)
        self.prefs = provider.LocalStorage(route=rutaProviders, name = 'prefs')

        #----Iniciar subproceso---
        self.initTask = True

        self.thread = Thread(self.data)
        self.thread.start()

        #-- Mostrar Ventana---
        self.showMaximized()
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
        self.move(sizeScreen.x()-int(sizeWindow.width()/2),sizeScreen.y() - int(sizeWindow.height()/2))

    def createWidgets(self):
        # Datos Actuales
        self.temperaturaWidget = widgets.RoundedContainer("Temperatura","temperatura.svg","25 °C")
        self.humedadWidget = widgets.RoundedContainer("Humedad","humedad.svg","50 %")
        self.irradWidget = widgets.RoundedContainer("Irradiancia","irrad.png","200 W/m²")
        self.velocidadWidget = widgets.RoundedContainer("Velocidad\n Viento","velocidad.svg","10 km/h")
        self.direccionWidget = widgets.RoundedContainer("Dirección\n Viento","direccion.png","90 °")
        self.lluviaWidget = widgets.RoundedContainer("Lluvia","lluvia.png","0 cm/día")

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

        self.loading = widgets.Loading(self)

    def updateGraph(self):
        # Graficar
        indexActual = self.menuVis.listaVariables.currentIndex()
        variableActual = self.menuVis.listaVariables.currentText()
        self.plot.plot(self.data.getTime(indexActual), self.data.getData(indexActual),variableActual, indexActual)

class Thread(QThread):
    def __init__(self,data):
        super().__init__()
        self.data = data
        self.threadactive = True
        self.prefs = provider.LocalStorage(route=rutaProviders, name = 'prefs')
        self.samplingTimes = self.data.verifySamplingTimes()
        self.signals = provider.Signals()

    def run(self):
        schedule.every(5).seconds.do(self.data.readAndUpdate)
        schedule.every(int(self.samplingTimes["env"])).seconds.do(self.data.env)
        schedule.every(int(self.samplingTimes["env"])).seconds.do(self.data.env)
        schedule.every(int(self.samplingTimes["irrad"])).seconds.do(self.data.irrad)
        schedule.every(int(self.samplingTimes["speed"])).seconds.do(self.data.windSpeed)
        schedule.every(int(self.samplingTimes["direction"])).seconds.do(self.data.windDirection)
        schedule.every(int(self.samplingTimes["rain"])).seconds.do(self.data.rain)

        while self.threadactive :
            schedule.run_pending()
            time.sleep(0.1)

    def stop(self):
        self.threadactive = False

if __name__ == '__main__':
    App = QApplication(sys.argv)
    window = Estacion()
    sys.exit(App.exec_())
