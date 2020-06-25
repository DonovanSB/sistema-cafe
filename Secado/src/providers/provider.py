#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
from openpyxl import Workbook, load_workbook
from datetime import datetime
import matplotlib.dates as dates
import os
from PyQt5.QtCore import pyqtSignal, QObject
import json

rutaPrefsUser = os.path.dirname(os.path.abspath(__file__))
statusFile = True

class Data:
    def __init__(self, textTempEnv, textHumEnv, textTemp1, textHum1, textTemp2, textHum2, textTemp3, textHum3, textHumGrain,):
        
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
        self.corruptedFile = False

        self.prefs = LocalStorage()
        self.prefs.beginPrefs(route=rutaPrefsUser)
        self.routeData = self.prefs.readPrefs()['routeData']

        # Inicializaciones para almacenamiento de datos
        self.wb = WBook(self.routeData).workbook
        self.initExcel(self.routeData)
        self.initDataService()

        self.signals = Signals()
        self.signals.signalUpdateStorageRoute.connect(self.updateStorgeRoute)
        self.signals.signalUpdateInputValue.connect(self.updateInputValue)
    
    def initDataService(self):
        self.envService = DataService( [self.textTempEnv, self.textHumEnv], self.envExcel, self.numData, ["°C", "%"], 2)
        self.env1Service = DataService( [self.textTemp1, self.textHum1], self.env1Excel, self.numData, ["°C", "%"], 2)
        self.env2Service = DataService( [self.textTemp2, self.textHum2], self.env2Excel, self.numData, ["°C", "%"], 2)
        self.env3Service = DataService( [self.textTemp3, self.textHum3], self.env3Excel, self.numData, ["°C", "%"], 2)
        self.humGrainService = DataService( self.textHumGrain, self.humGrainExcel, self.numData, "%")

    def initExcel(self, route):
        self.envExcel = Excel(wb = self.wb, titleSheet='Ambiente', head = ['Tiempo', 'Temperatura', 'Humedad'], route = route, initial = True)
        self.env1Excel = Excel(wb = self.wb, titleSheet='Zona 1', head = ['Tiempo', 'Temperatura', 'Humedad'], route = route)
        self.env2Excel = Excel(wb = self.wb, titleSheet='Zona 2', head = ['Tiempo', 'Temperatura', 'Humedad'], route = route)
        self.env3Excel = Excel(wb = self.wb, titleSheet='Zona 3', head = ['Tiempo', 'Temperatura', 'Humedad'], route = route)
        self.humGrainExcel = Excel(wb = self.wb, titleSheet='Humedad Grano', head = ['Tiempo', 'Humedad Grano'], route = route)

    def updateInputValue(self,hum):
        currentTime = datetime.now()
        self.humGrainService.update(hum, currentTime)

    def updateStorgeRoute(self,route):
        self.routeData = route
        self.wb = WBook(route).workbook
        self.initExcel(route)
        self.initDataService()

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
    
    def save(self):
        try:
            self.wb.save(self.routeData + '/datos.xlsx')
        except:
            print("provider save: Ingrese un ruta correcta para almacenar los datos")
        statusFile = True

class DataService:
    def __init__(self, text, excel, numData, units,numVarSensor = 1):
        self.text = text
        self.excel = excel
        self.numData = numData
        self.numVarSensor = numVarSensor
        self.units = units
        self.signals = Signals()

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
            datos = [time]
            datos.extend(data)
            self.excel.addRow(datos)
        else:
            self.data.append(data)
            if len(self.data) > self.numData:
                self.data.pop(0)
            self.text.setText( str(data) +" "+ self.units)
            self.excel.addRow([time, data])

        # Actualizar grafica  
        self.signals.signalUpdateGraph.emit()

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

class WBook:
    def __init__(self, route):
        fileExists = os.path.isfile(route + '/datos.xlsx')
        if fileExists:
            try:
                self.workbook = load_workbook(filename= route + '/datos.xlsx')
            except:
                print('Archivo dañado')
                statusFile = False
                self.workbook = Workbook()
        else:
            self.workbook = Workbook()

class Excel:
    def __init__(self, wb, titleSheet, head, route, initial = False):
        fileExists = os.path.isfile(route + '/datos.xlsx')
        self.route = route + '/'
        self.workbook = wb

        if fileExists and statusFile:
            self.sheet = self.workbook.get_sheet_by_name(titleSheet)
        else:
            if initial:
                self.sheet = self.workbook.active
                self.sheet.title = titleSheet
            else:
                self.sheet = self.workbook.create_sheet(title=titleSheet)  
            self.sheet.append(head)
        # print(len(tuple(self.sheet.rows)))
        # print(self.sheet.cell(row=3, column=1).value)

    def addRow(self, data):
        self.sheet.append(data)
            
class LocalStorage():
    def __init__(self):
        self.optionsServer = []
    
    def beginPrefs(self,route):
        self.routePrefs = route + "/"
    
    def readPrefs(self):
        try:
            with open(self.routePrefs + 'prefs.json') as file:
                if file.read():
                    file = open(self.routePrefs + 'prefs.json')
                    return json.load(file)
                else:
                    print('No se encontraron las preferencias del usuario')
                    return False
        except:
            print('No se pudo encontrar el archivo de prefs.json')
            return False

    def updatePrefs(self,prefs):
        with open(self.routePrefs + 'prefs.json', 'w') as file:
            json.dump(prefs, file)

def singleton(cls):    
    instance = [None]
    def wrapper(*args, **kwargs):
        if instance[0] is None:
            instance[0] = cls(*args, **kwargs)
        return instance[0]

    return wrapper
@singleton
class Signals(QObject):
    signalServerUpdate = pyqtSignal(bool)
    signalUpdateStorageRoute = pyqtSignal(str)
    signalUpdateInputValue = pyqtSignal(float)
    signalUpdateGraph = pyqtSignal()
