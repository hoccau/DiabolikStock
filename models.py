#!/usr/bin/python3
# -*- coding: utf-8 -*- 

from PyQt5.QtSql import (
    QSqlQueryModel, QSqlRelationalTableModel, QSqlRelation, QSqlTableModel,
    QSqlQuery)
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
        self.contenu_malles = ContenuMalles(None, self.db) 
        self.inputs = Inputs(None, self.db)
        self.contenu_type = ContenuType(None, self.db)
        self.malles_types_with_malles = MallesTypesWithMalles()

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

    def fill_stock(self, produit_id, quantity):
        query = QSqlQuery(
            "INSERT INTO contenu_malles(malle_ref, produit_id, quantity, etat_id) "
            + "VALUES('VSTOCK', "+str(produit_id)+", "+str(quantity)+", 1)")

class Malles(QSqlRelationalTableModel):
    def __init__(self, parent, db):
        super(Malles, self).__init__(parent, db)

        self.setTable('malles')
        self.setRelation(
            1, QSqlRelation('malles_types', 'id', 'denomination'))
        self.select()

class ContenuMalles(QSqlRelationalTableModel):
    def __init__(self, parent, db):
        super(ContenuMalles, self).__init__(parent, db)

        self.setTable('contenu_malles')
        self.setRelation(2, QSqlRelation('produits', 'id', 'nom'))
        self.setRelation(4, QSqlRelation('etats', 'id', 'etat'))
        self.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.select()

class MallesTypes(QSqlTableModel):
    def __init__(self, parent, db):
        super(MallesTypes, self).__init__(parent, db)

        self.setTable('malles_types')
        self.setHeaderData(1, Qt.Horizontal, "Dénomination")
        self.select()

class MallesTypesWithMalles(QSqlQueryModel):
    def __init__(self):
        super(MallesTypesWithMalles, self).__init__()
        self.select()

    def select(self):
        self.setQuery(
            " SELECT id, denomination, string_agg(reference, ', ') "\
            + "FROM malles_types "\
            + "LEFT JOIN malles ON malles.type_id = malles_types.id "\
            + "GROUP BY id")
        self.setHeaderData(1, Qt.Horizontal, "Dénomination")
        self.setHeaderData(2, Qt.Horizontal, "Malles")

class ContenuType(QSqlRelationalTableModel):
    def __init__(self, parent, db):
        super(ContenuType, self).__init__(parent, db)
        
        self.setTable('contenu_type')
        self.setRelation(
            1, QSqlRelation('produits', 'id', 'nom'))
        self.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.select()

class ProduitsModel(QSqlQueryModel):
    def __init__(self):
        super(ProduitsModel, self).__init__()
        self.select()
    
    def select(self):
        self.setQuery(
            "SELECT produits.nom, sum(quantity) FROM contenu_malles "\
            + "INNER JOIN produits ON produit_id = produits.id "\
            + "GROUP BY produits.nom")
