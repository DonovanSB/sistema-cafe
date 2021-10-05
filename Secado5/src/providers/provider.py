import os
import json
import random
import logging
import time
import sqlite3
from sqlite3 import Error
from datetime import datetime
import uuid
import matplotlib.dates as dates
from PyQt5.QtCore import pyqtSignal, QObject, QThread, QMutex, QDateTime
import paho.mqtt.client as mqtt

rutaPrefsUser = os.path.dirname(os.path.abspath(__file__))

parent = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir)
root = os.path.abspath(parent)
routeDatos = root + '/datos'

logging.basicConfig(filename = root + '/secado.log', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

qmutex = QMutex()

def singleton(cls):
    instance = [None]
    def wrapper(*args, **kwargs):
        if instance[0] is None:
            instance[0] = cls(*args, **kwargs)
        return instance[0]

    return wrapper

class Data:
    def __init__(self,
                 loading,
                 textTempEnv,
                 textHumEnv,
                 textTemp1,
                 textHum1,
                 textTemp2,
                 textHum2,
                 textTemp3,
                 textHum3,
                 textTemp4,
                 textHum4,
                 textTemp5,
                 textHum5,
                 textHumGrain):
        self.loading = loading
        self.textTempEnv  = textTempEnv
        self.textHumEnv   = textHumEnv
        self.textTemp1    = textTemp1
        self.textHum1     = textHum1
        self.textTemp2    = textTemp2
        self.textHum2     = textHum2
        self.textTemp3    = textTemp3
        self.textHum3     = textHum3
        self.textTemp4    = textTemp4
        self.textHum4     = textHum4
        self.textTemp5    = textTemp5
        self.textHum5     = textHum5
        self.textHumGrain = textHumGrain

        self.numData      = 8000

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
        self.signals.signalUpdateInputValue.connect(self.updateInputValue)

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
            samplingTimes = {"env":10,"env1":10,"env2":10,"env3":10,"env4":10,"env5":10}
        return samplingTimes

    def initDataService(self):
        namesEnv = '(time, temperatura, humedad)  VALUES(?, ?, ?)'
        namesHG = '(time, humedad)  VALUES(?, ?)'
        self.envService = DataService( self.sqlite, 'Ambiente', namesEnv, ['tempEnv', 'humEnv'], [self.textTempEnv, self.textHumEnv], self.numData, ["°C", "%"], 2)
        self.env1Service = DataService( self.sqlite, 'Zona1', namesEnv, ['temp1', 'hum1'], [self.textTemp1, self.textHum1], self.numData, ["°C", "%"], 2)
        self.env2Service = DataService( self.sqlite, 'Zona2', namesEnv, ['temp2', 'hum2'], [self.textTemp2, self.textHum2], self.numData, ["°C", "%"], 2)
        self.env3Service = DataService( self.sqlite, 'Zona3', namesEnv, ['temp3', 'hum3'], [self.textTemp3, self.textHum3], self.numData, ["°C", "%"], 2)
        self.env4Service = DataService( self.sqlite, 'Zona4', namesEnv, ['temp4', 'hum4'], [self.textTemp4, self.textHum4], self.numData, ["°C", "%"], 2)
        self.env5Service = DataService( self.sqlite, 'Zona5', namesEnv, ['temp5', 'hum5'], [self.textTemp5, self.textHum5], self.numData, ["°C", "%"], 2)
        self.humGrainService = DataService( self.sqlite, 'HGrano', namesHG, 'humGrano', self.textHumGrain, self.numData, "%")

    def initSQLite(self, route):
        self.sqlite = SQLite(nameDB = route)
        fieldsEnv = '(time date, temperatura real, humedad real)'
        fieldsHG = '(time date, humedad real)'
        self.sqlite.createTable(nameTable = 'Ambiente', fields = fieldsEnv)
        self.sqlite.createTable(nameTable = 'Zona1', fields = fieldsEnv)
        self.sqlite.createTable(nameTable = 'Zona2', fields = fieldsEnv)
        self.sqlite.createTable(nameTable = 'Zona3', fields = fieldsEnv)
        self.sqlite.createTable(nameTable = 'Zona4', fields = fieldsEnv)
        self.sqlite.createTable(nameTable = 'Zona5', fields = fieldsEnv)
        self.sqlite.createTable(nameTable = 'HGrano', fields = fieldsHG)

    def isLoading(self, loading):
        if loading:
            self.loading.start()
        else:
            self.loading.stop()

    def updateInputValue(self,hum):
        currentTime = datetime.now()
        self.humGrainService.updateUi(hum, currentTime)
        self.humGrainService.send(hum, currentTime)

    def getData(self, index):
        datos= [self.envService.data[0],
                self.envService.data[1],
                self.env1Service.data[0],
                self.env1Service.data[1],
                self.env2Service.data[0],
                self.env2Service.data[1],
                self.env3Service.data[0],
                self.env3Service.data[1],
                self.env4Service.data[0],
                self.env4Service.data[1],
                self.env5Service.data[0],
                self.env5Service.data[1],
                self.humGrainService.data]
        return datos[index]

    def getTime(self, index):
        timesList = [self.envService.time,
                     self.envService.time,
                     self.env1Service.time,
                     self.env1Service.time,
                     self.env2Service.time,
                     self.env2Service.time,
                     self.env3Service.time,
                     self.env3Service.time,
                     self.env4Service.time,
                     self.env4Service.time,
                     self.env5Service.time,
                     self.env5Service.time,
                     self.humGrainService.time]
        return timesList[index]

    def readAndUpdate(self):
        self.env(False)
        self.env1(False)
        self.env2(False)
        self.env3(False)
        self.env4(False)
        self.env5(False)
        # Actualizar grafica
        self.signals.signalUpdateGraph.emit()

    def env(self, send = True):
        temperatureEnv = random.randint(18, 25)
        humidityEnv = random.randint(50, 60)
        currentTime = datetime.now()
        self.envService.updateUi([temperatureEnv, humidityEnv], currentTime)
        if send:
            self.envService.send([temperatureEnv, humidityEnv], currentTime)

    def env1(self, send = True):
        temperature1 = random.randint(18, 25)
        humidity1 = random.randint(50, 60)
        currentTime = datetime.now()
        self.env1Service.updateUi([temperature1, humidity1], currentTime)
        if send:
            self.env1Service.send([temperature1, humidity1], currentTime)

    def env2(self, send = True):
        temperature2 = random.randint(18, 25)
        humidity2 = random.randint(50, 60)
        currentTime = datetime.now()
        self.env2Service.updateUi([temperature2, humidity2], currentTime)
        if send:
            self.env2Service.send([temperature2, humidity2], currentTime)

    def env3(self, send = True):
        temperature3 = random.randint(18, 25)
        humidity3 = random.randint(50, 60)
        currentTime = datetime.now()
        self.env3Service.updateUi([temperature3, humidity3], currentTime)
        if send:
            self.env3Service.send([temperature3, humidity3], currentTime)

    def env4(self, send = True):
        temperature4 = random.randint(18, 25)
        humidity4 = random.randint(50, 60)
        currentTime = datetime.now()
        self.env4Service.updateUi([temperature4, humidity4], currentTime)
        if send:
            self.env4Service.send([temperature4, humidity4], currentTime)

    def env5(self, send = True):
        temperature5 = random.randint(18, 25)
        humidity5 = random.randint(50, 60)
        currentTime = datetime.now()
        self.env5Service.updateUi([temperature5, humidity5], currentTime)
        if send:
            self.env5Service.send([temperature5, humidity5], currentTime)

class DataService:
    def __init__(self, sqlite, nameTable, namesDB, name, text, numData, units,numVarSensor = 1):
        self.prefs = LocalStorage(route=rutaPrefsUser, name = 'prefs')
        self.table = nameTable
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

        self.prefsMap = self.prefs.read()
        if self.prefsMap.__contains__("storageLimits"):
            self.dataLimit = self.prefsMap["storageLimits"]["mainData"]
        else:
            self.dataLimit = 60

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
        self.checkLimitDB(self.table, self.dataLimit)

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

    def checkLimitDB(self, table, limit):
        firstRow = self.sqlite.findFirst(table)
        if firstRow:
            dateAdded = QDateTime.fromString(firstRow[0][0], 'yyyy-MM-dd hh:mm:ss').addDays(limit)
            if QDateTime.currentDateTime() >= dateAdded:
                self.sqlite.removeByDate(table, limit)

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
        self.prefsMap = self.prefs.read()
        try:
            self.brokerAddress = self.prefsMap['server']
        except:
            logging.error('No se encontró server en prefs.json')
            self.brokerAddress = '192.168.1.5'
        try:
            self.port = self.prefsMap['port']
        except:
            logging.error('No se encontró puerto en prefs.json')
            self.port = 1883
        try:
            self.user = self.prefsMap['user']
        except:
            logging.error('No se encontró usuario mqqt en prefs.json')
            self.user = 'user'
        try:
            self.password = self.prefsMap['password']
        except:
            logging.error('No se encontró contraseña mqqt en prefs.json')
            self.password = '12345'
        try:
            self.topics = self.prefsMap["topics"]
        except:
            logging.error("Topics no encontrados")
            self.topics = {"humEnv":"topic1","tempEnv":"topic2","hum1":"topic3","temp1":"topic4","hum2":"topic5",
                      "temp2":"topic6","hum3":"topic7","temp3":"topic8","hum4":"topic9","temp4":"topic10",
                      "hum5":"topic11","temp5":"topic12","humGrano":"topic13"}

        if self.prefsMap.__contains__("storageLimits"):
            self.tempDataLimit = self.prefsMap["storageLimits"]["tempData"]
        else:
            self.tempDataLimit = 30

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
        if not info.is_published():
            # logging.error('No se pudo publicar los datos en el servidor')
            self.sqlite.insert((name, data, timestamp), names = self.names)
            self.isPending = True
            self.checkLimitDB(self.tempDataLimit)

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

    def checkLimitDB(self, limit):
        firstRow = self.sqlite.findFirst('pending')
        if firstRow:
            dateAdded = QDateTime.fromMSecsSinceEpoch(firstRow[0][3]*1000).addDays(limit)
            if QDateTime.currentDateTime() >= dateAdded:
                self.sqlite.removeByDate('pending', limit)

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

    def removeByDate(self, table, limit):
        self.cursor.execute('DELETE FROM ' + table + " WHERE time<= date('now', '-%s day')" % str(limit))
        self.con.commit()

    def findFirst(self, table):
        self.cursor.execute('SELECT * FROM ' + table + ' LIMIT 1')
        lista = self.cursor.fetchall()
        return lista


class Plotter:
    def __init__(self,Figure,ax):
        self.figure = Figure
        self.axis = ax
        self.formatTime = dates.DateFormatter("%H:%M")
        self.limits = [[0,80], [0,100], [0,80], [0,100], [0,80], [0,100], [0,80], [0,100], [0,80], [0,100], [0,80], [0,100], [0,100]]

    def plot(self,datax,datay,title,index):
        try:
            if len(datax) <= 0 and len(datay) <= 0:
                datax = [datetime.now()]
                datay = [0]
            self.axis.cla()
            if len(datax) == len(datay):
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
        self.threadactive = True
        self.target = target

    def run(self):
        self.target()

    def stop(self):
        self.threadactive = False

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
