#!/usr/bin/python3
# -*- coding: utf-8 -*- 

from PyQt5.QtWidgets import (
    QDialog, QLineEdit, QTextEdit, QDateEdit, QPushButton, QDataWidgetMapper, 
    QFormLayout, QGridLayout, QDialogButtonBox, QMessageBox, QComboBox, 
    QSpinBox, QDoubleSpinBox, QTableView, QAbstractItemView, QHBoxLayout, 
    QVBoxLayout, QLabel, QWidget, QStyledItemDelegate)
from PyQt5.QtCore import QDate, QByteArray, QSize, QModelIndex
from validators import EmailValidator, PhoneValidator, CPValidator
from PyQt5.QtGui import QIntValidator, QIcon
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
        
        self.model = model
        self.parent = parent
        self.view = QTableView(self)
        self.view.setModel(model)
        self.view.setItemDelegate(QSqlRelationalDelegate())

        close_button = QPushButton('Fermer')

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(close_button)
        self.setLayout(layout)
        self.setMinimumSize(500, 400)

        close_button.clicked.connect(self.accept)

class RowEditDialog(DisplayTableViewDialog):
    def __init__(self, parent, model):
        super().__init__(parent, model)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.view.doubleClicked.connect(self.edit_row)

class MallesDialog(RowEditDialog):
    def __init__(self, parent, model):
        super().__init__(parent, model)
        self.exec_()

    def edit_row(self, index):
        reference = self.model.data(self.model.index(index.row(), 0))
        ContenuMalle(self, self.parent.models.contenu_malles, reference)

class MallesTypesDialog(RowEditDialog):
    def __init__(self, parent, model):
        super().__init__(parent, model)
        self.view.hideColumn(0) # hide id
        self.exec_()

    def edit_row(self, index):
        type_id = self.model.data(self.model.index(index.row(), 0))
        denomination = self.model.data(self.model.index(index.row(), 1))
        ContenuType(self, self.parent.models.contenu_type, type_id, denomination)

