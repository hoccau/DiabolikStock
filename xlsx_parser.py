#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Parse an xlsx (Excel) file to populate the database with malles
"""

from openpyxl import load_workbook
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
import re

wb = load_workbook(filename = "liste_malles_2017.xlsx", read_only=True)
ws = wb.active

ws.max_row = 525
ws.max_column = 6 # means 'F' column
print(ws.calculate_dimension()) # is it good ?

database = QSqlDatabase.addDatabase('QPSQL')
database.setHostName("localhost")
database.setDatabaseName("testdiabostock")
database.setUserName("hoccau")
database.setPassword('password')
if database.open():
    print('database connexion ok!')

# Because type definition is not clear, I define a SansType type. 
QSqlQuery("INSERT INTO malles_types(denomination, observation) VALUES ('SansType', 'Ce type doit rester sans produit. Il sert simplement à définir des malles sans aucun type')")
QSqlQuery("INSERT INTO lieux(nom, ville, cp, numero, rue) VALUES \
('Base logistique Ribemont', 'Ribemont-sur-Ancre', 80800, 0, '')")

def get_id(query):
    req = QSqlQuery(query)
    while req.next():
        return req.value(0)

type_id = get_id("SELECT id FROM malles_types WHERE denomination = 'SansType'")
lieu_id = get_id("SELECT id FROM lieux WHERE nom = 'Base logistique Ribemont'")

regex = '^[A-Z]-[A-Z][0-9]{2}$' # regex for location (Adresse col)

def populate_db(xlsx_row):
    type_, number, nom, classe, adresse, observation = xlsx_row
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
    reference, type_id, lieu_id, section, shelf, slot, observation) \
    VALUES(?, ?, ?, ?, ?, ?, ?)")
    query.addBindValue(reference)
    query.addBindValue(type_id)
    query.addBindValue(lieu_id)
    query.addBindValue(section)
    query.addBindValue(shelf)
    query.addBindValue(slot)
    query.addBindValue(observation.value)
    query.exec_()

for row in ws.iter_rows(row_offset=1):
    populate_db(row)
