#!/usr/bin/python3
# -*- coding: utf-8 -*- 

from PyQt5.QtSql import (
    QSqlQueryModel, QSqlRelationalTableModel, QSqlRelation, QSqlTableModel)

class Models():
    """ Manage models """
    def __init__(self, db):
        self.db = db
        self.create_models()
    
    def create_models(self):
        self.fournisseurs = QSqlTableModel(None, self.db)
        self.fournisseurs.setTable('fournisseurs')
        self.fournisseurs.select()

class MallesTypes(QSqlTableModel):
    def __init__(self, parent, db):
        super(MallesType, self).__init__(parent, db)

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
