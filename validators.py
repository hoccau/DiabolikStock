#!/usr/bin/python3
# -*- coding: utf-8 -*- 

"""
RegExp used for validate Qt fields
"""

from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator

EmailValidator = QRegExpValidator(
    QRegExp('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'))
PhoneValidator = QRegExpValidator(
    QRegExp('^(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}$'))
PriceValidator = QRegExpValidator(QRegExp('\d[\d\,\.]+'))
