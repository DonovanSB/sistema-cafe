#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
from datetime import datetime
import matplotlib.dates as dates
import xlwt
import os
from PyQt5.QtCore import pyqtSignal, QObject
import json

route = os.path.dirname(os.getcwd()) + "/Estacion Cafe Fermentacion"
rutaData = route + "/datos"
rutaPrefsUser =route + "/src/providers"

class Data:
    def __init__(self,textTempR,textHumR,textTemp1,textTemp2,textTemp3,textBrix,textPh):
        
        self.textTempR = textTempR
        self.textHumR  = textHumR
        self.textTemp1 = textTemp1
        self.textTemp2 = textTemp2
        self.textTemp3 = textTemp3
        self.textBrix  = textBrix
        self.textPh    = textPh

        self.tempRData = []
        self.humRData  = []
        self.temp1Data = []
        self.temp2Data = []
        self.temp3Data = []
        self.brixData  = []
        self.phData    = []
        self.timeData  = []
        self.numData   = 1000

        self.brix = 50
        self.ph = 7

        self.prefs = LocalStorage()
        self.prefs.beginPrefs(route=rutaPrefsUser)
        prefs = self.prefs.readPrefs()
        if prefs:
            self.prefs.beginXlsx(name="datos",route=prefs["routeData"])
        else:
            print("provider Data: No se encontró ruta en prefs")

        self.signals = Signals()
        self.signals.signalUpdateStorageRoute.connect(self.updateStorgeRoute)
        self.signals.signalUpdateInputValue.connect(self.updateInputValue)
    
    def updateInputValue(self,name,value):
        if name == "Brix":
            self.brix = value
            self.textBrix.setText(str(self.brix) + " Bx")
        if name == "PH":
            self.ph = value
            self.textPh.setText(str(self.ph))

    def updateStorgeRoute(self,route):
        self.prefs.beginXlsx(name="datos",route=route)

    def readData(self):

        self.temperatureR = random.randint(18, 25)
        self.humidityR = random.randint(50, 60)
        self.temperature1 = random.randint(18, 25)
        self.temperature2 = random.randint(18, 25)
        self.temperature3 = random.randint(18, 25)
        self.time = datetime.now()

        # ---Almacenar Datos---
        self.tempRData.append(self.temperatureR)
        self.humRData.append(self.humidityR)
        self.temp1Data.append(self.temperature1)
        self.temp2Data.append(self.temperature2)
        self.temp3Data.append(self.temperature3)
        self.brixData.append(self.brix)
        self.phData.append(self.ph)
        self.timeData.append(self.time)

        
        if len(self.tempRData) > self.numData:
            self.tempRData.pop(0)
        
        if len(self.humRData) > self.numData:
            self.humRData.pop(0)
        
        if len(self.temp1Data) > self.numData:
            self.temp1Data.pop(0)
        
        if len(self.temp2Data) > self.numData:
            self.temp2Data.pop(0)

        if len(self.temp3Data) > self.numData:
            self.temp3Data.pop(0)
        
        if len(self.brixData) > self.numData:
            self.brixData.pop(0)

        if len(self.phData) > self.numData:
            self.phData.pop(0)
            
        if len(self.timeData) > self.numData:
            self.timeData.pop(0)
        
        self.datos = [self.tempRData,self.humRData,self.temp1Data,self.temp2Data,self.temp3Data,self.brixData,self.phData]
        
        self.updateData()

    def updateData(self):
        
        self.textTempR.setText( str(self.temperatureR) + " °C")
        self.textHumR.setText( str(self.humidityR) + " %")
        self.textTemp1.setText( str(self.temperature1) + " °C")
        self.textTemp2.setText( str(self.temperature2) + " °C")
        self.textTemp3.setText( str(self.temperature3) + " °C")

        data = [self.time,self.temperatureR,self.humidityR,self.temperature1,self.temperature2,self.temperature3,self.brix,self.ph]
        style = ["time","number","number","number","number","number","number","number"]
        try:
            self.prefs.saveXlsx(data,style)
        except:
            print("provider updateData: Ingrese un ruta correcta para almacenar los datos")
            

class Plotter:
    def __init__(self,Figure,ax):
        self.Fig = Figure
        self.ax = ax
        self.formatTime = dates.DateFormatter("%H:%M")
        self.limits = [[0,80], [0,100], [0,80], [0,80], [0,80], [0,85], [0,14]]

    def plot(self,datax,datay,title,index):
        self.ax.cla()
        self.ax.plot(datax,datay, 'b-')
        self.ax.xaxis.set_major_formatter(self.formatTime)
        self.ax.grid()
        self.ax.set_ylim(self.limits[index][0],self.limits[index][1])
        self.ax.set_title(title,fontsize = "18", fontweight='bold')
        self.ax.set_xlabel('Hora',fontsize = "15")
        self.ax.set_ylabel('x(t)',fontsize = "15")
        self.Fig.figure.subplots_adjust(top = 0.8,bottom=0.27, left=0.15)
        self.Fig.draw()

class LocalStorage():
    def __init__(self):
        self.optionsServer = []
    
    def beginPrefs(self,route):
        self.routePrefs = route + "/"
    
    def beginXlsx(self,name,route):
        self.nameXlsx = name
        self.routeXlsx = route + "/"
        self.wb = xlwt.Workbook()
        self.ws = self.wb.add_sheet('Sensores')
        self.styleTime = xlwt.easyxf('',num_format_str='D/M/YY h:mm:s')
        self.styleTitles = xlwt.easyxf('font: name Times New Roman, bold on')
        self.ws.write(0, 0, 'Fecha', self.styleTitles)
        self.ws.write(0, 1, 'Temperatura Ambiente', self.styleTitles)
        self.ws.write(0, 2, 'Humedad Ambiente', self.styleTitles)
        self.ws.write(0, 3, 'Temperatura 1', self.styleTitles)
        self.ws.write(0, 4, 'Temperatura 2', self.styleTitles)
        self.ws.write(0, 5, 'Temperatura 3', self.styleTitles)
        self.ws.write(0, 6, 'Brix', self.styleTitles)
        self.ws.write(0, 7, 'PH', self.styleTitles)
        self.pos = 1

    def saveXlsx(self,data,style):
        column = len(data)
        for i in range(column):
            if style[i] == "time":
                self.ws.write(self.pos, i, data[i],self.styleTime)
            if style[i] == "number":
                self.ws.write(self.pos, i, data[i])
            self.wb.save(self.routeXlsx+self.nameXlsx + ".xls")
        self.pos += 1
    
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
    signalUpdateInputValue = pyqtSignal(str,float)
