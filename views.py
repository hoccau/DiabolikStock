#!/usr/bin/python3
# -*- coding: utf-8 -*- 

from PyQt5.QtWidgets import (
    QDialog, QLineEdit, QTextEdit, QDateEdit, QPushButton, QDataWidgetMapper, 
    QFormLayout, QGridLayout, QDialogButtonBox, QMessageBox, QComboBox,
    QTableView, QAbstractItemView, QGroupBox, QHBoxLayout, QVBoxLayout, 
    QLabel, QWidget)
from PyQt5.QtCore import QRegExp, QDate, QByteArray, QSize
from PyQt5.QtGui import QRegExpValidator, QIntValidator, QIcon
from PyQt5.QtSql import QSqlRelationalDelegate
from collections import OrderedDict
import logging

class StartupView(QWidget):
    def __init__(self, parent):
        super(StartupView, self).__init__(parent)
        
        self.grid = QGridLayout()

        malle_button = self._create_button('caisse.png', 'Nouvelle malle')
        malle_type_button = self._create_button('caisse_type.png', 'Nouveau type')
        fournisseur_button = self._create_button('fournisseur.png', 'Nouveau fournisseur')
        input_button = self._create_button('input.png', 'Entrée de Produit')
        
        self.grid.addWidget(malle_button, 0, 0)
        self.grid.addWidget(malle_type_button, 0, 1)
        self.grid.addWidget(fournisseur_button, 1, 0)
        self.grid.addWidget(input_button, 1, 1)

        self.setLayout(self.grid)

        malle_button.clicked.connect(parent.add_malle)
        malle_type_button.clicked.connect(parent.add_malle_type)
        input_button.clicked.connect(parent.add_input)
        fournisseur_button.clicked.connect(parent.add_fournisseur)

    def _create_button(self, image, text):
        button = QPushButton()
        button.setIcon(QIcon('images/'+image))
        button.setIconSize(QSize(127, 100))
        button.setText(text)
        return button

class DisplayTableViewDialog(QDialog):
    def __init__(self, parent, model):
        super(DisplayTableViewDialog, self).__init__(parent)
        
        view = QTableView(self)
        view.setModel(model)
        view.setItemDelegate(QSqlRelationalDelegate())
        view.setEditTriggers(QAbstractItemView.NoEditTriggers)

        close_button = QPushButton('Fermer')

        layout = QVBoxLayout()
        layout.addWidget(view)
        layout.addWidget(close_button)
        self.setLayout(layout)

        close_button.clicked.connect(self.accept)

        self.exec_()

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

class AddProduct(MappedQDialog):
    def __init__(self, parent, model):
        super(AddProduct, self).__init__(parent, model)

        self.widgets['nom'] = QLineEdit()
        self.init_add_dialog()

    def submited(self):
        submited = self.mapper.submit()
        if submited:
            logging.info('produit added.')
            self.accept()
        else:
            logging.warning(self.model.lastError().text())

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

        self.contenu_malles_model = parent.models.contenu_malles

        self.widgets['reference'] = QLineEdit()
        self.widgets['type_id'] = QComboBox()

        type_model = self.model.relationModel(1)
        logging.debug(type_model)
        self.widgets['type_id'].setModel(type_model)
        self.widgets['type_id'].setModelColumn(
            type_model.fieldIndex('denomination'))
        
        self.mapper.setItemDelegate(QSqlRelationalDelegate(self))
        
        self.mapper.addMapping(self.widgets['reference'], 0)
        self.mapper.addMapping(self.widgets['type_id'], 1)

        self.auto_layout()
        self.auto_default_buttons()
        self.add_row()
        self.exec_()

    def submited(self):
        submited = self.mapper.submit()
        if submited:
            self.model.select()
            logging.info('Malle added.')
            self.accept()
            contenu = AddContenuMalle(self, self.contenu_malles_model)
            contenu.exec_()
        else:
            logging.warning(self.model.lastError().text())
            if error.nativeErrorCode() == '23505':
                QMessageBox.warning(
                    self, "Erreur", "Cette référence existe déjà.")

