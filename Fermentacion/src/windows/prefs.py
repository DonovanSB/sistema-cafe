import sys
import os
from PyQt5.QtWidgets import (
    QScrollArea,
    QMessageBox,
    QWidget,
    QTabWidget,
    QLineEdit,
    QFrame,
    QHBoxLayout,
    QPushButton,
    QGroupBox,
    QLabel,
    QGridLayout,
    QVBoxLayout,
    QDialog,
)
from PyQt5.QtCore import Qt

parent = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir)
route = os.path.abspath(parent)
sys.path.append(route + "/widgets")
sys.path.append(route + "/providers")
import provider
import widgets

rutaPrefsUser = route + "/providers"


class Conexion(QWidget):
    def __init__(self, prefs):
        super().__init__()
        self.preferences = prefs
        groupboxConexion = QGroupBox("Opciones de MQTT")

        labelServer = QLabel("Servidor")
        labelServer.setMaximumWidth(150)
        self.server = QLineEdit()
        self.server.setMaximumWidth(300)
        try:
            if self.preferences:
                self.server.setText(self.preferences["server"])
            else:
                self.server.setPlaceholderText("192.68.185.27")
        except:
            print("No se encontró servidor en las preferencias del usuario")
        labelPort = QLabel("Puerto")
        labelPort.setMaximumWidth(150)
        self.port = QLineEdit()
        self.port.setMaximumWidth(300)
        try:
            if self.preferences:
                self.port.setText(str(self.preferences["port"]))
        except:
            print("No se encontró puerto en las preferencias del usuario")
        labelUser = QLabel("Usuario")
        labelUser.setMaximumWidth(150)
        self.user = QLineEdit()
        self.user.setMaximumWidth(300)
        try:
            if self.preferences:
                self.user.setText(self.preferences["user"])
        except:
            print("No se encontró usuario mqtt en las preferencias del usuario")

        labelPassword = QLabel("Contraseña")
        labelPassword.setMaximumWidth(150)
        self.password = QLineEdit()
        self.password.setMaximumWidth(300)
        self.password.setEchoMode(QLineEdit.Password)
        try:
            if self.preferences:
                self.password.setText(self.preferences["password"])
        except:
            print("No se encontró contraseña mqtt en las preferencias del usuario")

        groupboxTopics = QGroupBox("Topics")

        self.namesSensors = [
            "Hum Ambiente",
            "Temp Ambiente",
            "Temperatura 1",
            "Temperatura 2",
            "Temperatura 3",
            "Temperatura 4",
            "Brix",
            "PH",
        ]
        self.savedNames = [
            "humEnv",
            "tempEnv",
            "temp1",
            "temp2",
            "temp3",
            "temp4",
            "brix",
            "ph",
        ]
        numSensors = len(self.namesSensors)
        labelsSensors = []
        for name in self.namesSensors:
            label = QLabel(name)
            label.setMaximumWidth(150)
            labelsSensors.append(label)
        self.inputsSensors = []
        for i in range(numSensors):
            lineEdit = QLineEdit()
            lineEdit.setMaximumWidth(500)
            self.inputsSensors.append(lineEdit)

        try:
            if self.preferences["topics"]:
                topics = self.preferences["topics"]
                for i in range(numSensors):
                    self.inputsSensors[i].setText(topics[self.savedNames[i]])
        except:
            print("No se encontraron topics en las preferencias del usuario")

        grid = QGridLayout(groupboxTopics)
        grid.setAlignment(Qt.AlignTop)
        for i in range(numSensors):
            grid.addWidget(labelsSensors[i], i, 0)
            grid.addWidget(self.inputsSensors[i], i, 1)

        gridConexion = QGridLayout(groupboxConexion)
        gridConexion.setAlignment(Qt.AlignTop)
        gridConexion.addWidget(labelServer, 0, 0)
        gridConexion.addWidget(self.server, 0, 1)
        gridConexion.addWidget(labelPort, 0, 2)
        gridConexion.addWidget(self.port, 0, 3)
        gridConexion.addWidget(labelUser, 1, 0)
        gridConexion.addWidget(self.user, 1, 1)
        gridConexion.addWidget(labelPassword, 1, 2)
        gridConexion.addWidget(self.password, 1, 3)
        gridConexion.addWidget(groupboxTopics, 2, 0, 1, 4)

        vbox = QVBoxLayout()
        vbox.addWidget(groupboxConexion)
        self.setLayout(vbox)


class Storage(QWidget):
    def __init__(self, prefs):
        super().__init__()
        self.preferences = prefs
        # ---Storage---
        groupboxStorage = QGroupBox("Opciones de almacenamiento ")

        labelRoute = QLabel("Ingresar ruta de almacenamiento:")
        self.routeData = QLineEdit()
        if self.preferences:
            self.routeData.setText(self.preferences["routeData"])
        else:
            self.routeData.setPlaceholderText("/home/pi/data")

        # Limites de almacenamiento
        self.storageLimits = StorageLimits(self.preferences)

        vboxStorage = QVBoxLayout()
        vboxStorage.setAlignment(Qt.AlignTop)
        vboxStorage.addWidget(labelRoute)
        vboxStorage.addWidget(self.routeData)
        groupboxStorage.setLayout(vboxStorage)
        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignTop)
        vbox.addWidget(groupboxStorage)
        vbox.addWidget(self.storageLimits)
        self.setLayout(vbox)