class MappedQDialog(QDialog):
    """ Abstract class for inputs forms views """
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

        self.widgets['email'].setValidator(EmailValidator)
        self.widgets['phone'].setValidator(PhoneValidator)

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
    def __init__(self, parent, model, fournisseurs_model):
        super(AddProduct, self).__init__(parent, model)

        self.widgets['nom'] = QLineEdit()
        self.widgets['fournisseur_id'] = QComboBox()
        self.widgets['fournisseur_id'].setModel(fournisseurs_model)
        self.widgets['fournisseur_id'].setModelColumn(1)
        add_fournisseur_button = QPushButton('+')

        self.mapper.setItemDelegate(QSqlRelationalDelegate(self))

        self.mapper.addMapping(self.widgets['nom'], 1)
        self.mapper.addMapping(self.widgets['fournisseur_id'], 2)
        
        self.layout = QFormLayout(self)
        self.layout.addRow('Nom', self.widgets['nom'])
        fournisseur_layout = QHBoxLayout()
        fournisseur_layout.addWidget(self.widgets['fournisseur_id'])
        fournisseur_layout.addWidget(add_fournisseur_button)
        self.layout.addRow('Fournisseur', fournisseur_layout)

        add_fournisseur_button.clicked.connect(parent.add_fournisseur)
        self.auto_default_buttons()
        self.add_row()
        self.exec_()

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
        self.widgets['price'] = QDoubleSpinBox()
        self.widgets['quantity'] = QSpinBox()

        add_fournisseur_button = QPushButton('+')
        add_produit_button = QPushButton('+')
        add_fournisseur_button.clicked.connect(self.add_new_fournisseur)
        add_produit_button.clicked.connect(self.add_new_produit)

        self.widgets['date_achat'].setDate(QDate.currentDate())

        f_index = self.model.fieldIndex('fournisseur_id') #fails
        self.fournisseur_model = self.model.relationModel(1) #fournisseur_id col
        self.produit_model = self.model.relationModel(2) #produit_id col

        self.widgets['fournisseur_id'].setModel(self.fournisseur_model)
        self.widgets['fournisseur_id'].setModelColumn(
            self.fournisseur_model.fieldIndex('nom'))
        self.widgets['produit_id'].setModel(self.produit_model)
        self.widgets['produit_id'].setModelColumn(
            self.produit_model.fieldIndex('nom'))

        self.mapper.setItemDelegate(QSqlRelationalDelegate(self))

        # We set the mapping by number col because fiedIndex method fails
        self.mapper.addMapping(self.widgets['fournisseur_id'], 1)
        self.mapper.addMapping(self.widgets['produit_id'], 2)
        self.mapper.addMapping(self.widgets['date_achat'], 3)
        self.mapper.addMapping(self.widgets['price'], 4)
        self.mapper.addMapping(self.widgets['quantity'], 5)
        
        for key, widget in self.widgets.items():
            if self.mapper.mappedSection(widget) == -1:
                logging.warning(key+' is not mapped.')

        self.layout = QFormLayout(self)
        fournisseur_layout = QHBoxLayout()
        fournisseur_layout.addWidget(self.widgets['fournisseur_id'])
        fournisseur_layout.addWidget(add_fournisseur_button)
        product_layout = QHBoxLayout()
        product_layout.addWidget(self.widgets['produit_id'])
        product_layout.addWidget(add_produit_button)

        self.layout.addRow('Fournisseur', fournisseur_layout)
        self.layout.addRow('Produit', product_layout)
        self.layout.addRow("Date d'achat", self.widgets['date_achat'])
        self.layout.addRow("Prix unitaire", self.widgets['price'])
        self.layout.addRow("Quantité", self.widgets['quantity'])

        self.auto_default_buttons()
        self.add_row()
        self.exec_()

    def add_new_fournisseur(self):
        model = self.parentWidget().models.fournisseurs
        result = AddFournisseur(self, model).result()
        if result:
            self.fournisseur_model.select()
            self.widgets['fournisseur_id'].setCurrentIndex(
                self.widgets['fournisseur_id'].count() - 1)

    def add_new_produit(self):
        model = self.parentWidget().models.produits
        result = AddProduct(self, model).result()
        logging.debug(result)
        if result:
            self.produit_model.select()
            combo_box = self.widgets['produit_id']
            combo_box.setCurrentIndex(combo_box.count() - 1)

    def submited(self):
        submited = self.mapper.submit()
        if submited:
            self.model.select()
            logging.info("L'entrée a bien été enregistrée")
            self.submit_vstock()
            self.accept()
        if not submited:
            db_error = self.model.lastError()
            last_query = self.model.query().lastError().type()
            logging.debug(db_error)
            if db_error:
                logging.warning(self.model.tableName()+' '+db_error.text())
            QMessageBox.warning(self, "Erreur", "L'enregistrement a échoué")

    def submit_vstock(self):
        model = self.parentWidget().models.contenu_malles
        combobox = self.widgets['produit_id']
        row = combobox.currentIndex()
        model_index = combobox.model().index(row, 0)
        product_id = combobox.model().data(model_index)

        quantity = self.widgets['quantity'].value()
        self.model.fill_stock(product_id, quantity)

class AddMalle(MappedQDialog):
    def __init__(self, parent, model, malles_type_model):
        super(AddMalle, self).__init__(parent, model)

        self.contenu_malles_model = parent.models.contenu_malles

        self.widgets['reference'] = QLineEdit()
        self.widgets['type_id'] = QComboBox()

        self.widgets['type_id'].setModel(malles_type_model)
        self.widgets['type_id'].setModelColumn(
            malles_type_model.fieldIndex('denomination'))
        
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
            contenu = ContenuMalle(
                self,
                self.contenu_malles_model,
                self.widgets['reference'].text())
        else:
            logging.warning(self.model.lastError().text())
            if error.nativeErrorCode() == '23505':
                QMessageBox.warning(
                    self, "Erreur", "Cette référence existe déjà.")

class ContenuMalle(QDialog):
    def __init__(self, parent, model, malle_ref=None):
        super(ContenuMalle, self).__init__(parent)
        
        self.model = model
        self.model.select()
        self.malle_ref = malle_ref
        self.model.setFilter("malle_ref = '"+str(malle_ref)+"'")

        self.title_label = QLabel("Contenu de la malle " + str(malle_ref))

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

        self.exec_()
        
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
            type_id = self.model.record(self.model.rowCount() -1).value(0)
            self.products = ContenuType(
                self,
                self.contenu_type_model,
                type_id,
                self.widgets['denomination'].text())
        else:
            error = self.model.lastError()
            logging.warning(error.text())
            if error.nativeErrorCode() == '23505':
                QMessageBox.warning(
                    self, "Erreur", "Cette malle type semble déjà exister")

