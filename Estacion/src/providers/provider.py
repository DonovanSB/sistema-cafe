#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
from datetime import datetime
import matplotlib.dates as dates
from openpyxl import Workbook, load_workbook
import os
from PyQt5.QtCore import pyqtSignal, QObject
import json
import logging

rutaPrefsUser = os.path.dirname(os.path.abspath(__file__))

parent = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir)
route = os.path.abspath(parent)
logging.basicConfig(filename = route + '/estacion.log', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

class Data:
    def __init__(self,textTemp,textHum,textIrrad,textSpeed,textDir,textRain):
        self.textTemp = textTemp
        self.textHum = textHum
        self.textIrrad = textIrrad
        self.textSpeed = textSpeed
        self.textDir = textDir
        self.textRain = textRain

        self.numData = 1000

        self.prefs = LocalStorage()
        self.prefs.beginPrefs(route=rutaPrefsUser)
        self.routeData = os.path.abspath(self.prefs.readPrefs()['routeData'] + '/datos.xlsx')
        
        # Inicializaciones para almacenamiento de datos
        self.wb = WBook(self.routeData).workbook
        self.initExcel(self.routeData)
        self.initDataService()

        self.signals = Signals()
        self.signals.signalUpdateStorageRoute.connect(self.updateStorgeRoute)
    
    def initDataService(self):
        self.envService = DataService( [self.textTemp, self.textHum], self.envExcel, self.numData, ["°C", "%"], 2)
        self.irradService = DataService( self.textIrrad, self.irradExcel, self.numData, "W/m²")
        self.speedService = DataService( self.textSpeed, self.speedExcel, self.numData, "km/h")
        self.directionService = DataService( self.textDir, self.directionExcel, self.numData, "°")
        self.rainService = DataService( self.textRain, self.rainExcel, self.numData, "cm/h")

    def initExcel(self, route):
        self.envExcel = Excel(wb = self.wb, titleSheet='Ambiente', head = ['Tiempo', 'Temperatura', 'Humedad'], route = route, initial = True)
        self.irradExcel = Excel(wb = self.wb, titleSheet='Irradiancia', head = ['Tiempo', 'Irradiancia'], route = route)
        self.speedExcel = Excel(wb = self.wb, titleSheet='Velocidad V', head = ['Tiempo', 'Velocidad'], route = route)
        self.directionExcel = Excel(wb = self.wb, titleSheet='Direccion V', head = ['Tiempo', 'Direccion'], route = route)
        self.rainExcel = Excel(wb = self.wb, titleSheet='Lluvia', head = ['Tiempo', 'Lluvia'], route = route)

    def updateStorgeRoute(self,route):
        self.routeData = os.path.abspath(route + '/datos.xlsx')
        self.wb = WBook(self.routeData).workbook
        self.initExcel(self.routeData)
        self.initDataService()
    
    def getData(self, index):
        data = [self.envService.data[0], self.envService.data[1], self.irradService.data, self.speedService.data, self.directionService.data, self.rainService.data]
        return data[index]

    def getTime(self, index):
        time = [self.envService.time, self.envService.time, self.irradService.time, self.speedService.time, self.directionService.time, self.rainService.time]
        return time[index]

    def env(self):
        # Leer datos
        temperatureR = random.randint(18, 25)
        humidityR = random.randint(50, 60)
        currentTime = datetime.now()
        self.envService.update([temperatureR, humidityR], currentTime)
    
    def irrad(self):
        irradiance = random.randint(200, 300)
        currentTime = datetime.now()
        self.irradService.update(irradiance, currentTime)

    def windSpeed(self):
        speed = random.randint(5, 10)
        currentTime = datetime.now()
        self.speedService.update(speed, currentTime)

    def windDirection(self):
        direction = random.randint(0, 360)
        currentTime = datetime.now()
        self.directionService.update(direction, currentTime)

    def rain(self):
        rain = random.randint(0, 5)
        currentTime = datetime.now()
        self.rainService.update(rain, currentTime)

    def save(self):
        try:
            self.wb.save(self.routeData)
        except:
            logging.error('Ingrese un ruta correcta para almacenar los datos')
            print("provider save: Ingrese un ruta correcta para almacenar los datos")
        
        self.signals.statusFile = True

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
        self.limits = [[0,80], [0,100], [0,1200], [0,100], [0,360], [0,50]]

    def plot(self,datax,datay,title,index):
        if len(datax) <= 0 and len(datay) <= 0:
            datax = [datetime.now()]
            datay = [0]
        self.ax.cla()
        if len(datax) == len(datay):
            self.ax.plot(datax,datay, 'b-')
        self.ax.plot(datax,datay, 'b-')
        self.ax.xaxis.set_major_formatter(self.formatTime)
        self.ax.grid()
        self.ax.set_ylim(self.limits[index][0],self.limits[index][1])
        self.ax.set_title(title,fontsize = "18", fontweight='bold')
        self.ax.set_xlabel('Hora',fontsize = "15")
        self.ax.set_ylabel('x(t)',fontsize = "15")
        self.Fig.figure.subplots_adjust(top = 0.85,bottom=0.2, left=0.13, right = 0.95)
        self.Fig.draw()

class WBook:
    def __init__(self, route):

        signals = Signals()

        fileExists = os.path.isfile(route)
        if fileExists:
            try:
                self.workbook = load_workbook(filename= route)
            except:
                logging.error('Archivo de respaldo de datos dañado')
                print('Archivo de respaldo de datos dañado')
                signals.statusFile = False
                self.workbook = Workbook()
        else:
            self.workbook = Workbook()

class Excel:
    def __init__(self, wb, titleSheet, head, route, initial = False):

        signals = Signals()

        fileExists = os.path.isfile(route)
        self.workbook = wb

        if fileExists and signals.statusFile:
            self.sheet = self.workbook.get_sheet_by_name(titleSheet)
        else:
            if initial:
                self.sheet = self.workbook.active
                self.sheet.title = titleSheet
            else:
                self.sheet = self.workbook.create_sheet(title=titleSheet)  
            self.sheet.append(head)

    def addRow(self, data):
        self.sheet.append(data)

class LocalStorage():
    def __init__(self):
        self.optionsServer = []
    
    def beginPrefs(self,route):
        self.routePrefs = os.path.abspath(route + "/prefs.json")

    def readPrefs(self):
        try:
            with open(self.routePrefs) as file:
                if file.read():
                    file = open(self.routePrefs)
                    return json.load(file)
                else:
                    logging.error('No se encontraron las preferencias del usuario')
                    print('No se encontraron las preferencias del usuario')
                    return False
        except:
            logging.error('No se pudo encontrar el archivo de prefs.json')
            print('No se pudo encontrar el archivo de prefs.json')
            return False

    def updatePrefs(self,prefs):
        with open(self.routePrefs, 'w') as file:
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
    signalUpdateGraph = pyqtSignal()

    statusFile = True
