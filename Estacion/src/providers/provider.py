#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
from datetime import datetime
import matplotlib.dates as dates
import xlwt
import os
from PyQt5.QtCore import pyqtSignal, QObject
import json

rutaPrefsUser = os.path.dirname(os.path.abspath(__file__))

class Data:
    def __init__(self,textTemp,textHum,textIrrad,textVel,textDir,textLluvia):
        self.textTemp = textTemp
        self.textHum = textHum
        self.textIrrad = textIrrad
        self.textVel = textVel
        self.textDir = textDir
        self.textLluvia = textLluvia

        self.tempData = []
        self.humData = []
        self.irradData = []
        self.speedData = []
        self.directionData = []
        self.rainData = []
        self.timeData = []
        self.numData = 1000

        self.prefs = LocalStorage()
        self.prefs.beginPrefs(route=rutaPrefsUser)
        prefs = self.prefs.readPrefs()
        if prefs:
            self.prefs.beginXlsx(name="datos",route=prefs["routeData"])
        else:
            print("provider Data: No se encontró ruta en prefs")

        self.signals = Signals()
        self.signals.signalUpdateStorageRoute.connect(self.updateStorgeRoute)
    
    def updateStorgeRoute(self,route):
        self.prefs.beginXlsx(name="datos",route=route)

    def readData(self):

        self.temperature = random.randint(18, 25)
        self.humidity = random.randint(50, 60)
        self.irrad = random.randint(200, 300)
        self.speed = random.randint(5, 10)
        self.direction = random.randint(0, 360)
        self.rain = random.randint(0, 5)
        self.time = datetime.now()

        # ---Almacenar Datos---
        self.tempData.append(self.temperature)
        self.humData.append(self.humidity)
        self.irradData.append(self.irrad)
        self.speedData.append(self.speed)
        self.directionData.append(self.direction)
        self.rainData.append(self.rain)
        self.timeData.append(self.time)

        if len(self.tempData) > self.numData:
            self.tempData.pop(0)
        
        if len(self.humData) > self.numData:
            self.humData.pop(0)
        
        if len(self.irradData) > self.numData:
            self.irradData.pop(0)
        
        if len(self.speedData) > self.numData:
            self.speedData.pop(0)
        
        if len(self.directionData) > self.numData:
            self.directionData.pop(0)

        if len(self.rainData) > self.numData:
            self.rainData.pop(0)
            
        if len(self.timeData) > self.numData:
            self.timeData.pop(0)

        self.datos = [self.tempData, self.humData, self.irradData, self.speedData, self.directionData, self.rainData]
        
        self.updateData()

    def updateData(self):
        self.textTemp.setText( str(self.temperature) + " °C")
        self.textHum.setText( str(self.humidity) + " %")
        self.textIrrad.setText( str(self.irrad) + " W/m²")
        self.textVel.setText( str(self.speed) + " km/h")
        self.textDir.setText( str(self.direction) + " °")
        self.textLluvia.setText( str(self.rain) + " cm/h")
        
        data = [self.time,self.temperature,self.humidity,self.irrad,self.speed,self.direction,self.rain]
        style = ["time","number","number","number","number","number","number"]
        try:
            self.prefs.saveXlsx(data,style)
        except:
            print("provider updateData: Ingrese un ruta correcta para almacenar los datos")
            

class Plotter:
    def __init__(self,Figure,ax):
        self.Fig = Figure
        self.ax = ax
        self.formatTime = dates.DateFormatter("%H:%M")
        self.limits = [[0,80], [0,100], [0,1200], [0,100], [0,360], [0,50]]

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
        self.ws.write(0, 1, 'Temperatura', self.styleTitles)
        self.ws.write(0, 2, 'Humedad', self.styleTitles)
        self.ws.write(0, 3, 'Irradiancia', self.styleTitles)
        self.ws.write(0, 4, 'Velocidad', self.styleTitles)
        self.ws.write(0, 5, 'Direccion', self.styleTitles)
        self.ws.write(0, 6, 'Lluvia', self.styleTitles)
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
