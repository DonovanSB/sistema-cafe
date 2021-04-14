#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from PyQt5.QtWidgets import QDialog, QGraphicsDropShadowEffect, QPushButton, QDesktopWidget,QFrame, QLabel, QVBoxLayout, QLineEdit, QMessageBox
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt
parent = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir)
route = os.path.abspath(parent)
sys.path.append(route + "/src/windows")
import prefs

rutaAssets = route + "/assets/"

class Shadow(QGraphicsDropShadowEffect):
    def __init__(self):
        super().__init__()
        self.setBlurRadius(5)
        self.setXOffset(0)
        self.setYOffset(3)
        self.setColor(QColor(0,0,0,100))

class Login(QDialog):
    def __init__(self):
        super().__init__()
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
        self.centrar()

        #--- Elementos de La GUI---
        self.widgets()

        self.user.setText(os.getenv("USER_ENV"))
        self.password.setText(os.getenv("PASS_ENV"))

        #-- Mostrar Ventana---
        self.show()
        self.setFocus()

    def widgets(self):

        header = QFrame(self)
        header.resize(self.width,220)
        header.setStyleSheet("background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 #0d47a1, stop:1 #4a148c)")

        labelImagen1 = QLabel(self)
        logoUdenar = QPixmap(rutaAssets + "udenar.png")
        labelImagen1.setPixmap(logoUdenar)
        labelImagen1.resize(logoUdenar.width(),logoUdenar.height())
        labelImagen1.move(self.width/2-logoUdenar.width()/2,10)

        backgroundLogin = QFrame(self)
        backgroundLogin.move(0,180)
        backgroundLogin.resize(self.width,280)
        backgroundLogin.setStyleSheet("QFrame {border-radius: 20px; background-color: white; margin-left: 30px;  margin-right: 30px}")
        backgroundLogin.setGraphicsEffect(Shadow())

        #---Body---
        vbox = QVBoxLayout(backgroundLogin)

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

        # self.password.setPlaceholderText("Ingrese su contraseña")

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

        self.messageBox = QMessageBox(self)
        self.messageBox.setIcon(QMessageBox.Critical)
        self.messageBox.setWindowTitle('Error')
        self.messageBox.setText('Usuario o Constraseña incorrectos')
        self.messageBox.setStandardButtons(QMessageBox.Ok)

    def centrar(self):
        sizeScreen = QDesktopWidget().availableGeometry().center()
        sizeWindow = self.geometry()
        self.move(sizeScreen.x()-sizeWindow.width()/2,sizeScreen.y() - sizeWindow.height()/2)

    def submit(self):
        if (self.user.text() == os.getenv("USER_ENV") and self.password.text() == os.getenv("PASS_ENV")):
            self.close()
            self.prefsWindow = prefs.Preferencias()
        else:
            self.messageBox.show()
