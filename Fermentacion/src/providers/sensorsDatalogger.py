import time
import os
import json

providersPath = os.path.dirname(os.path.abspath(__file__))

# =====================================
# Configuracion AM2301 (DHT22)
# =====================================
import Adafruit_DHT
dht = Adafruit_DHT.DHT22

# =====================================
# Configuracion DS18B20
# =====================================
from ds18b20 import DS18B20
tempSensor = DS18B20()

# =====================================
# Clase para leer archivos json
# =====================================
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
                    print('No se encontraron los ids de los sensores de temperatura')
                    return False
        except:
            print('No se pudo encontrar el archivo ' + self.name + '.json')
            return False

    def update(self, prefs):
        with open(self.routePrefs, 'w') as file:
            json.dump(prefs, file)
# =====================================
# Clase de conectores DHT
# =====================================
class DHTConnector:
	def __init__(self, _connector, _typeSensor, _deviceId = '0'):
		if _typeSensor == 'DS18B20' and _deviceId != '0':
			self.pin = getPinSensor('DHT1')
			self.typeSensor = _typeSensor
			self.deviceId = getRegisteredId(_deviceId)
			self.error = False
		elif _typeSensor == 'AM2301':
			self.pin = getPinSensor(_connector)
			self.typeSensor = _typeSensor
			self.deviceId = _deviceId
			self.error = False
		else:
			self.error = True
			print('Error al configurar DHT connector')
		
	def getTemperature(self):
		if self.error == False:
			hum, temp = getValueDHTConnector(self.pin, self.typeSensor, self.deviceId)
			return temp
		else: 
			print('Error al configurar DHT connector')
	
	def getHumidity(self):
		if self.error == False:
			hum, temp = getValueDHTConnector(self.pin, self.typeSensor, self.deviceId)
			return hum
		else: 
			print('Error al configurar DHT connector')
		
	def getHumidityAndTemperature(self):
		if self.error == False:
			hum = 100
			while hum >= 100:
				hum, temp = getValueDHTConnector(self.pin, self.typeSensor, self.deviceId)
			return min(max(hum,0),100), min(max(temp,0),100)
		else: 
			print('Error al configurar DHT connector')
		
			
# =====================================
# Funcion para obtener el pin
# =====================================
def getPinSensor(connector):
	if connector == 'DHT':
		return 23
	elif connector == 'DHT1':
		return 18
	elif connector == 'DHT2':
		return 24
	elif connector == 'DHT3':
		return 25
	else:
		return 999

# =====================================
# Funcion para obtener el id registrado
# =====================================
def getRegisteredId(deviceId):
	localeStorage = LocalStorage(providersPath, 'devices')
	devices =  localeStorage.read()
	if devices:
		if deviceId == '1':
			if devices.__contains__('sensor1'):
				return devices['sensor1']
			else:
				return '/sys/bus/w1/devices/28-01191f16007e/w1_slave'
		elif deviceId == '2':
			if devices.__contains__('sensor2'):
				return devices['sensor2']
			else:
				return '/sys/bus/w1/devices/28-0119126fe5aa/w1_slave'
		elif deviceId == '3':
			if devices.__contains__('sensor3'):
				return devices['sensor3']
			else:
				return '/sys/bus/w1/devices/28-01191254f3e8/w1_slave'
		elif deviceId == '4':
			if devices.__contains__('sensor4'):
				return devices['sensor4']
			else:
				return '/sys/bus/w1/devices/28-0119125c8982/w1_slave'
		else:
			return '/nada'
	else:
		return '/nada'

# =====================================
# Obtener el valor de sensores de 
# conectores DHT
# =====================================
def getValueDHTConnector(pin, typeSensor, path):
	if typeSensor == 'AM2301':
		hum, temp = readAM2301(pin)
		return hum, temp
	elif typeSensor == 'DS18B20':
		temp = readDS18B20(pin, path)
		return 0,temp
	else:
		return 0,0

# =====================================
# Funcion para leer dht
# =====================================
def readAM2301(pin):
	try:
		humidity, temperature = Adafruit_DHT.read(dht, pin)
		attempts = 0
		while temperature == None and attempts < 3:
			humidity, temperature = Adafruit_DHT.read(dht, pin)
			attempts = attempts+1
			time.sleep(0.1)
		if temperature == None:
			print("DHT no conectado")
			return 0, 0
		else:
			return humidity, temperature
	except:
		print("DHT no conectado")
		return 0, 0

# =====================================
# Funcion para leer ds18b20
# =====================================
def readDS18B20(pin, path):
	try:
		temp = tempSensor.getTemperatureById(path)
		return temp
	except:
		print("DS18B20 no conectado")
		return 0
