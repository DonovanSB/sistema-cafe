#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
from openpyxl import Workbook, load_workbook
from datetime import datetime
import matplotlib.dates as dates
import os
from PyQt5.QtCore import pyqtSignal, QObject, QThread
from PyQt5.QtWidgets import QMessageBox
import json
import logging
import paho.mqtt.client as mqtt
import time
import sqlite3
from sqlite3 import Error 

rutaPrefsUser = os.path.dirname(os.path.abspath(__file__))

parent = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir)
root = os.path.abspath(parent)
routeDatos = root + '/datos'

logging.basicConfig(filename = root + '/secado.log', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def singleton(cls):    
    instance = [None]
    def wrapper(*args, **kwargs):
        if instance[0] is None:
            instance[0] = cls(*args, **kwargs)
        return instance[0]

    return wrapper

class Data:
    def __init__(self, loading, textTempEnv, textHumEnv, textTemp1, textHum1, textTemp2, textHum2, textTemp3, textHum3, textHumGrain,):
        
        self.loading = loading
        self.textTempEnv  = textTempEnv
        self.textHumEnv   = textHumEnv
        self.textTemp1    = textTemp1
        self.textHum1     = textHum1
        self.textTemp2    = textTemp2
        self.textHum2     = textHum2
        self.textTemp3    = textTemp3
        self.textHum3     = textHum3
        self.textHumGrain = textHumGrain
       
        self.numData      = 1000

        self.prefs = LocalStorage(route=rutaPrefsUser, name = 'prefs')
        try:
            self.routeData = os.path.abspath(self.prefs.read()['routeData'])
            isExist = os.path.exists(self.routeData)
            if isExist:
                self.routeData = os.path.abspath(self.routeData + '/data')
            else:
                self.routeData = routeDatos + '/data'
        except:
            logging.error('No se pudo encontrar la ruta de almacenamiento de datos en prefs.json')
            self.routeData = routeDatos + '/datos.db'
    
        # Inicializaciones para almacenamiento de datos
        self.initSQLite(self.routeData)
        self.initDataService()

        self.signals = Signals()
        self.signals.signalIsLoanding.connect(self.isLoading)
        self.signals.signalUpdatePrefs.connect(self.updatePrefs)
        self.signals.signalUpdateInputValue.connect(self.updateInputValue)

        # Mqqt
        self.client = Mqtt('secado')
        
        self.threadForever = ThreadForever(target=self.client.verifyPending)
        self.threadForever.start()
    
    def initDataService(self):
        namesEnv = '(time, temperatura, humedad)  VALUES(?, ?, ?)'
        namesHG = '(time, humedad)  VALUES(?, ?)'
        self.envService = DataService( self.sqlite, 'Ambiente', namesEnv, ['T.ambiente', 'H.ambiente'], [self.textTempEnv, self.textHumEnv], self.numData, ["°C", "%"], 2)
        self.env1Service = DataService( self.sqlite, 'Zona1', namesEnv, ['T.zona1', 'H.zona1'], [self.textTemp1, self.textHum1], self.numData, ["°C", "%"], 2)
        self.env2Service = DataService( self.sqlite, 'Zona2', namesEnv, ['T.zona2', 'H.zona2'], [self.textTemp2, self.textHum2], self.numData, ["°C", "%"], 2)
        self.env3Service = DataService( self.sqlite, 'Zona3', namesEnv, ['T.zona3', 'H.zona3'], [self.textTemp3, self.textHum3], self.numData, ["°C", "%"], 2)
        self.humGrainService = DataService( self.sqlite, 'HGrano', namesHG, 'H.grano', self.textHumGrain, self.numData, "%")

    def initSQLite(self, route):
        self.sqlite = SQLite(nameDB = route)
        fieldsEnv = '(time date, temperatura real, humedad real)'
        fieldsHG = '(time date, humedad real)'
        self.sqlite.createTable(nameTable = 'Ambiente', fields = fieldsEnv)
        self.sqlite.createTable(nameTable = 'Zona1', fields = fieldsEnv)
        self.sqlite.createTable(nameTable = 'Zona2', fields = fieldsEnv)
        self.sqlite.createTable(nameTable = 'Zona3', fields = fieldsEnv)
        self.sqlite.createTable(nameTable = 'HGrano', fields = fieldsHG)

    def isLoading(self, loading):
        if loading:
            self.loading.start()
        else:
            self.loading.stop()

    def updateInputValue(self,hum):
        currentTime = datetime.now()
        self.humGrainService.update(hum, currentTime)

    def updatePrefs(self,route):
        self.routeData = os.path.abspath(route + '/data')
        self.initSQLite(self.routeData)
        self.initDataService()
        self.thread = Thread(target = self.client.connect)
        self.thread.start()
        

    def getData(self, index):
        datos= [self.envService.data[0],self.envService.data[1],self.env1Service.data[0],self.env1Service.data[1],self.env2Service.data[0],self.env2Service.data[1],self.env3Service.data[0],self.env3Service.data[1],self.humGrainService.data]     
        return datos[index]

    def getTime(self, index):
        time = [self.envService.time, self.envService.time, self.env1Service.time, self.env1Service.time, self.env2Service.time, self.env2Service.time, self.env3Service.time, self.env3Service.time, self.humGrainService.time]
        return time[index]

    def env(self):
        temperatureEnv = random.randint(18, 25)
        humidityEnv = random.randint(50, 60)
        currentTime = datetime.now()
        self.envService.update([temperatureEnv, humidityEnv], currentTime)
    
    def env1(self):
        temperature1 = random.randint(18, 25)
        humidity1 = random.randint(50, 60)
        currentTime = datetime.now()
        self.env1Service.update([temperature1, humidity1], currentTime)
        
    def env2(self):
        temperature2 = random.randint(18, 25)
        humidity2 = random.randint(50, 60)
        currentTime = datetime.now()
        self.env2Service.update([temperature2, humidity2], currentTime)

    def env3(self):
        temperature3 = random.randint(18, 25)
        humidity3 = random.randint(50, 60)
        currentTime = datetime.now()
        self.env3Service.update([temperature3, humidity3], currentTime)
            

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
        self.client = Mqtt('secado')

        if self.numVarSensor > 1:
            self.data = [[] for i in range(self.numVarSensor)]
        else:
            self.data = []
        self.time = []
    
    def update(self, data, time):
        self.time.append(time)
        if len(self.time) > self.numData:
            self.time.pop(0)

        if self.numVarSensor > 1:
            for i in range(self.numVarSensor):
                self.data[i].append(data[i])
                if len(self.data[i]) > self.numData:
                    self.data[i].pop(0)
                self.text[i].setText( str(data[i]) +" "+ self.units[i])
                # Enviar datos al servidor
                self.client.publish(self.name[i],data[i],time)
            datos = [time]
            datos.extend(data)
            self.sqlite.insert(datos, names = self.namesDB)
        else:
            self.data.append(data)
            if len(self.data) > self.numData:
                self.data.pop(0)
            self.text.setText( str(data) +" "+ self.units)
            # Enviar datos al servidor
            self.client.publish(self.name, data, time)
            self.sqlite.insert((time, data), names = self.namesDB)
        # Actualizar grafica  
        self.signals.signalUpdateGraph.emit()

@singleton
class Mqtt:
    def __init__(self, clientID):
        self.prefs = LocalStorage(route=rutaPrefsUser, name = 'prefs')
        self.client = mqtt.Client(client_id=clientID, clean_session=True, userdata=None, transport="tcp")
        self.isPending = True
        self.isConnected = False
        
        self.sqlite = SQLite(nameDB = routeDatos + '/temporal' )
        self.nameTable = 'pending'
        fields = '(id integer PRIMARY KEY, name text, value real, time date)'
        self.names = self.nameTable + '(name, value, time)  VALUES(?, ?, ?)'
        self.sqlite.createTable(nameTable = self.nameTable, fields = fields)

        self.signals = Signals()
        try:
            self.topic = self.prefs.read()['topic']
        except:
            logging.error('No se encontró topic en prefs.json')
            self.topic = 'estacion/secado'

        # Conectar en segundo plano
        self.thread = Thread(target = self.connect)
        self.thread.start()

    def connect(self):
        self.signals.signalIsLoanding.emit(True)
        try:
            self.brokerAddress = self.prefs.read()['server']
        except:
            logging.error('No se encontró server en prefs.json')
        try:
            self.client.username_pw_set(username="usuario_publicador_1",password="123")
            self.client.connect(self.brokerAddress, port=1884)
            self.isConnected = True
        except:
            self.signals.signalAlert.emit('No se pudo conectar al servidor')
            logging.error('No se pudo conectar al servidor')
            self.isConnected = False
        
        self.signals.signalIsLoanding.emit(False)
    
    def publish(self, name, data, time):
        payload = json.dumps({name:data,'time':str(time)})
        info = self.client.publish(self.topic, payload)
        if info.is_published() == False:
            # logging.error('No se pudo publicar los datos en el servidor')
            self.sqlite.insert((name, data, time), names = self.names)
            self.isPending = True
            self.isConnected = False
        else:
            self.isConnected = True
    
    def verifyPending(self):
        if self.isPending and self.isConnected:
            dataTemp = self.sqlite.find()
            if dataTemp:
                for item in dataTemp:
                    payload = json.dumps({item[1]:item[2], 'time':str(item[3])})
                    info = self.client.publish(self.topic, payload)
                    if info.is_published():
                        self.sqlite.removeById(item[0])
                        self.isConnected = True
                    else:
                        # logging.error('No se pudo publicar los datos en el servidor')  
                        self.isConnected = False   
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
        self.nameTable = nameTable
        self.cursor.execute('create table if not exists ' + self.nameTable + fields)
        self.con.commit()

    def insert(self, data, names):
        self.cursor.execute('INSERT INTO '+ names, data)
        self.con.commit()

    def removeById(self, id):
        self.cursor.execute('DELETE FROM ' + self.nameTable + ' WHERE id=' + str(id))
        self.con.commit()

    def find(self):
        self.cursor.execute('SELECT * FROM ' + self.nameTable)
        return self.cursor.fetchall()

class Plotter:
    def __init__(self,Figure,ax):
        self.Fig = Figure
        self.ax = ax
        self.formatTime = dates.DateFormatter("%H:%M")
        self.limits = [[0,80], [0,100], [0,80], [0,100], [0,80], [0,100], [0,80], [0,100], [0,100]]

    def plot(self,datax,datay,title,index):
        if len(datax) <= 0 and len(datay) <= 0:
            datax = [datetime.now()]
            datay = [0]
        self.ax.cla()
        if len(datax) == len(datay):
            self.ax.plot(datax,datay, 'b-')
        self.ax.xaxis.set_major_formatter(self.formatTime)
        self.ax.grid()
        self.ax.set_ylim(self.limits[index][0],self.limits[index][1])
        self.ax.set_title(title,fontsize = "18", fontweight='bold')
        self.ax.set_xlabel('Hora',fontsize = "15")
        self.ax.set_ylabel('x(t)',fontsize = "15")
        self.Fig.figure.subplots_adjust(top = 0.85,bottom=0.2, left=0.1, right = 0.95)
        self.Fig.draw()
            
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
        super(Thread,self).__init__()
        self.threadactive = True
        self.target = target

    def run(self):
        self.target()
    
    def stop(self):
        self.threadactive = False

class ThreadForever(QThread):

    def __init__(self, target, every=5):
        super(ThreadForever,self).__init__()
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
    signalUpdatePrefs = pyqtSignal(str)
    signalUpdateInputValue = pyqtSignal(float)
    signalUpdateGraph = pyqtSignal()
    signalIsLoanding = pyqtSignal(bool)
    signalAlert = pyqtSignal(str)

    statusFile = True
    dataPending = False
