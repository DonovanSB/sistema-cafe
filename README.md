## Sistema de monitoreo de cultivos de café

## Instalar librerias automaticamente 
correr en la ruta del repositorio
```
sh ./install.sh
```

## Manualmente:

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

## Correr app cuando inicia Raspberry
```
mkdir ~/.config/autostart
sudo nano ~/.config/autostart/nombre.desktop
```
pegar
```
[Desktop Entry]
Encoding=UTF-8
Type=Application
Name=Secado
Exec=python3 /home/pi/Development/sistema-cafe/Secado/main.py
Terminal=true
Categories=Utility;
StartupNotify=true
```
## Acceso directo en aplicaciones
```
sudo nano /usr/share/applications/nombre.desktop
```

## Configuración Fermentación
Agregar un archivo .json en la ruta sistema-cafe->Fermentacion->src->providers con los ids de los sensores de temperatura encapsulados ds18b20, con la siguiente estructura y con el nombre devices.json
```
{
    "sensor1": "/sys/bus/w1/devices/28-01191f16007e/w1_slave",
    "sensor2": "/sys/bus/w1/devices/28-0119126fe5aa/w1_slave",
    "sensor3": "/sys/bus/w1/devices/28-01191254f3e8/w1_slave",
    "sensor4": "/sys/bus/w1/devices/28-0119125c8982/w1_slave"
}
```