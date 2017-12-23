#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Parse an xlsx (Excel) file to populate the database with malles
"""

from openpyxl import load_workbook
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtCore import QSettings
from db import Query
import re

wb = load_workbook(filename = "liste_malles_2018.xlsx", read_only=True)
ws = wb.active

ws.max_row = 525
ws.max_column = 7 # means 'G' column
print(ws.calculate_dimension()) # is it good ?

def get_id(query):
    req = QSqlQuery(query)
    while req.next():
        return req.value(0)

regex = '^[A-Z]-[A-Z][0-9]{2}$' # regex for location (Adresse col)

def get_all_types(sheet):
    types = []
    for row in sheet.iter_rows(row_offset=1):
        type_, number, nom, sousclasse, classe, adresse, observation = row
        if sousclasse not in types:
            types.append(sousclasse)
    return types

def get_all_categories(sheet):
    categories = []
    for row in sheet.iter_rows(row_offset=1):
        type_, number, nom, sousclasse, classe, adresse, observation = row
        if classe not in types:
            types.append(sousclasse)
    return types

def get_col_as_list(col, sheet):
    res = []
    for row in sheet.iter_rows(row_offset=1):
        if row[col] not in res:
            res.append(row[col])
    return res

malles_types = get_col_as_list(3, ws)
categories = get_col_as_list(4, ws)
print(malles_types)
print(categories)

def populate_db(xlsx_row):
    type_, number, nom, sousclasse, classe, adresse, observation = xlsx_row
    if not type_.value or not number.value:
        return False
    reference = type_.value + str(number.value)
    if adresse.value:
        if re.match(regex, adresse.value,flags=re.M):
            section = adresse.value[0]
            slot = adresse.value[2]
            shelf = adresse.value[3:5]
        else:
            section, slot, shelf = '', '', ''
    else:
        section, slot, shelf = '', '', ''
    query = QSqlQuery()
    query.prepare("INSERT INTO malles(\
    reference, category_id, type_id, lieu_id, section, shelf, slot, observation) \
    VALUES(?, ?, ?, ?, ?, ?, ?, ?)")
    query.addBindValue(reference)
    query.addBindValue(category_id)
    query.addBindValue(type_id)
    query.addBindValue(lieu_id)
    query.addBindValue(section)
    query.addBindValue(shelf)
    query.addBindValue(slot)
    query.addBindValue(observation.value)
    query.exec_()

db = Query()
settings = QSettings('Kidivid', 'DiabolikStock')
connected = db.connect(settings)

if connected:
    print('database connexion ok!')

# Location by default
QSqlQuery("INSERT INTO lieux(nom, ville, cp, numero, rue) VALUES \
('Base logistique Ribemont', 'Ribemont-sur-Ancre', 80800, 0, '')")
lieu_id = get_id("SELECT id FROM lieux WHERE nom = 'Base logistique Ribemont'")

for row in ws.iter_rows(row_offset=1):
    populate_db(row)