class ContenuType(QDialog):
    def __init__(self, parent, model, type_id=None, denomination=None):
        super().__init__(parent)

        self.model = model
        self.model.select()
        self.type_id = type_id
        self.model.setFilter("type_id = "+str(type_id))

        self.title_label = QLabel(
            "Contenu type d'une malle "+ denomination)

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

        self.exec_()
        
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

class SejourForm(MappedQDialog):
    def __init__(self, parent, model, lieux_model):
        super().__init__(parent, model)
        
        self.widgets['nom'] = QLineEdit()
        self.widgets['lieu_id'] = QComboBox()
        self.widgets['directeur'] = QLineEdit()
        self.widgets['nbr_enfants'] = QSpinBox()
        self.widgets['observation'] = QTextEdit()
        add_lieu_button = QPushButton('+')
        
        self.widgets['lieu_id'].setModel(lieux_model)
        self.widgets['lieu_id'].setModelColumn(1) #nom
        
        self.mapper.setItemDelegate(QSqlRelationalDelegate(self))
        
        self.mapper.addMapping(
            self.widgets['observation'],
            5,
            QByteArray(b'plainText')) #because default is tohtml
        self.mapper.addMapping(self.widgets['nom'], 1)
        self.mapper.addMapping(self.widgets['lieu_id'], 2)
        self.mapper.addMapping(self.widgets['directeur'], 3)
        self.mapper.addMapping(self.widgets['nbr_enfants'], 4)
        
        self.layout = QFormLayout(self)
        lieu_layout = QHBoxLayout()
        lieu_layout.addWidget(self.widgets['lieu_id'])
        lieu_layout.addWidget(add_lieu_button)
        self.layout.addRow('Nom du séjour', self.widgets['nom'])
        self.layout.addRow('Lieu', lieu_layout)
        self.layout.addRow('Nom du directeur', self.widgets['directeur'])
        self.layout.addRow("Nombre d'enfants", self.widgets['nbr_enfants'])
        self.layout.addRow("Observations", self.widgets['observation'])
        
        add_lieu_button.clicked.connect(parent.add_lieu)

        self.auto_default_buttons()
        self.add_row()
        self.exec_()

    def submited(self):
        submited = self.mapper.submit()
        self.model.submitAll()
        logging.debug(self.model.lastError().text())
        if submited:
            self.model.select()
            logging.info('Sejour added.')
            self.accept()

class ContenuCheckerDialog(QDialog):
    def __init__(self, parent, models):
        super().__init__()

        self.models = models
        filter_combobox = QComboBox()
        filter_combobox.setModel(models.malles)
        self.model = models.contenu_checker
        self.view = QTableView()
        self.view.setModel(self.model)
        etat_delegate = EtatDelegate(self)
        self.view.setItemDelegateForColumn(5, etat_delegate)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(filter_combobox)
        self.layout.addWidget(self.view)

        self.setMinimumSize(550, 500)

        filter_combobox.currentTextChanged.connect(self.set_filter)
        self.set_filter(filter_combobox.currentText())

    def set_filter(self, reference):
        logging.debug('reference:'+str(reference))
        self.model.setFilter("malle_ref = '" + reference + "'")

class LieuForm(MappedQDialog):
    def __init__(self, parent, model):
        super().__init__(parent, model)

        self.widgets['nom'] = QLineEdit()
        self.widgets['ville'] = QLineEdit()
        self.widgets['cp'] = QLineEdit()
        self.widgets['numero'] = QLineEdit()
        self.widgets['rue'] = QLineEdit()

        self.widgets['cp'].setValidator(CPValidator) 
        self.widgets['numero'].setValidator(QIntValidator()) 

        self.init_add_dialog()
       
    def submited(self):
        submited = self.mapper.submit()
        self.model.submitAll()
        if submited:
            self.accept()
        else:
            logging.warning(self.model.lastError().text())


class EtatDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, opt, index):
        super().paint(painter, opt, index)

    def createEditor(self, parent, option, index):
        logging.debug(index)
        editor = QComboBox(parent)
        editor.setModel(index.model().etats_model)
        editor.setModelColumn(1)
        return editor

    def setModelData(self, editor, model, index):
        idx = editor.model().index(editor.currentIndex(), 0)
        model.setData(index, editor.model().data(idx), None)


