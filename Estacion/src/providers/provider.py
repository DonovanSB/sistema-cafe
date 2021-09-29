import os
import time
import json
import logging
import random
import sqlite3
from sqlite3 import Error
from datetime import datetime
import uuid
import matplotlib.dates as dates
from PyQt5.QtCore import pyqtSignal, QObject, QThread, QMutex
import paho.mqtt.client as mqtt
import sensorsStation

rutaPrefsUser = os.path.dirname(os.path.abspath(__file__))

parent = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir)
root = os.path.abspath(parent)
routeDatos = root + '/datos'
logging.basicConfig(filename = root + '/estacion.log', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

qmutex = QMutex()

# Sensores
estacion = sensorsStation.SensorsStation()

def singleton(cls):
    instance = [None]
    def wrapper(*args, **kwargs):
        if instance[0] is None:
            instance[0] = cls(*args, **kwargs)
        return instance[0]

    return wrapper

class Data:
    def __init__(self,loading,textTemp,textHum,textIrrad,textSpeed,textDir,textRain):
        self.loading = loading
        self.textTemp = textTemp
        self.textHum = textHum
        self.textIrrad = textIrrad
        self.textSpeed = textSpeed
        self.textDir = textDir
        self.textRain = textRain

        self.numData = 8000

        self.prefs = LocalStorage(route=rutaPrefsUser, name = 'prefs')
        try:
            route = os.path.abspath(self.prefs.read()['routeData'])
            self.routeData  = self.verifyRoute(route)
        except:
            logging.error('No se pudo encontrar la ruta de almacenamiento de datos en prefs.json')
            self.routeData = routeDatos + '/datos.db'

        # Inicializaciones para almacenamiento de datos
        self.initSQLite(self.routeData)
        self.initDataService()

        self.signals = Signals()
        self.signals.signalIsLoanding.connect(self.isLoading)

        # Mqqt
        self.client = Mqtt()

        # Verificar si hay datos pendiendes en un nuevo hilo
        self.threadForever = ThreadForever(target=self.client.verifyPending)
        self.threadForever.start()

    def verifyRoute(self,route):
        if os.path.exists(route):
            route = os.path.abspath(route + '/data')
        else:
            route = routeDatos + '/data'
        return route

    def verifySamplingTimes(self):
        try:
            samplingTimes = self.prefs.read()["samplingTimes"]
        except:
            logging.error("Tiempos de muestreo no encontrados")
            samplingTimes = {"env":10,"irrad":10,"speed":10,"direction":10,"rain":10}
        return samplingTimes

    def initDataService(self):
        namesEnv = '(time, temperatura, humedad)  VALUES(?, ?, ?)'
        namesIrrad = '(time, irradiancia)  VALUES(?, ?)'
        namesSpeed = '(time, velocidad)  VALUES(?, ?)'
        namesDir = '(time, direccion)  VALUES(?, ?)'
        namesRain = '(time, lluvia)  VALUES(?, ?)'
        self.envService = DataService( self.sqlite, 'Ambiente', namesEnv, ['tempEnv', 'humEnv'], [self.textTemp, self.textHum], self.numData, ["°C", "%"], 2)
        self.irradService = DataService( self.sqlite, 'Irradiancia', namesIrrad, 'irrad', self.textIrrad, self.numData, "W/m²")
        self.speedService = DataService( self.sqlite, 'VelocidadV', namesSpeed, 'speed', self.textSpeed, self.numData, "km/h")
        self.directionService = DataService( self.sqlite, 'DireccionV', namesDir, 'direction', self.textDir, self.numData, "°")
        self.rainService = DataService( self.sqlite, 'Lluvia', namesRain, 'rain', self.textRain, self.numData, "cm/día")

    def initSQLite(self, route):
        self.sqlite = SQLite(nameDB = route)
        self.sqlite.createTable(nameTable = 'Ambiente', fields = '(time date, temperatura real, humedad real)')
        self.sqlite.createTable(nameTable = 'Irradiancia', fields = '(time date, irradiancia real)')
        self.sqlite.createTable(nameTable = 'VelocidadV', fields = '(time date, velocidad real)')
        self.sqlite.createTable(nameTable = 'DireccionV', fields = '(time date, direccion real)')
        self.sqlite.createTable(nameTable = 'Lluvia', fields = '(time date, lluvia real)')

    def isLoading(self, loading):
        if loading:
            self.loading.start()
        else:
            self.loading.stop()

    def getData(self, index):
        data = [self.envService.data[0], self.envService.data[1], self.irradService.data, self.speedService.data, self.directionService.data, self.rainService.data]
        return data[index]

    def getTime(self, index):
        timeData = [self.envService.time, self.envService.time, self.irradService.time, self.speedService.time, self.directionService.time, self.rainService.time]
        return timeData[index]

    def readAndUpdate(self):
        self.env(False)
        self.irrad(False)
        self.windSpeed(False)
        self.windDirection(False)
        self.rain(False)
        # Actualizar grafica
        self.signals.signalUpdateGraph.emit()

    def env(self, send = True):
        # Leer datos
        humidity, temperature = estacion.getHumidityAndTemperature()
        humidityR = round(humidity,1)
        temperatureR = round(temperature,1)
        currentTime = datetime.now()
        if (humidity != 0 and temperature !=0):
            self.envService.updateUi([temperatureR, humidityR], currentTime)
            if send:
                self.envService.send([temperatureR, humidityR], currentTime)

    def irrad(self, send = True):
        irradiance = round(estacion.getRadiation(),1)
        currentTime = datetime.now()
        self.irradService.updateUi(irradiance, currentTime)
        if send:
            self.irradService.send(irradiance, currentTime)

    def windSpeed(self, send = True):
        speed = round(estacion.getVelocity())
        currentTime = datetime.now()
        self.speedService.updateUi(speed, currentTime)
        if send:
            self.speedService.send(speed, currentTime)

    def windDirection(self, send = True):
        direction = round(estacion.getDirection())
        currentTime = datetime.now()
        self.directionService.updateUi(direction, currentTime)
        if send:
            self.directionService.send(direction, currentTime)

    def rain(self, send = True):
        rain = round(estacion.getPrecipitation(),1)
        currentTime = datetime.now()
        self.rainService.updateUi(rain, currentTime)
        if send:
            self.rainService.send(rain, currentTime)

class DataService:
    def __init__(self, sqlite, nameTable, namesDB, name, text, numData, units,numVarSensor = 1):
        self.sqlite = sqlite
        self.namesDB = nameTable + namesDB
        self.name = name
        self.text = text
        self.numData = numData
        self.numVarSensor = numVarSensor
        self.units = units
        self.signals = Signals()

        # Mqqt
        self.client = Mqtt()

        if self.numVarSensor > 1:
            self.data = [[] for i in range(self.numVarSensor)]
        else:
            self.data = []
        self.time = []

    def send(self, data, timeData):
        timeString = timeData.strftime("%Y-%m-%d %H:%M:%S")
        if self.numVarSensor > 1:
            for i in range(self.numVarSensor):
                # Enviar datos al servidor
                self.client.publish(self.name[i],data[i],timeData)
            datos = [timeString]
            datos.extend(data)
            self.sqlite.insert(datos, names = self.namesDB)
        else:
            # Enviar datos al servidor
            self.client.publish(self.name, data, timeData)
            self.sqlite.insert((timeString, data), names = self.namesDB)

    def updateUi(self, data, timeData):
        self.time.append(timeData)
        if len(self.time) > self.numData:
            self.time.pop(0)

        if self.numVarSensor > 1:
            for i in range(self.numVarSensor):
                self.data[i].append(data[i])
                if len(self.data[i]) > self.numData:
                    self.data[i].pop(0)
                self.text[i].setText( str(data[i]) +" "+ self.units[i])
        else:
            self.data.append(data)
            if len(self.data) > self.numData:
                self.data.pop(0)
            self.text.setText( str(data) +" "+ self.units)

@singleton
class Mqtt:
    def __init__(self):
        self.prefs = LocalStorage(route=rutaPrefsUser, name = 'prefs')
        self.client = mqtt.Client(client_id=str(uuid.getnode()), clean_session=True, userdata=None, transport="tcp")
        self.isPending = True

        self.sqlite = SQLite(nameDB = routeDatos + '/temporal' )
        self.nameTable = 'pending'
        fields = '(id integer PRIMARY KEY, name text, value real, time date)'
        self.names = self.nameTable + '(name, value, time)  VALUES(?, ?, ?)'
        self.sqlite.createTable(nameTable = self.nameTable, fields = fields)

        self.signals = Signals()
        try:
            self.brokerAddress = self.prefs.read()['server']
        except:
            logging.error('No se encontró server en prefs.json')
            self.brokerAddress = '192.168.1.5'
        try:
            self.port = self.prefs.read()['port']
        except:
            logging.error('No se encontró puerto en prefs.json')
            self.port = 1883
        try:
            self.user = self.prefs.read()['user']
        except:
            logging.error('No se encontró usuario mqqt en prefs.json')
            self.user = 'user'
        try:
            self.password = self.prefs.read()['password']
        except:
            logging.error('No se encontró contraseña mqqt en prefs.json')
            self.password = '12345'
        try:
            self.topics = self.prefs.read()["topics"]
        except:
            logging.error("Topics no encontrados")
            self.topics = {"tempEnv":"topic1","humEnv":"topic2","irrad":"topic3","speed":"topic4","direction":"topic5","rain":"topic6"}

        self.client.on_connect = self.onConnect
        self.client.on_disconnect = self.onDisconnect

        # Conectar en segundo plano
        self.thread = Thread(target = self.connect)
        self.thread.start()

    def onConnect(self, client, userdata, flags, rc):
        if rc == 0:
            self.signals.signalMessages.emit('En línea')
        else:
            self.signals.signalMessages.emit('Desconectado')

        self.signals.signalIsLoanding.emit(False)

    def onDisconnect(self, client, userdata, rc):
        self.signals.signalMessages.emit('Desconectado')

    def connect(self):
        self.signals.signalIsLoanding.emit(True)
        self.signals.signalMessages.emit('Desconectado')
        try:
            self.client.username_pw_set(username=self.user,password=self.password)
            self.client.connect(self.brokerAddress, port=self.port, keepalive=10)
        except:
            self.signals.signalIsLoanding.emit(False)
            self.signals.signalAlert.emit('No se pudo conectar al servidor')
            logging.error('No se pudo conectar al servidor')

        self.client.loop_start()

    def publish(self, name, data, timeData):
        timestamp = int(timeData.timestamp())
        payload = json.dumps({"valor1":data,'Fecha':timestamp})
        info = self.client.publish(self.topics[name], payload)
        time.sleep(0.1)
        if info.is_published() == False:
            # logging.error('No se pudo publicar los datos en el servidor')
            self.sqlite.insert((name, data, timestamp), names = self.names)
            self.isPending = True

    def verifyPending(self):
        if self.isPending and self.client.is_connected():
            dataTemp = self.sqlite.find()
            if dataTemp:
                for item in dataTemp:
                    payload = json.dumps({"valor1":item[2], 'Fecha': item[3]})
                    info = self.client.publish(self.topics[item[1]], payload)
                    time.sleep(0.1)
                    if info.is_published():
                        self.sqlite.removeById(item[0])
            else:
                self.isPending = False

class SQLite:
    def __init__(self, nameDB):
        self.nameDB = nameDB
        self.con = self.connection(self.nameDB)
        self.cursor = self.con.cursor()

    def connection(self, nameDB):
        try:
            con = sqlite3.connect(nameDB + '.db', check_same_thread = False)
            return con

        except Error:
            logging.error(Error.message)
            print(Error.message)
    def createTable(self, nameTable, fields):
        qmutex.lock()
        self.nameTable = nameTable
        self.cursor.execute('create table if not exists ' + self.nameTable + fields)
        self.con.commit()
        qmutex.unlock()

    def insert(self, data, names):
        qmutex.lock()
        self.cursor.execute('INSERT INTO '+ names, data)
        self.con.commit()
        qmutex.unlock()

    def removeById(self, id):
        qmutex.lock()
        self.cursor.execute('DELETE FROM ' + self.nameTable + ' WHERE id=' + str(id))
        self.con.commit()
        qmutex.unlock()

    def find(self):
        qmutex.lock()
        self.cursor.execute('SELECT * FROM ' + self.nameTable + ' LIMIT 500')
        lista = self.cursor.fetchall()
        qmutex.unlock()
        return lista

class Plotter:
    def __init__(self,Figure,ax):
        self.figure = Figure
        self.axis = ax
        self.formatTime = dates.DateFormatter("%H:%M")
        self.limits = [[0,80], [0,100], [0,1200], [0,100], [0,360], [0,50]]

    def plot(self,datax,datay,title,index):
        try:
            if len(datax) <= 0 and len(datay) <= 0:
                datax = [datetime.now()]
                datay = [0]
            self.axis.cla()
            if len(datax) == len(datay):
                self.axis.plot(datax,datay, 'b-')
            self.axis.plot(datax,datay, 'b-')
            self.axis.xaxis.set_major_formatter(self.formatTime)
            self.axis.grid()
            self.axis.set_ylim(self.limits[index][0],self.limits[index][1])
            self.axis.set_title(title,fontsize = "18", fontweight='bold')
            self.axis.set_xlabel('Hora',fontsize = "14")
            self.axis.set_ylabel('x(t)',fontsize = "15")
            self.figure.figure.subplots_adjust(top = 0.85,bottom=0.21, left=0.13, right = 0.95)
            self.figure.draw()
        except:
            print('No se pudo graficar')
            logging.warning('No se pudo graficar')

class LocalStorage():
    def __init__(self, route, name):
        self.optionsServer = []
        self.routePrefs = os.path.abspath(route + "/" + name + ".json")
        self.name = name

    def read(self):
        try:
            with open(self.routePrefs) as file:
                if file.read():
                    file = open(self.routePrefs)
                    return json.load(file)
                else:
                    logging.warning('El archivo ' + self.name + '.json está vacío')
                    print('El archivo ' + self.name + '.json está vacío')
                    return False
        except:
            logging.error('No se pudo encontrar el archivo ' + self.name + '.json')
            print('No se pudo encontrar el archivo ' + self.name + '.json')
            return False

    def update(self,prefs):
        with open(self.routePrefs, 'w') as file:
            json.dump(prefs, file)

class Thread(QThread):

    def __init__(self, target):
        super().__init__()
        self.target = target

    def run(self):
        self.target()

class ThreadForever(QThread):

    def __init__(self, target, every=5):
        super().__init__()
        self.threadactive = True
        self.target = target
        self.every = every

    def run(self):
        while self.threadactive:
            self.target()
            time.sleep(self.every)

    def stop(self):
        self.threadactive = False

@singleton
class Signals(QObject):
    signalUpdatePrefs = pyqtSignal()
    signalUpdateInputValue = pyqtSignal(float)
    signalUpdateGraph = pyqtSignal()
    signalIsLoanding = pyqtSignal(bool)
    signalAlert = pyqtSignal(str)
    signalMessages = pyqtSignal(str)