class StorageLimits(QWidget):
    def __init__(self, prefs):
        super().__init__()
        self.preferences = prefs
        # Tiempos de muestreo
        groupboxTS = QGroupBox("Límites de almacenamiento (días)")

        self.namesSensors = ["Datos principales", "Datos temporales"]
        self.savedNames = ["mainData", "tempData"]
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
            if self.preferences["storageLimits"]:
                storageLimits = self.preferences["storageLimits"]
                for i in range(numSensors):
                    self.inputsSensors[i].setText(
                        str(storageLimits[self.savedNames[i]])
                    )
        except:
            print(
                "No se encontraron limites de días de almacenamiento en las preferencias del usuario"
            )

        gridTS = QGridLayout()
        gridTS.setAlignment(Qt.AlignTop)
        for i in range(numSensors):
            gridTS.addWidget(labelsSensors[i], i, 0)
            gridTS.addWidget(self.inputsSensors[i], i, 1)
        groupboxTS.setLayout(gridTS)
        vbox = QVBoxLayout()
        vbox.addWidget(groupboxTS)
        self.setLayout(vbox)


class SamplingTime(QWidget):
    def __init__(self, prefs):
        super().__init__()
        self.preferences = prefs
        # Tiempos de muestreo
        groupboxTS = QGroupBox("Tiempos de muestreo (segundos)")

        self.namesSensors = [
            "Ambiente",
            "Temperatura 1",
            "Temperatura 2",
            "Temperatura 3",
            "Temperatura 4",
        ]
        self.savedNames = ["env", "temp1", "temp2", "temp3", "temp4"]
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
            print(
                "No se encontraron tiempos de muestreo en las preferencias del usuario"
            )

        gridTS = QGridLayout()
        gridTS.setAlignment(Qt.AlignTop)
        for i in range(numSensors):
            gridTS.addWidget(labelsSensors[i], i, 0)
            gridTS.addWidget(self.inputsSensors[i], i, 1)
        groupboxTS.setLayout(gridTS)
        vbox = QVBoxLayout()
        vbox.addWidget(groupboxTS)
        self.setLayout(vbox)


class Preferencias(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Preferencias")
        self.setMinimumWidth(400)

        # Estilos
        self.styleButtons = """QPushButton {background-color:#0d47a1;
                                            color: white;
                                            border-radius: 5px;
                                            font: 15px bold;
                                            margin: 5px 5px 5px 5px;
                                            padding: 5px;}
                            QPushButton:hover {background-color: #5472d3}
                            QPushButton:pressed {background-color: #002171}"""
        # providers
        self.prefs = provider.LocalStorage(route=rutaPrefsUser, name="prefs")
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

        self.tabWidget.addTab(self.conexion, "Conexión")
        self.tabWidget.addTab(self.storage, "Almacenamiento")
        self.tabWidget.addTab(self.time, "Tiempos")
        grid = QGridLayout()
        grid.addWidget(self.tabWidget, 0, 0, 1, 2)
        grid.addWidget(frameButtons, 1, 1)

        scroll = QScrollArea()
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(540)
        widget = QWidget()
        widget.setLayout(grid)
        scroll.setWidget(widget)
        vbox = QVBoxLayout()
        vbox.addWidget(scroll)
        vbox.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vbox)

    def closePreferencias(self):
        self.close()

    def savePrefs(self):
        samplingTimes = {}
        for i in range(len(self.time.namesSensors)):
            samplingTimes.update(
                {self.time.savedNames[i]: self.time.inputsSensors[i].text()}
            )
        topics = {}
        for i in range(len(self.conexion.savedNames)):
            topics.update(
                {self.conexion.savedNames[i]: self.conexion.inputsSensors[i].text()}
            )
        dataJson = {
            "server": self.conexion.server.text(),
            "port": int(self.conexion.port.text()),
            "user": self.conexion.user.text(),
            "password": self.conexion.password.text(),
            "topics": topics,
            "routeData": self.storage.routeData.text(),
            "samplingTimes": samplingTimes,
            "storageLimits": {
                "mainData": int(self.storage.storageLimits.inputsSensors[0].text()),
                "tempData": int(self.storage.storageLimits.inputsSensors[1].text()),
            },
        }
        self.prefs.update(dataJson)
        self.close()
        reply = QMessageBox.question(
            None,
            " ",
            "Los cambios harán efecto después de reiniciar la aplicación ¿Desea reiniciar la aplicación ahora?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.signals.signalUpdatePrefs.emit()
