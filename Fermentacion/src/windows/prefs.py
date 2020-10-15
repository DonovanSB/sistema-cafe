import sys
import os
from PyQt5.QtWidgets import QScrollArea, QWidget, QLineEdit, QFrame, QHBoxLayout, QPushButton, QGroupBox,QLabel, QGridLayout, QVBoxLayout, QDialog
from PyQt5.QtCore import Qt
parent = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
route = os.path.abspath(parent)
sys.path.append(route + "/widgets")
sys.path.append(route + "/providers")
import provider
import widgets

rutaPrefsUser =route + "/providers"
class Preferencias(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Preferencias")

        #Estilos
        self.styleButtons = """QPushButton {background-color:#0d47a1;
                                            color: white;
                                            border-radius: 5px;
                                            font: 15px bold;
                                            margin: 5px 5px 5px 5px;
                                            padding: 5px;}
                            QPushButton:hover {background-color: #5472d3}
                            QPushButton:pressed {background-color: #002171}"""
        #providers
        self.prefs = provider.LocalStorage(route=rutaPrefsUser, name = 'prefs')
        self.signals = provider.Signals()
        self.preferences = []
        self.crearWidgets()
        self.show()

    def crearWidgets(self):
        self.preferences = self.prefs.read()     
        groupboxServer = QGroupBox("Opciones del servidor ",self)

        labelServer = QLabel("Ingresar servidor")
        self.server = QLineEdit()
        if self.preferences:
            self.server.setText(self.preferences["server"])
        else:
            self.server.setPlaceholderText("192.68.185.27")

        labelTopic = QLabel("Ingresar Topic")
        self.topic = QLineEdit()
        if self.preferences:
            self.topic.setText(self.preferences["topic"])
        else:
            self.topic.setPlaceholderText("estacion/fermentacion")

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
        hboxButtons.addWidget(buttonCancel)
        hboxButtons.addWidget(buttonSave)

        vboxServer = QVBoxLayout()
        vboxServer.addWidget(labelServer)
        vboxServer.addWidget(self.server)
        vboxServer.addWidget(labelTopic)
        vboxServer.addWidget(self.topic)
        groupboxServer.setLayout(vboxServer)

        #---Storage---
        groupboxStorage = QGroupBox("Opciones de almacenamiento ",self)
        labelRoute = QLabel("Ingresar ruta de almacenamiento:")
        self.routeData = QLineEdit()
        if self.preferences:
            self.routeData.setText(self.preferences["routeData"])
        else:
            self.routeData.setPlaceholderText("/home/pi/data")
        vboxStorage = QVBoxLayout()
        vboxStorage.addWidget(labelRoute)
        vboxStorage.addWidget(self.routeData)
        groupboxStorage.setLayout(vboxStorage)

        # Tiempos de muestreo
        groupboxTS = QGroupBox("Tiempos de muestreo (segundos)", self)

        self.namesSensors = ["Ambiente", "Temperatura 1", "Temperatura 2", "Temperatura 3", "Temperatura 4"]
        self.savedNames = ["env","temp1","temp2","temp3","temp4"]
        numSensors = len(self.namesSensors)
        labelsSensors = []
        for name in self.namesSensors:
            labelsSensors.append(QLabel(name, self))
        self.inputsSensors = []
        for i in range(numSensors):
            self.inputsSensors.append(QLineEdit())
        
        try: 
            if self.preferences["samplingTimes"]:
                samplingTimes = self.preferences["samplingTimes"]
                for i in range(numSensors):
                    self.inputsSensors[i].setText(samplingTimes[self.savedNames[i]])
        except:
            print('No se encontraron tiempos de muestreo en las preferencias del usuario')

        gridTS = QGridLayout()
        for i in range(numSensors):
            gridTS.addWidget(labelsSensors[i],i,0)
            gridTS.addWidget(self.inputsSensors[i],i,1)
        groupboxTS.setLayout(gridTS)

        grid = QGridLayout()
        grid.addWidget(groupboxServer,0,0,1,2)
        grid.addWidget(groupboxStorage,1,0,1,2)
        grid.addWidget(groupboxTS,2,0)
        grid.addWidget(frameButtons,3,1)
        
        scroll = QScrollArea()
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(540)
        widget = QWidget()
        widget.setLayout(grid)
        scroll.setWidget(widget)
        vbox = QVBoxLayout()
        vbox.addWidget(scroll)
        vbox.setContentsMargins(0,0,0,0)
        self.setLayout(vbox)

    def closePreferencias(self):
        self.close()

    def savePrefs(self):
        samplingTimes = {}
        for i in range(len(self.namesSensors)):
            samplingTimes.update({self.savedNames[i]: self.inputsSensors[i].text()})
        dataJson = {"server":self.server.text(),"topic":self.topic.text(),"routeData":self.routeData.text(), "samplingTimes": samplingTimes}
        self.prefs.update(dataJson)
        self.close()
        self.signals.signalUpdatePrefs.emit(self.routeData.text())
        