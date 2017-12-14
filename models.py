#!/usr/bin/python3
# -*- coding: utf-8 -*- 

from PyQt5.QtSql import (
    QSqlQueryModel, QSqlRelationalTableModel, QSqlRelation, QSqlTableModel,
    QSqlQuery, QSqlRecord)
from PyQt5.QtCore import Qt
import logging

class Models():
    """ Manage models """
    def __init__(self, db):
        self.db = db
        self.create_models()
        self.create_connections()
    
    def create_models(self):
        self.fournisseurs = Fournisseurs(None, self.db)
        self.produits = Produits(None, self.db)
        self.malles_types = MallesTypes(None, self.db)
        self.malles = Malles(None, self.db)
        self.contenu_malles = ContenuMalles()
        self.malle_log = MalleLog(None, self.db)
        self.inputs = Inputs(None, self.db)
        self.contenu_type = ContenuType(None, self.db)
        self.malles_types_with_malles = MallesTypesWithMalles()
        self.sejours = Sejours(None, self.db)
        self.lieux = QSqlTableModel(None, self.db)
        self.lieux.setTable('lieux')
        self.lieux.select()
        self.lieux.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.sejours_malles_types = SejoursMallesTypes(None, self.db)
        self.reservations = Reservations(None, self.db)
        self.users_groups_rel = QSqlTableModel(None, self.db)
        self.users_groups_rel.setTable('users_groups_rel')
        self.users_groups_rel.select()
        #self.users_groups_rel.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.users = Users(None, self.db, self.users_groups_rel)
        logging.info("Models created.")

    def create_connections(self):
        contenu_type_products = self.contenu_type.relationModel(2)
        self.produits.dataChanged.connect(contenu_type_products.select)

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

class ContenuMalles(QSqlQueryModel):
    def __init__(self):
        super().__init__()
        self.filter = None
        self.etats_model = QSqlTableModel()
        self.etats_model.setTable('etats')
        self.etats_model.select()

    def select(self):
        query = "SELECT contenu_malles.id, "\
        + "malle_ref, "\
        + "produits.nom, "\
        + "contenu_type.quantity AS qté_prévue, "\
        + "contenu_malles.quantity AS qté_réelle, "\
        + "etats.etat, "\
        + "contenu_malles.observation "\
        + "FROM contenu_malles "\
        + "LEFT JOIN contenu_type ON contenu_type.id = contenu_type_id "\
        + "INNER JOIN produits ON produits.id = contenu_type.produit_id "\
        + "INNER JOIN etats ON etats.id = contenu_malles.etat_id"
        if self.filter:
            query += " WHERE " + self.filter
        query += " ORDER BY contenu_malles.id"
        self.setQuery(query)
        if self.lastError().text().rstrip():
            logging.warning(self.lastError().text())

    def setFilter(self, filter_):
        self.filter = filter_
        self.select()
    
    def setData(self, index, value, role):
        id_ = index.model().data(index.sibling(index.row(), 0))
        if index.column() == 4:
            self.update_data("quantity", value, id_)
        elif index.column() == 5:
            self.update_data("etat_id", value, id_)
        elif index.column() == 6:
            self.update_data("observation", value, id_)
        self.select()
        return True

    def flags(self, index):
        flags = super().flags(index)
        if index.column() in (4, 5, 6):
            flags |= Qt.ItemIsEditable
        return flags

    def update_data(self, field, value, id_):
        query = QSqlQuery()
        query.prepare("UPDATE contenu_malles "\
        + "SET " + field + " = :val "\
        + "WHERE contenu_malles.id = :id_")
        query.bindValue(':val', value)
        query.bindValue(':id_', id_)
        query.exec_()
        self.select()
        
class MalleLog(QSqlRelationalTableModel):
    def __init__(self, parent, db):
        super().__init__(parent, db)

        self.setTable('malle_log')
        self.setRelation(
            1, QSqlRelation('users', 'id', 'name'))
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
            return True
        else:
            error = query.lastError()
            self.setLastError(error)
            return False

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

class Users(QSqlTableModel):
    def __init__(self, parent, db, users_groups_rel_model):
        super().__init__(parent, db)

        self.users_groups_rel_model = users_groups_rel_model
        self.setTable('users')
        self.setEditStrategy(QSqlTableModel.OnManualSubmit)
        self.select()

    def set_group(self, user_id, group_id):
        logging.debug(str(user_id) + ' ' + str(group_id))
        model = self.users_groups_rel_model
        inserted = model.insertRow(model.rowCount())
        model.setData(model.index(model.rowCount() - 1, 1), user_id)
        model.setData(model.index(model.rowCount() - 1, 2), group_id)
        submited = model.submitAll()
        logging.debug(submited)
        if submited:
            logging.info("group submited")
        if not submited:
            logging.debug(model.lastError().text())

    def get_groups(self, user_id):
        model = self.users_groups_rel_model
        logging.debug(model.rowCount())
        model.setFilter('user_id = ' + str(user_id))
        logging.debug(model.rowCount())
        groups = [model.data(model.index(i, 2)) for i in range(model.rowCount())]
        model.setFilter('')
        return groups

    def get_id_by_name(self, name):
        for i in range(self.rowCount()):
            if self.index(i, 1).data() == name:
                return self.index(i, 0).data()

