#!/usr/bin/python3
# -*- coding: utf-8 -*- 

from PyQt5.QtWidgets import (
    QDialog, QLineEdit, QTextEdit, QPushButton, QDataWidgetMapper, QFormLayout,
    QDialogButtonBox, QMessageBox)
from PyQt5.QtCore import QRegExp, QDate, QByteArray
from PyQt5.QtGui import QRegExpValidator, QIntValidator
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

class Fournisseur(QDialog):
    def __init__(self, parent, model):
        super(Fournisseur, self).__init__(parent)

        self.model = model

        self.widgets = OrderedDict([
        #('id', QSpinBox()),
        ('nom', QLineEdit()),
        ('email', QLineEdit()),
        ('phone', QLineEdit()),
        ('observation', QTextEdit()),
        ])

        self.mapper = QDataWidgetMapper(self)
        self.mapper.setModel(self.model)
        for field, widget in self.widgets.items():
            self.mapper.addMapping(widget, model.fieldIndex(field))
            logging.debug(
                str(field) + ' is mapped:'\
                + str(self.mapper.mappedSection(widget)))
        self.mapper.addMapping(
            self.widgets['observation'],
            model.fieldIndex('observation'),
            QByteArray(b'plaintext')) #because default is tohtml
        
        self.layout = QFormLayout(self)
        for k, v in self.widgets.items():
            self.layout.addRow(k, v)

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
        
        inserted = self.model.insertRow(self.model.rowCount())
        if not inserted:
            logging.warning('Row not inserted in model {0}'.format(self.model))
        self.mapper.toLast()

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            self)
        buttons.accepted.connect(self.submited)
        buttons.rejected.connect(self.reject)

        self.layout.addRow(buttons)

        self.exec_()

    def submited(self):
        if self.verif():
            submited = self.mapper.submit()
            if not submited:
                logging.warning("oups, le submit n'a pas fonctionné")
                db_error = self.model.lastError().databaseText()
                if db_error:
                    logging.info(db_error)
                QMessageBox.warning(self, "Erreur", "L'enregistrement a échoué")
            if submited:
                logging.info("Le fournisseur a bien été enregistré")
                self.accept()
