#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
route = os.path.dirname(os.getcwd()) + "/Estacion Cafe"
sys.path.append(route + "/src/windows")
from PyQt5.QtWidgets import QDialog, QGraphicsDropShadowEffect, QApplication, QPushButton, QWidget, QDesktopWidget,QFrame, QLabel, QVBoxLayout, QLineEdit, QMessageBox
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt
from dotenv import load_dotenv
import prefs

load_dotenv()
rutaAssets = route + "/assets/"

class Shadow(QGraphicsDropShadowEffect):
    def __init__(self):
        super(Shadow,self).__init__()
        self.setBlurRadius(5)
        self.setXOffset(0)
        self.setYOffset(3)
        self.setColor(QColor(0,0,0,100))

class Login(QDialog):
    def __init__(self):
        super(Login,self).__init__()
        #--- Variables Ventana------
        self.top = 100
        self.left = 100
        self.width = 350
        self.height = 500

        #----Inicializacion Ventana---
        self.setWindowTitle("Login")
        self.setGeometry(self.left,self.top,self.width,self.height)
        self.setFixedSize(self.width,self.height)
        self.setStyleSheet("QDialog {background: white}")
        self.Centrar()
    
        #--- Elementos de La GUI---
        self.widgets()
        
        self.user.setText(os.getenv("USER_ENV"))

        #-- Mostrar Ventana---
        self.show()
        self.setFocus()

    def widgets(self):

        Header = QFrame(self)
        Header.resize(self.width,220)
        Header.setStyleSheet("background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #0d47a1, stop:1 #4a148c)")

        LabelImagen1 = QLabel(self)
        LogoUdenar = QPixmap(rutaAssets + "udenar.png")
        LabelImagen1.setPixmap(LogoUdenar)
        LabelImagen1.resize(LogoUdenar.width(),LogoUdenar.height())
        LabelImagen1.move(self.width/2-LogoUdenar.width()/2,10)

        BackgroundLogin = QFrame(self)
        BackgroundLogin.move(0,180)
        BackgroundLogin.resize(self.width,280)
        BackgroundLogin.setStyleSheet("QFrame {border-radius: 20px; background-color: white; margin-left: 30px;  margin-right: 30px}")
        BackgroundLogin.setGraphicsEffect(Shadow())

        #---Body---
        vbox = QVBoxLayout(BackgroundLogin)

        #---Inicio de Sesion
        titleLogin  = QLabel("Iniciar sesión")
        titleLogin.setAlignment(Qt.AlignCenter)
        titleLogin.setStyleSheet("font: 24px; color: #4a148c; font-weight:bold ")

        userL = QLabel("Usuario")
        userL.setStyleSheet("background-color: rgba(4,28,56, 0);font: 18px;margin-left: 30px; margin-right: 30px; color: #311b92; font-weight:bold")
        self.user = QLineEdit()
        self.user.setStyleSheet("font:14px; margin-left: 30px; margin-right: 30px; padding: 5px")

        #self.user.setPlaceholderText("Ingrese su usuario")

        passwordL = QLabel("Contraseña")
        passwordL.setStyleSheet("background-color: rgba(4,28,56, 0);font: 18px; margin-left: 30px; margin-right: 30px; color: #311b92; font-weight:bold")
        self.password = QLineEdit()
        self.password.setStyleSheet("font:14px; margin-left: 30px; margin-right: 30px; padding: 5px")
        self.password.setEchoMode(QLineEdit.Password)
        
        #self.password.setPlaceholderText("Ingrese su contraseña")

        #--- Ingresar---
        self.iniciar = QPushButton("Iniciar sesión",self)
        self.iniciar.clicked.connect(self.submit)
        self.iniciar.setStyleSheet("background:green")
        self.iniciar.setStyleSheet("QPushButton {background-color:#4a148c; color: white; border-radius: 10px; font: 15px bold; font-weight:bold; margin: 10px 50px 10px 50px ; padding: 7px;}"
                                    "QPushButton:hover { background-color: #7c43bd}"
                                    "QPushButton:pressed { background-color: #12005e}")

        vbox.addWidget(titleLogin)
        vbox.addWidget(userL)
        vbox.addWidget(self.user)
        vbox.addWidget(passwordL)
        vbox.addWidget(self.password)
        vbox.addWidget(self.iniciar)
        vbox.setContentsMargins(0,0,0,0)

        self.mb = QMessageBox(self)
        self.mb.setIcon(QMessageBox.Critical)
        self.mb.setWindowTitle('Error')
        self.mb.setText('Usuario o Constraseña incorrectos')
        self.mb.setStandardButtons(QMessageBox.Ok)

    def Centrar(self):
        S_Screen = QDesktopWidget().availableGeometry().center()
        S_Win = self.geometry()
        self.move(S_Screen.x()-S_Win.width()/2,S_Screen.y() - S_Win.height()/2)

    def submit(self):
        if (self.user.text() == os.getenv("USER_ENV") and self.password.text() == os.getenv("PASS_ENV")):
            self.close()
            self.prefsWindow = prefs.Preferencias()
        else:
            self.mb.show()
