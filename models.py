#!/usr/bin/python3
# -*- coding: utf-8 -*- 

from PyQt5.QtSql import (
    QSqlQueryModel, QSqlRelationalTableModel, QSqlRelation, QSqlTableModel)
from PyQt5.QtCore import Qt
import logging

class Models():
    """ Manage models """
    def __init__(self, db):
        self.db = db
        self.create_models()
    
    def create_models(self):
        self.fournisseurs = Fournisseurs(None, self.db)
        self.produits = Produits(None, self.db)
        self.malles_types = MallesTypes(None, self.db)
        self.malles = Malles(None, self.db)
        self.inputs = Inputs(None, self.db)

class Fournisseurs(QSqlTableModel):
    def __init__(self, parent, db):
        super(Fournisseurs, self).__init__(parent, db)
        
        self.setTable('fournisseurs')
        self.select()

class Produits(QSqlTableModel):
    def __init__(self, parent, db):
        super(Produits, self).__init__(parent, db)

        self.setTable('produits')
        self.select()

class Inputs(QSqlRelationalTableModel):
    def __init__(self, parent, db):
        super(Inputs, self).__init__(parent, db)

        self.setTable('inputs')
        rel1 = QSqlRelation('fournisseurs', 'id', 'nom')
        self.setRelation(1, rel1)
        self.setRelation(
            2, QSqlRelation('produits', 'id', 'nom'))
        self.select()

class Malles(QSqlRelationalTableModel):
    def __init__(self, parent, db):
        super(Malles, self).__init__(parent, db)

        self.setTable('malles')
        self.setRelation(
            1, QSqlRelation('malles_types', 'id', 'denomination'))
        self.select()

class MallesTypes(QSqlTableModel):
    def __init__(self, parent, db):
        super(MallesTypes, self).__init__(parent, db)

        self.setTable('malles_types')
        self.setHeaderData(0, Qt.Horizontal, "Référence")
        self.setHeaderData(1, Qt.Horizontal, "Dénomination")
        self.select()

class ExempleModel(QSqlQueryModel):
    def __init__(self):
        super(ExempleModel, self).__init__()
        self.select()
    
    def select(self):
        self.setQuery("QUERY HERE")
        self.setHeaderData(0, Qt.Horizontal, "Nom de colonne 0")
        self.setHeaderData(1, Qt.Horizontal, "Nom de colonne 1")
