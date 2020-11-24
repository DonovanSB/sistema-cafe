import sys
import os
from PyQt5.QtWidgets import QScrollArea, QMessageBox, QWidget, QTabWidget, QLineEdit, QFrame, QPushButton, QGroupBox,QLabel, QGridLayout, QVBoxLayout, QHBoxLayout, QDialog
from PyQt5.QtCore import Qt
parent = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
route = os.path.abspath(parent)
sys.path.append(route + "/widgets")
sys.path.append(route + "/providers")
import provider
import widgets

rutaPrefsUser =route + "/providers"

class Conexion(QWidget):
    def __init__(self, prefs):
        super().__init__()
        self.preferences = prefs
        groupboxServer = QGroupBox("Opciones del conexión")

        labelServer = QLabel("Ingresar servidor")
        self.server = QLineEdit()
        self.server.setMaximumWidth(300)
        if self.preferences:
            self.server.setText(self.preferences["server"])
        else:
            self.server.setPlaceholderText("192.68.185.27")

        labelTopic = QLabel("Ingresar Topic")
        self.topic = QLineEdit()
        self.topic.setMaximumWidth(300)
        if self.preferences:
            self.topic.setText(self.preferences["topic"])
        else:
            self.topic.setPlaceholderText("estacion/secado")
        vboxServer = QVBoxLayout()
        vboxServer.setAlignment(Qt.AlignTop)
        vboxServer.addWidget(labelServer)
        vboxServer.addWidget(self.server)
        vboxServer.addWidget(labelTopic)
        vboxServer.addWidget(self.topic)
        groupboxServer.setLayout(vboxServer)

        vbox = QVBoxLayout()
        vbox.addWidget(groupboxServer)
        self.setLayout(vbox)

class Storage(QWidget):
    def __init__(self, prefs):
        super().__init__()
        self.preferences = prefs
        #---Storage---
        groupboxStorage = QGroupBox("Opciones de almacenamiento ")

        labelRoute = QLabel("Ingresar ruta de almacenamiento:")
        self.routeData = QLineEdit()
        if self.preferences:
            self.routeData.setText(self.preferences["routeData"])
        else:
            self.routeData.setPlaceholderText("/home/pi/data")

        vboxStorage = QVBoxLayout()
        vboxStorage.setAlignment(Qt.AlignTop)
        vboxStorage.addWidget(labelRoute)
        vboxStorage.addWidget(self.routeData)
        groupboxStorage.setLayout(vboxStorage)
        vbox = QVBoxLayout()
        vbox.addWidget(groupboxStorage)
        self.setLayout(vbox)

class SamplingTime(QWidget):
    def __init__(self, prefs):
        super().__init__()
        self.preferences = prefs
        # Tiempos de muestreo
        groupboxTS = QGroupBox("Tiempos de muestreo (segundos)")

        self.namesSensors = ["Ambiente", "Zona 1", "Zona 2", "Zona 3"]
        self.savedNames = ["env","env1","env2","env3"]
        numSensors = len(self.namesSensors)
        labelsSensors = []
        for name in self.namesSensors:
            label = QLabel(name)
            label.setMaximumWidth(150)
            labelsSensors.append(label)
        self.inputsSensors = []
        for i in range(numSensors):
            lineEdit = QLineEdit()
            lineEdit.setMaximumWidth(200)
            self.inputsSensors.append(lineEdit)

        try:
            if self.preferences["samplingTimes"]:
                samplingTimes = self.preferences["samplingTimes"]
                for i in range(numSensors):
                    self.inputsSensors[i].setText(samplingTimes[self.savedNames[i]])
        except:
            print('No se encontraron tiempos de muestreo en las preferencias del usuario')

        gridTS = QGridLayout()
        gridTS.setAlignment(Qt.AlignTop)
        for i in range(numSensors):
            gridTS.addWidget(labelsSensors[i],i,0)
            gridTS.addWidget(self.inputsSensors[i],i,1)
        groupboxTS.setLayout(gridTS)
        vbox = QVBoxLayout()
        vbox.addWidget(groupboxTS)
        self.setLayout(vbox)

class Preferencias(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Preferencias")
        self.setMinimumWidth(400)

        #Estilos
        self.styleButtons = "QPushButton {background-color:#0d47a1; color: white; border-radius: 5px;font: 15px bold; margin: 0px 5px 0px 0px ; padding: 5px 10px 5px 10px;}" "QPushButton:hover { background-color: #5472d3}" "QPushButton:pressed { background-color: #002171}"

        #providers
        self.prefs = provider.LocalStorage(route=rutaPrefsUser, name = 'prefs')
        self.signals = provider.Signals()

        self.preferences = []

        self.crearWidgets()
        self.show()

    def crearWidgets(self):

        self.tabWidget = QTabWidget()
        self.preferences = self.prefs.read()

        self.conexion = Conexion(self.preferences)
        self.storage = Storage(self.preferences)
        self.time = SamplingTime(self.preferences)

        buttonSave = QPushButton("Guardar")
        buttonSave.clicked.connect(self.savePrefs)
        buttonSave.setStyleSheet(self.styleButtons)
        buttonSave.setGraphicsEffect(widgets.Shadow())

        buttonCancel = QPushButton("Cancelar")
        buttonCancel.clicked.connect(self.closePreferencias)
        buttonCancel.setStyleSheet(self.styleButtons)
        buttonCancel.setGraphicsEffect(widgets.Shadow())

        frameButtons = QFrame()
        hboxButtons = QHBoxLayout(frameButtons)
        hboxButtons.addWidget(buttonSave)
        hboxButtons.addWidget(buttonCancel)

        # scroll = QScrollArea()
        # scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # scroll.setWidgetResizable(True)
        # scroll.setMinimumHeight(540)
        # widget = QWidget()
        # widget.setLayout(grid)
        # scroll.setWidget(widget)
        # vbox = QVBoxLayout()
        # vbox.addWidget(scroll)
        # vbox.setContentsMargins(0,0,0,0)
        # self.setLayout(vbox)

        self.tabWidget.addTab(self.conexion, 'Conexión')
        self.tabWidget.addTab(self.storage, 'Almacenamiento')
        self.tabWidget.addTab(self.time, 'Tiempos')
        grid = QGridLayout()
        grid.addWidget(self.tabWidget,0,0,1,2)
        grid.addWidget(frameButtons,1,1)
        self.setLayout(grid)


    def closePreferencias(self):
        self.close()

    def savePrefs(self):
        samplingTimes = {}
        for i in range(len(self.time.namesSensors)):
            samplingTimes.update({self.time.savedNames[i]: self.time.inputsSensors[i].text()})
        dataJson = {"server":self.conexion.server.text(),
                    "topic":self.conexion.topic.text(),
                    "routeData":self.storage.routeData.text(),
                    "samplingTimes": samplingTimes}
        self.prefs.update(dataJson)
        self.close()
        reply = QMessageBox.question(None,' ',"Los cambios harán efecto después de reiniciar la aplicación ¿Desea reiniciar la aplicación ahora?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.signals.signalUpdatePrefs.emit()
