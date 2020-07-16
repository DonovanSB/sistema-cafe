import sys
import os
parent = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
route = os.path.abspath(parent)
sys.path.append( route + "/widgets")
sys.path.append( route + "/providers")
from PyQt5.QtWidgets import QLineEdit, QPushButton, QGroupBox,QLabel, QGridLayout, QVBoxLayout, QDialog
import provider
import widgets

rutaPrefsUser = route + "/providers"

class Preferencias(QDialog):
    def __init__(self):
        super(Preferencias,self).__init__()
        self.setWindowTitle("Preferencias")

        #Estilos
        self.styleBottoms = "QPushButton {background-color:#0d47a1; color: white; border-radius: 5px;font: 15px bold; margin: 5px 5px 5px 5px ; padding: 5px;}" "QPushButton:hover { background-color: #5472d3}" "QPushButton:pressed { background-color: #002171}"
        
        #providers
        self.prefs = provider.LocalStorage(route=rutaPrefsUser, name = 'prefs')
        
        self.signals = provider.Signals()

        self.optionsServer = []

        self.crearWidgets()
        self.show()
    
    def crearWidgets(self):
        self.optionsServer = self.prefs.read()
       
        groupboxServer = QGroupBox("Opciones del servidor ",self)
        
        labelServer = QLabel("Ingresar servidor")
        self.server = QLineEdit()
        if self.optionsServer:
            self.server.setText(self.optionsServer["server"])
        else:
            self.server.setPlaceholderText("192.68.185.27")

        labelTopic = QLabel("Ingresar Topic")
        self.topic = QLineEdit()
        if self.optionsServer:
            self.topic.setText(self.optionsServer["topic"])
        else:
            self.topic.setPlaceholderText("estacion/secado")

        bottomSave = QPushButton("Guardar")
        bottomSave.clicked.connect(self.savePrefs)
        bottomSave.setStyleSheet(self.styleBottoms)
        bottomSave.setGraphicsEffect(widgets.Shadow())

        bottomCancel = QPushButton("Cancelar")
        bottomCancel.clicked.connect(self.closePreferencias)
        bottomCancel.setStyleSheet(self.styleBottoms)
        bottomCancel.setGraphicsEffect(widgets.Shadow())

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
        if self.optionsServer:
            self.routeData.setText(self.optionsServer["routeData"])
        else:
            self.routeData.setPlaceholderText("/home/pi/data")
        
        vboxStorage = QVBoxLayout()
        vboxStorage.addWidget(labelRoute)
        vboxStorage.addWidget(self.routeData)
        groupboxStorage.setLayout(vboxStorage)



        grid = QGridLayout(self)
        grid.addWidget(groupboxServer,0,0,1,2)
        grid.addWidget(groupboxStorage,1,0,1,2)
        grid.addWidget(bottomCancel,2,0)
        grid.addWidget(bottomSave,2,1)

    def closePreferencias(self):
        self.close()

    def savePrefs(self):
        dataJson = {"server":self.server.text(),"topic":self.topic.text(),"routeData":self.routeData.text()}
        self.prefs.update(dataJson)
        self.signals.signalUpdatePrefs.emit(self.routeData.text())
        self.close()