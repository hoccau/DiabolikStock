#!/usr/bin/python3
# -*- coding: utf-8 -*- 

from PyQt5.QtWidgets import QMessageBox
import logging

def displayed_error(error):
    QMessageBox.warning(None, "Erreur", error.text())
    logging.warning(error.text())