class AddContenuMalle(QDialog):
    def __init__(self, parent, model):
        super(AddContenuMalle, self).__init__(parent)
        
        self.model = model
        self.parent_record = parent.model.record(parent.model.rowCount() -1)
        logging.debug(self.parent_record)
        self.malle_ref = self.parent_record.value(0)
        self.model.setFilter("malle_ref = '"+str(self.malle_ref)+"'")

        self.title_label = QLabel(
            "Contenu de la malle " + self.parent_record.value(0))

        self.products_table = QTableView()
        self.products_table.setModel(self.model)
        self.products_table.setItemDelegate(QSqlRelationalDelegate())

        self.add_button = QPushButton('+')
        self.finish_button = QPushButton('Terminé')
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.products_table)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.finish_button)
        self.layout.addLayout(buttons_layout)
        self.setLayout(self.layout)
        
        self.add_button.clicked.connect(self.add_row)
        self.finish_button.clicked.connect(self.terminated)
        
    def submit_row(self):
        submited = self.model.submitAll()
        if not submited:
            error = self.model.lastError()
            logging.warning(error.text())
            logging.debug(self.model.query().lastQuery())
            if error.nativeErrorCode() == '23505':
                QMessageBox.warning(
                    self, "Erreur", "Ce produit semble déjà exister pour cette malle")
            elif error.nativeErrorCode() == '23502':
                QMessageBox.warning(
                    self, "Erreur", "Êtes-vous sûr(e) d'avoir entré un produit?")
            return False
        else:
            return True
    
    def add_row(self):
        if self.model.isDirty():
            submited = self.submit_row()
        inserted = self.model.insertRow(self.model.rowCount())
        record = self.model.record()
        record.setValue('malle_ref', self.malle_ref)
        record.setGenerated('id', False)
        record_is_set = self.model.setRecord(self.model.rowCount() -1, record)
        if not inserted:
            logging.warning(
                'Row not inserted in model {0}'.format(self.model))

    def terminated(self):
        if self.model.isDirty():
            submited = self.submit_row()
            if not submited:
                return False
        self.close()
    
class AddMalleType(MappedQDialog):
    def __init__(self, parent, model):
        super(AddMalleType, self).__init__(parent, model)

        self.contenu_type_model = parent.models.contenu_type
        self.widgets['denomination'] = QLineEdit()
        self.widgets['observation'] = QTextEdit()
        self.widgets['denomination'].setPlaceholderText('ex: Pédagogique')
        self.init_mapping()

        self.mapper.addMapping(
            self.widgets['observation'],
            self.model.fieldIndex('observation'),
            QByteArray(b'plainText')) #because default is tohtml

        self.auto_layout()

        self.auto_default_buttons()
        self.add_row()
        self.exec_()

    def submited(self):
        submited = self.mapper.submit()
        if submited:
            self.model.select()
            self.accept()
            self.products = AddContenuType(self, self.contenu_type_model)
            self.products.exec_()
        else:
            error = self.model.lastError()
            logging.warning(error.text())
            if error.nativeErrorCode() == '23505':
                QMessageBox.warning(
                    self, "Erreur", "Cette malle type semble déjà exister")

class AddContenuType(QDialog):
    def __init__(self, parent, model):
        super(AddContenuType, self).__init__(parent)

        self.model = model
        self.parent_record = parent.model.record(parent.model.rowCount() -1)
        logging.debug(self.parent_record)
        self.type_id = self.parent_record.value(0) 
        self.model.setFilter("type_id = "+str(self.type_id))

        self.title_label = QLabel(
            "Contenu type d'une malle "+self.parent_record.value(1))

        self.products_table = QTableView()
        self.products_table.setModel(self.model)
        self.products_table.setItemDelegate(QSqlRelationalDelegate())

        self.add_button = QPushButton('+')
        self.finish_button = QPushButton('Terminé')
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.products_table)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.finish_button)
        self.layout.addLayout(buttons_layout)
        self.setLayout(self.layout)
        
        self.add_button.clicked.connect(self.add_row)
        self.finish_button.clicked.connect(self.terminated)
        
    def submit_row(self):
        submited = self.model.submitAll()
        if not submited:
            error = self.model.lastError()
            logging.warning(error.text())
            if error.nativeErrorCode() == '23505':
                QMessageBox.warning(
                    self, "Erreur", "Ce produit semble déjà exister pour cette malle")
            elif error.nativeErrorCode() == '23502':
                QMessageBox.warning(
                    self, "Erreur", "Êtes-vous sûr(e) d'avoir entré un produit?")
            return False
        else:
            return True
    
    def add_row(self):
        if self.model.isDirty():
            submited = self.submit_row()
        inserted = self.model.insertRow(self.model.rowCount())
        record = self.model.record()
        record.setValue('type_id', self.type_id)
        record_is_set = self.model.setRecord(self.model.rowCount() -1, record)
        if not inserted:
            logging.warning(
                'Row not inserted in model {0}'.format(self.model))

    def terminated(self):
        if self.model.isDirty():
            submited = self.submit_row()
            if not submited:
                return False
        self.close()

