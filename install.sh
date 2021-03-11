#! /bin/bash
sudo apt install toilet
toilet -f mono12 -F metal App café Udenar
echo =========== Empezaremos con la instalación de librerías ...============
sudo apt update
sudo apt upgrade

echo =========== Instalando PyQt5 ===========
sudo apt-get install python3-pyqt5
sudo apt-get install python3-pyqt5.qtsql

echo =========== Instalando Matplotlib ===========
python3 -m pip install -U pip
python3 -m pip install -U matplotlib

echo =========== Instalando schedule ===========
sudo pip3 install schedule

echo =========== Instalando sqlite3 ===========
sudo apt install sqlite3
sudo apt install sqlitebrowser

echo =========== Instalando Paho-mqtt ===========
sudo pip3 install paho-mqtt

echo =========== Instalando DHT ===========
sudo pip3 install Adafruit_Python_DHT

echo =========== Instalando ADC ===========
sudo apt-get install build-essential python-dev python-smbus git
cd ~
git clone https://github.com/adafruit/Adafruit_Python_ADS1x15.git
cd Adafruit_Python_ADS1x15
sudo python3 setup.py install

git checkout hardware