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
        self.sejours = Sejours(None, self.db)
        self.lieux = QSqlTableModel(None, self.db)
        self.lieux.setTable('lieux')
        self.lieux.select()
        self.lieux.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.sejours_malles_types = SejoursMallesTypes(None, self.db)
        self.contenu_checker = ContenuChecker()
        self.reservations = Reservations(None, self.db)

class Fournisseurs(QSqlTableModel):
    def __init__(self, parent, db):
        super(Fournisseurs, self).__init__(parent, db)
        
        self.setTable('fournisseurs')
        self.select()

class Produits(QSqlRelationalTableModel):
    def __init__(self, parent, db):
        super(Produits, self).__init__(parent, db)

        self.setTable('produits')
        self.setRelation(2, QSqlRelation('fournisseurs', 'id', 'nom'))
        self.select()

class Inputs(QSqlRelationalTableModel):
    def __init__(self, parent, db):
        super(Inputs, self).__init__(parent, db)

        self.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.setTable('inputs')
        rel1 = QSqlRelation('fournisseurs', 'id', 'nom')
        self.setRelation(1, rel1)
        rel2 = QSqlRelation('produits', 'id', 'nom')
        self.setRelation(2, rel2)
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
        self.setRelation(
            2, QSqlRelation('lieux', 'id', 'nom'))
        self.setJoinMode(QSqlRelationalTableModel.LeftJoin)
        self.setEditStrategy(QSqlTableModel.OnManualSubmit)
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

    def removeRow(self, row):
        id_ = self.data(self.index(row, 0))
        logging.debug(id_)
        query = QSqlQuery()
        query.prepare("DELETE FROM malles_types WHERE id = :id_")
        query.bindValue(':id_', id_)
        res = query.exec_()
        if res:
            logging.info("Malle type id: " + str(id_) + " deleted.")
            self.select()
        else:
            logging.warning(query.lastError().text())

class ContenuType(QSqlRelationalTableModel):
    def __init__(self, parent, db):
        super(ContenuType, self).__init__(parent, db)
        
        self.setTable('contenu_type')
        self.setRelation(
            2, QSqlRelation('produits', 'id', 'nom'))
        self.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.select()

class ProduitsModel(QSqlQueryModel):
    def __init__(self):
        super(ProduitsModel, self).__init__()
        self.select()
    
    def select(self):
        self.setQuery(
            """
            SELECT produits.nom,
            coalesce(sum(quantity), 0) AS quantité 
            FROM produits
            LEFT JOIN contenu_malles ON contenu_malles.produit_id = produits.id 
            INNER JOIN fournisseurs 
            ON fournisseurs.id = produits.fournisseur_id 
            GROUP BY produits.nom
            """)

class Sejours(QSqlRelationalTableModel):
    def __init__(self, parent, db):
        super().__init__(parent, db)

        self.setTable('sejours')
        rel = QSqlRelation('lieux', 'id', 'nom')
        self.setRelation(2, rel)
        self.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.select()

class SejoursMallesTypes(QSqlRelationalTableModel):
    def __init__(self, parent, db):
        super().__init__(parent, db)
        self.setTable('sejours_malles_types_rel')
        rel = QSqlRelation('malles_types', 'id', 'denomination')

class Reservations(QSqlRelationalTableModel):
    def __init__(self, parent, db):
        super().__init__(parent, db)
        self.setTable('reservations')
        rel = QSqlRelation('sejours', 'id', 'nom')
        self.setRelation(1, rel)

class ContenuChecker(QSqlQueryModel):
    def __init__(self):
        super().__init__()
        self.main_query = "SELECT id, nom, reel, attendu, "\
        + "difference, etat "\
        + "FROM contenu_check "
        self.current_filter = 'malle_ref = NULL'
        self.etats_model = QSqlTableModel()
        self.etats_model.setTable('etats')
        self.etats_model.select()

    def select(self):
        self.setQuery(self.main_query + " WHERE " + self.current_filter)

    def setFilter(self, filter_):
        self.current_filter = filter_
        self.select()
    
    def setData(self, index, value, role):
        logging.debug(index.column())
        id_ = index.model().data(index.sibling(index.row(), 0))
        if index.column() == 5:
            self.set_etat(value, id_)
        elif index.column() == 2:
            self.set_nbr(value, id_)
        self.select()
        return value

    def flags(self, index):
        flags = super().flags(index)
        if index.column() in (2, 5):
            flags |= Qt.ItemIsEditable
        return flags

    def set_etat(self, etat_id, id_):
        query = QSqlQuery()
        query.prepare("UPDATE contenu_malles "\
        + "SET etat_id = :etat_id "\
        + "WHERE contenu_malles.id = :id_")
        query.bindValue(':etat_id', etat_id)
        query.bindValue(':id_', id_)
        query.exec_()

    def set_nbr(self, quantity, id_):
        query = QSqlQuery()
        query.prepare("UPDATE contenu_malles "\
        + "SET quantity = :quantity "\
        + "WHERE contenu_malles.id = :id_")
        query.bindValue(':quantity', quantity)
        query.bindValue(':id_', id_)
        query.exec_()

