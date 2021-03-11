## Sistema de monitoreo de cultivos de café

## Dependencias

* PyQt5
```
sudo apt-get install python3-pyqt5
sudo apt-get install python3-pyqt5.qtsql
```
* Matplotlib
```
python3 -m pip install -U pip
python3 -m pip install -U matplotlib
```
Si se obtiene un error relacionado con setuptools
```
python3 -m pip install -U pip setuptools
python3 -m pip install matplotlib
```
* Schedule
```
sudo pip3 install schedule
```
* SQLite3
```
sudo apt install sqlite3
sudo apt-get install sqlitebrowser
```
* Paho-mqtt
```
sudo pip3 install paho-mqtt
```

## Sensores
* DHT
```
sudo pip3 install Adafruit_Python_DHT
```
* ADC
```
sudo apt-get update
sudo apt-get install build-essential python-dev python-smbus git
cd ~
git clone https://github.com/adafruit/Adafruit_Python_ADS1x15.git
cd Adafruit_Python_ADS1x15
sudo python3 setup.py install
```
# Configurar usuario y contraseña en las variables de entorno
con
```
sudo nano ~/.profile
```
y agregando las siguientes lineas al final
```
export USER_ENV="your user"
export PASS_ENV="your password"
```
reiniciar el sistema

## Inicio del programa
Ejecutar main.py