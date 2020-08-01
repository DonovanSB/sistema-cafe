## Sistema de monitoreo de cultivos de café

## Dependencias

* PyQt5
```
sudo apt-get install python-pyqt5
sudo apt-get install python-pyqt5.qtsql
```
* Matplotlib
```
python -m pip install -U pip
python -m pip install -U matplotlib
```
Si se obtiene un error relacionado con setuptools
```
python -m pip install -U pip setuptools
python -m pip install matplotlib
```
* Schedule
```
sudo pip install schedule
```
* SQLite3
```
sudo apt install sqlite3
```
# Configurar usuario y contraseña en las variables de entorno
con
```
sudo nano ~/.profile
```
y agregando las siguientes lineas al final
```
USER_ENV="your user"
PASS_ENV="your password"
```
reiniciar el sistema

## Inicio del programa
Ejecutar main.py