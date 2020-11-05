# =====================================
# Configuracion ADC
# =====================================
import Adafruit_ADS1x15
adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1

# =====================================
# Configuracion AM2301 (DHT22)
# =====================================
import Adafruit_DHT
dht = Adafruit_DHT.DHT22
pinDHT = 23

# =====================================
# Configuracion Velocidad viento
# =====================================
import RPi.GPIO as GPIO
import time, threading
GPIO.setmode(GPIO.BCM)
VELOCITY_PIN = 24
GPIO.setup(VELOCITY_PIN,GPIO.IN)

# Detectar pulsos de giro
contVelocityInterrupt = 0
def detectPulse(chanel):
	global contVelocityInterrupt
	contVelocityInterrupt = contVelocityInterrupt + 1
	
GPIO.add_event_detect(VELOCITY_PIN, GPIO.RISING, callback = detectPulse)

# Tarea para calcular velocidad
periodCalculateVelocity = 5
velocityCalculated = 0
	
def calculateSpeed():
	global contVelocityInterrupt, velocityCalculated
	velocityCalculated = contVelocityInterrupt*(2.25/periodCalculateVelocity)
	velocityCalculated = velocityCalculated*1.60934
	contVelocityInterrupt = 0
	threading.Timer(periodCalculateVelocity, calculateSpeed).start()

threading.Timer(periodCalculateVelocity, calculateSpeed).start()
	
# =====================================
# Configuracion Pluviometro
# =====================================
import datetime
PLUVIOMETER_PIN = 18
GPIO.setup(PLUVIOMETER_PIN, GPIO.IN)
quantityIncrease = 0.26393	# ml de agua por pulso
restartTimeTimerCounter = 60*10
dailyPrecipitationCalculated = 0
flagResetValue = False

def calculatePrecipitation(chanel):
	global dailyPrecipitationCalculated
	dailyPrecipitationCalculated = dailyPrecipitationCalculated + quantityIncrease

GPIO.add_event_detect(PLUVIOMETER_PIN, GPIO.RISING, callback = calculatePrecipitation)

# Reiniciar el contador de precipitacion
def restartTimerCounter():
	global dailyPrecipitationCalculated, flagResetValue
	now = datetime.datetime.now()
	
	if now.hour == 0 and flagResetValue:
		dailyPrecipitationCalculated = 0
		flagResetValue = False
		
	if now.hour > 0:
		flagResetValue = True

	threading.Timer(restartTimeTimerCounter, restartTimerCounter).start()
	
threading.Timer(restartTimeTimerCounter, restartTimerCounter).start()

# =====================================
# Clase de sensores
# =====================================
class SensorsStation:
	def __init__(self):
		return
		
	def getRadiation(self):
		dataAdc = adc.read_adc(1, gain=GAIN)
		radiation = convertRange(dataAdc, 0, 26400, 0, 1800)
		return radiation
		
	def getDirection(self):
		dataAdc = adc.read_adc(0, gain=2/3)
		return convertRange(dataAdc, 0, 27070, 0, 360)
		
	def getTemperature(self):
		humidity, temperature = readAM2301(pinDHT)
		return temperature
		
	def getHumidity(self):
		humidity, temperature = readAM2301(pinDHT)
		return humidity
		
	def getHumidityAndTemperature(self):
		hum = 100
		while hum >= 100:
			hum, temp = readAM2301(pinDHT)
		return min(max(hum,0),100), min(max(temp,0),100)
	
	def getVelocity(self):
		global velocityCalculated
		return velocityCalculated
	
	def getPrecipitation(self):
		global dailyPrecipitationCalculated
		return dailyPrecipitationCalculated

# =====================================
# Funcion para convertir entre rangos
# =====================================
def convertRange(x, in_min, in_max, out_min, out_max):
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

# =====================================
# Funcion para leer dht
# =====================================
def readAM2301(pin):
	try:
		humidity, temperature = Adafruit_DHT.read_retry(dht, pin)
		if temperature == None:
			print("DHT no conectado")
			return 0, 0
		else:
			return humidity, temperature
	except:
		print("DHT no conectado")
		return 0, 0
