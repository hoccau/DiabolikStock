#!/usr/bin/python3
# -*- coding: utf-8 -*- 

from PyQt5.QtWidgets import (
    QDialog, QLineEdit, QTextEdit, QDateEdit, QPushButton, QDataWidgetMapper, 
    QFormLayout, QDialogButtonBox, QMessageBox, QComboBox)
from PyQt5.QtCore import QRegExp, QDate, QByteArray
from PyQt5.QtGui import QRegExpValidator, QIntValidator
from PyQt5.QtSql import QSqlRelationalDelegate
from collections import OrderedDict
import logging

class Form(QDialog):
    """Abstract class not used for the moment"""
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.parent = parent
        self.model = parent.model
        self.grid = QGridLayout()
        self.field_index = 0
        self.submitButton = QPushButton("Enregistrer")
        self.quitButton = QPushButton("Fermer")
        
    def add_field(self, label_name, widget):
        self.field_index += 1
        self.grid.addWidget(QLabel(label_name), self.field_index, 0)
        self.grid.addWidget(widget, self.field_index, 1)

    def add_layout(self, label_name, layout):
        self.field_index += 1
        self.grid.addWidget(QLabel(label_name), self.field_index, 0)
        self.grid.addLayout(layout, self.field_index, 1)

    def initUI(self):
        self.field_index += 1
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.submitButton)
        buttons_layout.addWidget(self.quitButton)
        self.grid.addLayout(buttons_layout, 100, 1) #100 means at the end
        self.setLayout(self.grid)
        self.submitButton.clicked.connect(self.submit_datas)
        self.quitButton.clicked.connect(self.reject)
        self.show()

class MappedQDialog(QDialog):
    def __init__(self, parent, model):
        super(MappedQDialog, self).__init__(parent)

        self.model = model
        self.widgets = OrderedDict()
        self.mapper = QDataWidgetMapper(self)
        self.mapper.setModel(self.model)
        
    def init_add_dialog(self):
        self.init_mapping()
        self.auto_layout()
        self.auto_default_buttons()
        self.add_row()
        self.exec_()
        
    def add_row(self):
        inserted = self.model.insertRow(self.model.rowCount())
        if not inserted:
            logging.warning(
                'Row not inserted in model {0}'.format(self.model))
        self.mapper.toLast()

    def init_mapping(self):
        for field, widget in self.widgets.items():
            self.mapper.addMapping(widget, self.model.fieldIndex(field))
            if self.mapper.mappedSection(widget) == -1:
                logging.warning('Widget '+field+' not mapped.')
        
    def auto_layout(self):
        self.layout = QFormLayout(self)
        for k, v in self.widgets.items():
            self.layout.addRow(k, v)
        
    def auto_default_buttons(self):
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            self)
        buttons.accepted.connect(self.submited)
        buttons.rejected.connect(self.undo)
        self.layout.addRow(buttons)
    
    def undo(self):
        self.model.revertAll()
        self.reject()

class Fournisseur(MappedQDialog):
    def __init__(self, parent, model):
        super(Fournisseur, self).__init__(parent, model)

        self.widgets['nom'] = QLineEdit()
        self.widgets['email'] = QLineEdit()
        self.widgets['phone'] = QLineEdit()
        self.widgets['observation'] = QTextEdit()

        self.widgets['email'].setValidator(QRegExpValidator(
            QRegExp('^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')))
        self.widgets['phone'].setValidator(QRegExpValidator(
            QRegExp('^(?:(?:\+|00)33|0)\s*[1-9](?:[\s.-]*\d{2}){4}$')))

        self.init_mapping()

        self.mapper.addMapping(
            self.widgets['observation'],
            self.model.fieldIndex('observation'),
            QByteArray(b'plainText')) #because default is tohtml

        self.auto_layout()

    def verif(self):
        if not self.widgets['nom'].text():
            QMessageBox.warning(self, "Erreur", "Il faut entrer un nom.")
            return False
        elif len(self.widgets['observation'].toPlainText()) >= 300:
            QMessageBox.warning(
                self,
                "Erreur",
                "Vous avez dépassé le nombre de caractère autorisé en observation.")
        else:
            return True

class AddFournisseur(Fournisseur):
    def __init__(self, parent, model):
        super(AddFournisseur, self).__init__(parent, model)
            
        self.auto_default_buttons()
        self.add_row()
        self.exec_()

    def submited(self):
        if self.verif():
            logging.debug(self.widgets['observation'].toPlainText())
            submited = self.mapper.submit()
            if not submited:
                db_error = self.model.lastError().text()
                if db_error:
                    logging.warning(self.model.tableName()+' '+db_error)
                QMessageBox.warning(self, "Erreur", "L'enregistrement a échoué")
                self.model.select()
                self.reject()
            if submited:
                self.model.select()
                logging.info("Le fournisseur a bien été enregistré")
                self.accept()


class AddInput(MappedQDialog):
    def __init__(self, parent, model):
        super(AddInput, self).__init__(parent, model)

        self.widgets['fournisseur_id'] = QComboBox()
        self.widgets['produit_id'] = QComboBox()
        self.widgets['date_achat'] = QDateEdit()
        self.widgets['price'] = QLineEdit()

        self.widgets['date_achat'].setDate(QDate.currentDate())

        f_index = self.model.fieldIndex('fournisseur_id') #fails
        fournisseur_model = self.model.relationModel(1) #fournisseur_id col
        produit_model = self.model.relationModel(2) #produit_id col

        self.widgets['fournisseur_id'].setModel(fournisseur_model)
        self.widgets['fournisseur_id'].setModelColumn(
            fournisseur_model.fieldIndex('nom'))
        self.widgets['produit_id'].setModel(produit_model)
        self.widgets['produit_id'].setModelColumn(
            produit_model.fieldIndex('nom'))

        self.mapper.setItemDelegate(QSqlRelationalDelegate(self))

        self.mapper.addMapping(self.widgets['fournisseur_id'], 1)
        self.mapper.addMapping(self.widgets['produit_id'], 2)
        self.mapper.addMapping(self.widgets['date_achat'], 3)
        self.mapper.addMapping(self.widgets['price'], 4)
        
        for key, widget in self.widgets.items():
            if self.mapper.mappedSection(widget) == -1:
                logging.warning(key+' is not mapped.')

        self.auto_layout()
        self.auto_default_buttons()
        self.add_row()
        self.exec_()

    def submited(self):
        submited = self.mapper.submit()
        if submited:
            self.model.select()
            logging.info("L'entrée a bien été enregistrée")
            self.accept()
        if not submited:
            db_error = self.model.lastError().type()
            last_query = self.model.query().lastError().type()
            logging.debug(db_error)
            if db_error:
                logging.warning(self.model.tableName()+' '+db_error)
            QMessageBox.warning(self, "Erreur", "L'enregistrement a échoué")

class AddMalle(MappedQDialog):
    def __init__(self, parent, model):
        super(AddMalle, self).__init__(parent, model)

        self.widgets['reference'] = QLineEdit()
        self.widgets['type_id'] = QLineEdit()
        
        self.init_add_dialog()

    def submited(self):
        pass
    
class AddMalleType(MappedQDialog):
    def __init__(self, parent, model):
        super(AddMalleType, self).__init__(parent, model)

        self.widgets['denomination'] = QLineEdit()
        self.widgets['observation'] = QLineEdit()
        
        self.init_add_dialog()

    def submited(self):
        pass
