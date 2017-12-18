#!/usr/bin/python3
# -*- coding: utf-8 -*- 

"""
Diabolik Stock | QT Views
"""

from PyQt5.QtWidgets import (
    QDialog, QLineEdit, QTextEdit, QDateEdit, QPushButton, QDataWidgetMapper, 
    QFormLayout, QGridLayout, QDialogButtonBox, QMessageBox, QComboBox, 
    QSpinBox, QDoubleSpinBox, QTableView, QAbstractItemView, QHBoxLayout, 
    QVBoxLayout, QLabel, QWidget, QStyledItemDelegate, QCalendarWidget,
    QItemDelegate, QToolButton, QGroupBox, QCheckBox)
from PyQt5.QtCore import (
    QDate, QDateTime, QByteArray, QSize, Qt, QVariant, QSortFilterProxyModel, 
    QMessageAuthenticationCode)
from validators import EmailValidator, PhoneValidator, CPValidator, PortValidator
from PyQt5.QtGui import QIntValidator, QIcon
from PyQt5.QtSql import QSqlRelationalDelegate
from collections import OrderedDict
from utils import displayed_error
import string
import random
import logging

class UserConnect(QDialog):
    def __init__(self, parent, model):
        super().__init__(parent)
        self.setWindowTitle('Connection')
        self.model = model
        self.model.setFilter('')
        self.acl_group = None
        if self.model.rowCount() == 0:
            res = QMessageBox.question(
                    self,
                    'Aucun utilisateur',
                    "Il n'y a aucun utilisateur dans la base de donnée. "\
                    + "Faut-il en créer un ?")
            if res:
                UserDialog(
                        self,
                        parent.models.users)
        self.user = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(2)
        ok_button = QPushButton('OK')
        cancel_button = QPushButton('Annuler')
        layout = QFormLayout()
        layout.addRow('utilisateur', self.user)
        layout.addRow('mot de passe', self.password)
        layout.addWidget(ok_button)
        layout.addWidget(cancel_button)
        ok_button.clicked.connect(self.connect)

        self.setLayout(layout)
        self.exec_()

    def get_user(self):
        return self.user.text(), self.acl_group

    def connect(self):
        self.model.setFilter("name = '" + self.user.text() + "'")
        if not self.model.rowCount():
            QMessageBox.warning(
                self,
                'Erreur',
                "L'utilisateur " + self.user.text() + " n'existe pas.")
            return False
        user_id = self.model.data(self.model.index(0, 0))
        salt = self.model.data(self.model.index(0, 3))
        model_hash = self.model.data(self.model.index(0,4))
        code = QMessageAuthenticationCode(6, QByteArray(salt.encode()))
        code.addData(QByteArray(self.password.text().encode()))
        given_hash = str(code.result().toHex().data(), encoding='utf-8')
        if given_hash == model_hash:
            logging.debug('authentication succed!')
            self.acl_group = self.model.get_groups(user_id)
            #group_string = self.model.data(self.model.index(0, 5))
            #self.acl_group = [int(i) for i in group_string.split(',')]
            self.accept()
        else:
            logging.debug('wrong')
            QMessageBox.warning(self, 'Erreur', "Mauvais mot de passe") 
            return False 

class HCloseDialog(QDialog):
    """ wrap a DisplayTableView into QDialog """
    def __init__(self, parent, widget):
        super().__init__(parent)

        self.main_widget = widget
        self.setWindowTitle(self.main_widget.windowTitle())
        self.close_button = QPushButton('Fermer')

        layout = QVBoxLayout(self)
        layout.addWidget(widget)

        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.close_button)
        layout.addLayout(self.button_layout)

        self.close_button.clicked.connect(self.accept)

class HSaveDialog(HCloseDialog):
    def __init__(self, parent, widget):
        super().__init__(parent, widget)
        
        save_button = QPushButton('Enregistrer')
        self.close_button.setText('Annuler')
        self.button_layout.addWidget(save_button)
        save_button.clicked.connect(self.save_and_quit)
        self.close_button.clicked.connect(self.revert_and_quit)
    
    def save_and_quit(self):
        submited = self.main_widget.model.submitAll()
        if not submited:
            error = self.model.lastError()
            logging.warning(error.text())
            QMessageBox.warning(self, "Erreur", error.text())
        self.accept()

    def revert_and_quit(self):
        self.main_widget.model.revertAll()
        self.close()

class ConfigDialog(QDialog):
    def __init__(self, parent, settings):
        super().__init__(parent)

        self.setWindowTitle('Configuration')
        self.settings = settings
        self.db_hostname = QLineEdit()
        self.db_name = QLineEdit()
        self.db_port = QLineEdit()
        self.db_user = QLineEdit()
        self.db_password = QLineEdit()
        self.auto_stock = QCheckBox()
        self.ok_button = QPushButton('OK')
        self.cancel_button = QPushButton('Annuler')
        self.db_port.setValidator(PortValidator)
        self.db_password.setEchoMode(2) # stars replace chars

        self.ok_button.clicked.connect(self.write_and_quit)
        self.cancel_button.clicked.connect(self.close)

        db_group = QGroupBox('Base de donnée')
        db_layout = QFormLayout()
        db_layout.addRow("Nom d'hôte", self.db_hostname)
        db_layout.addRow("Nom de la base", self.db_name)
        db_layout.addRow("Port", self.db_port)
        db_layout.addRow("Utilisateur", self.db_user)
        db_layout.addRow("Mot de passe", self.db_password)
        db_layout.addRow("Stock automatique", self.auto_stock)
        db_group.setLayout(db_layout)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(db_group)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        self.read_settings()
        self.exec_()

    def read_settings(self):
        """ read settings and populate widgets """
        self.db_hostname.setText(self.settings.value('db/host'))
        self.db_name.setText(self.settings.value('db/name'))
        self.db_port.setText(str(self.settings.value('db/port')))
        self.db_user.setText(self.settings.value('db/user'))
        self.db_password.setText(self.settings.value('db/password'))
        if self.settings.value('autostock'):
            if self.settings.value('autostock') == 'true':
                self.auto_stock.setChecked(True)
            if self.settings.value('autostock') == 'false':
                self.auto_stock.setChecked(False)
        
    def write_and_quit(self):
        self.settings.setValue('db/host', self.db_hostname.text())
        self.settings.setValue('db/name', self.db_name.text())
        self.settings.setValue('db/port', int(self.db_port.text()))
        self.settings.setValue('db/user', self.db_user.text())
        self.settings.setValue('db/password', self.db_password.text())
        self.settings.setValue('autostock', self.auto_stock.isChecked())
        self.parent().init_config()
        self.accept()

class DisplayTableView(QWidget):
    def __init__(self, parent, model):
        QWidget.__init__(self, parent)
        
        self.model = model
        self.view = QTableView()
        self.proxy = QSortFilterProxyModel()
        self.proxy.setSourceModel(model)
        self.view.setModel(self.proxy)
        self.view.setSortingEnabled(True)
        self.view.setItemDelegate(QSqlRelationalDelegateBehindProxy())
        
        self.parent = parent

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        buttons_layout = QHBoxLayout()
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        self.setMinimumSize(500, 400)

class RowEdit(DisplayTableView):
    def __init__(self, parent, model):
        super().__init__(parent, model)
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.view.doubleClicked.connect(self.edit_row)

        add_button = QPushButton('+')
        remove_button = QPushButton('-')

        button_layout = QHBoxLayout()
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        self.layout().insertLayout(1, button_layout)

        add_button.clicked.connect(self.add_row)
        remove_button.clicked.connect(self.remove_row)

    def remove_row(self):
        select = self.view.selectionModel()
        row = select.currentIndex().row()
        removed = self.proxy.removeRow(row)
        if removed:
            logging.debug(
                "removed row in " + str(self.model) + " : " + str(row))
            self.model.submitAll()
        if not removed:
            logging.debug(self.model.lastError().text())

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
            if type(widget) == QTextEdit: # because it needs specific property
                self.mapper.addMapping(
                    widget,
                    self.model.fieldIndex(field),
                    QByteArray(b'plainText')) 
            else:
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

class UsersArray(RowEdit):
    def __init__(self, parent, users_model):
        super().__init__(parent, users_model)

        self.setWindowTitle('Utilisateurs')
        self.view.setColumnHidden(0, True) #id
        self.view.setColumnHidden(3, True) #password salt
        self.view.setColumnHidden(4, True) #password hash
        self.model.setFilter('')

    def edit_row(self, index):
        idx = self.proxy.mapToSource(index)
        UserDialog(self.parent, self.model, idx) 
    
    def add_row(self):
        UserDialog(self.parent, self.model)

    def remove_row(self):
        reply = QMessageBox.question(
            None, 'Sûr(e) ?', "Vous allez détruire définitivement cet "\
            + "utilisateur. Êtes-vous sûr(e) ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)
        if reply == QMessageBox.No:
            return False
        super().remove_row()
        self.model.submitAll()

class UserDialog(QDialog):
    def __init__(self, parent, users_model, index=None):
        super().__init__(parent)

        self.setWindowTitle('Utilisateur')
        self.model = users_model

        name = QLineEdit()
        email = QLineEdit()
        self.password = QLineEdit()
        self.password_repeat = QLineEdit()
        self.group = QComboBox()
        self.group.addItems(['administrateur', 'utilisateur'])

        email.setValidator(EmailValidator)
        self.password.setEchoMode(2) # stars replace chars
        self.password_repeat.setEchoMode(2) # stars replace chars

        self.mapper = QDataWidgetMapper(self)
        self.mapper.setModel(self.model)
        self.mapper.addMapping(name, 1)
        self.mapper.addMapping(email, 2)
        #self.mapper.addMapping(self.group, 5, QByteArray(b'currentIndex'))
        
        self.layout = QFormLayout(self)
        self.layout.addRow('Nom', name)
        self.layout.addRow('Email', email)
        self.layout.addRow('Mot de passe', self.password)
        self.layout.addRow('Vérification', self.password_repeat)
        self.layout.addRow('Groupe', self.group)
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            self)
        buttons.accepted.connect(self.submited)
        buttons.rejected.connect(self.close)
        self.layout.addRow(buttons)

        if index:
            self.mapper.setCurrentIndex(index.row())
        else:
            inserted = self.model.insertRow(self.model.rowCount())
            self.mapper.toLast()

        self.exec_()

    def submited(self):
        if self.password.text() != self.password_repeat.text():
            QMessageBox.warning(self, 'Erreur', 'Les mots de passes ne sont '\
            + 'pas identiques.')
            return False
        salt = ''.join(random.choice(string.ascii_letters) for _ in range(32))
        code = QMessageAuthenticationCode(6, QByteArray(salt.encode()))
        code.addData(QByteArray(self.password.text().encode()))
        hash_ = str(code.result().toHex().data(), encoding='utf-8')
        self.model.setData(self.model.index(self.model.rowCount() -1, 3), salt) 
        self.model.setData(
            self.model.index(self.model.rowCount() -1, 4), str(hash_))
        mapper_submited = self.mapper.submit()
        submited = self.model.submitAll()
        if submited:
            user_id = self.model.data(
                self.model.index(self.model.rowCount() -1, 0))
            group_id = self.group.currentIndex() + 1
            self.model.set_group(user_id, group_id)
        self.accept()

class MallesArray(RowEdit):
    def __init__(self, parent, model):
        super().__init__(parent, model)
        self.setWindowTitle('Malles')
        self.resize(750, 400)
        self.parent = parent

    def add_row(self):
        self.parent.add_malle()
        self.model.select()

    def edit_row(self, index):
        idx = self.proxy.mapToSource(index)
        MalleFormWithContenu(
            self.parent, 
            self.parent.models.malles,
            self.parent.models,
            idx)

    def remove_row(self):
        reply = QMessageBox.question(
            None, 'Sûr(e) ?', "Vous allez détruire définitivement cette malle, "\
            + "ainsi que son contenu. Êtes-vous sûr(e) ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)
        if reply == QMessageBox.No:
            return False
        super().remove_row()
        res = self.model.submitAll()
        logging.debug(res)

class CategoriesArray(RowEdit):
    def __init__(self, parent, model):
        super().__init__(parent, model)
        self.setWindowTitle('Categories')
        self.view.setColumnHidden(0, True)
        self.view.setEditTriggers(QAbstractItemView.AllEditTriggers)
        self.view.setSelectionBehavior(QAbstractItemView.SelectItems)

    def edit_row(self, index):
        pass

    def add_row(self, index):
        self.model.insertRow(self.model.rowCount())

    def submit_and_close(self):
        submited = self.model.submitAll()
        if submited:
            self.close()

class LieuxArray(RowEdit):
    def __init__(self, parent, model):
        super().__init__(parent, model)
        self.setWindowTitle('Lieux')
        self.parent = parent

    def edit_row(self, index):
        idx = self.proxy.mapToSource(index)
        LieuForm(None, self.parent.models.lieux, idx) 

    def add_row(self):
        LieuForm(None, self.parent.models.lieux)

class MallesTypes(RowEdit):
    def __init__(self, parent, model):
        super().__init__(parent, model)
        self.setWindowTitle('Malles Types')
        self.view.hideColumn(0) # hide id

    def add_row(self):
        self.parent.add_malle_type()
        self.model.select()

    def edit_row(self, index):
        idx = self.proxy.mapToSource(index)
        type_id = idx.model().data(idx.model().index(idx.row(), 0))
        denomination = self.model.data(self.model.index(idx.row(), 1))
        ContenuType(self, self.parent.models.contenu_type, type_id, denomination)

    def remove_row(self):
        reply = QMessageBox.question(
            None, 'Sûr(e) ?', "À priori, vous n'avez pas à détruire un type. "\
            + "Ne répondez oui que si vous savez exactement ce que vous "\
            + "faîtes. Voulez-vous vraiment détruire un type, ainsi que tout "\
            + "le contenu type associé ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)
        if reply == QMessageBox.No:
            return False
        
        # I don't use inherited method because the proxy seems to fail calling
        # overrided removeRow() model's method...
        select = self.view.selectionModel()
        row = self.proxy.mapToSource(select.currentIndex()).row()
        removed = self.model.removeRow(row)
        if not removed:
            error = self.model.lastError()
            logging.warning(error.text())
            QMessageBox.warning(self, "Erreur", error.text())

class ProduitsArray(RowEdit):
    def __init__(self, parent, model):
        super().__init__(parent, model)
        self.setWindowTitle('Produits')

    def add_row(self):
        ProductForm(
            self.parent,
            self.parent.models.produits,
            self.parent.models.fournisseurs)
        self.model.select()

    def edit_row(self, index):
        idx = self.proxy.mapToSource(index)
        ProductForm(
            self.parent,
            self.parent.models.produits,
            self.parent.models.fournisseurs,
            index = idx)
        self.model.select()

    def remove_row(self):
        reply = QMessageBox.question(
            None, 'Que souhaitez-vous faire ? ', "Vous ne pouvez pas détruire "\
            + "un produit. Voulez-vous mettre sa quantité en stock à 0 ? ",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)
        if reply == QMessageBox.Yes:
            select = self.view.selectionModel()
            row = select.currentIndex().row()
            self.model.setData(self.model.index(row, 3), 0)
            self.model.submitAll()

class Fournisseur(MappedQDialog):
    def __init__(self, parent, model):
        super(Fournisseur, self).__init__(parent, model)

        self.setWindowTitle('Fournisseurs')
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

class ProductForm(MappedQDialog):
    def __init__(self, parent, model, fournisseurs_model, index=None):
        super().__init__(parent, model)

        self.setWindowTitle('Produit')
        self.widgets['nom'] = QLineEdit()
        self.widgets['fournisseur_id'] = QComboBox()
        self.widgets['fournisseur_id'].setModel(fournisseurs_model)
        self.widgets['fournisseur_id'].setModelColumn(1)

        add_fournisseur_button = QPushButton('+')

        self.mapper.setItemDelegate(QSqlRelationalDelegateWithNullValues(self))

        self.mapper.addMapping(self.widgets['nom'], 1)
        self.mapper.addMapping(self.widgets['fournisseur_id'], 2)
        
        self.layout = QFormLayout(self)
        self.layout.addRow('Nom', self.widgets['nom'])
        fournisseur_layout = QHBoxLayout()
        fournisseur_layout.addWidget(self.widgets['fournisseur_id'])
        fournisseur_layout.addWidget(add_fournisseur_button)
        self.layout.addRow('Fournisseur \npar défaut', fournisseur_layout)

        add_fournisseur_button.clicked.connect(self.add_fournisseur)
        self.auto_default_buttons()
        if index:
            self.widgets['stock_qty'] = QSpinBox()
            self.mapper.addMapping(self.widgets['stock_qty'], 3)
            self.layout.insertRow(2, 'Quantité', self.widgets['stock_qty'])
            self.mapper.setCurrentIndex(index.row())
        else:
            self.add_row()
        self.exec_()

    def add_fournisseur(self):
        self.parent().add_fournisseur()
        self.model.relationModel(2).select()

    def submited(self):
        submited = self.mapper.submit()
        if submited:
            logging.info('produit added.')
            self.accept()
        else:
            displayed_error(self.model.lastError())

class QSqlRelationalDelegateWithNullValues(QSqlRelationalDelegate):
    """ Delegate for storing NULL value in database when no data (instead of 
    empty string) in 'reference' field """
    
    def setModelData(self, editor, model, index):
        if index.column() == 3 and ''.join(editor.text().split()) == '':
            model.setData(index, QVariant()) #QVariant() means NULL value in db 
        elif index.column() == 1:
            data = editor.text().lower()
            model.setData(index, data)
        else:
            super().setModelData(editor, model, index)

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
        models = self.parentWidget().models
        result = ProductForm(
            self.parentWidget(), 
            models.produits, 
            models.fournisseurs).result()
        logging.debug(result)
        if result:
            self.produit_model.select()
            combo_box = self.widgets['produit_id']
            combo_box.setCurrentIndex(combo_box.count() - 1)

    def submited(self):
        submited = self.mapper.submit()
        if submited:
            self.model.submitAll()
            logging.info("L'entrée a bien été enregistrée")
            self.accept()
        if not submited:
            db_error = self.model.lastError()
            if db_error:
                logging.warning(self.model.tableName()+' '+db_error.text())
            QMessageBox.warning(self, "Erreur", "L'enregistrement a échoué")

class InputsArray(RowEdit):
    def __init__(self, parent, model):
        super().__init__(parent, model)
        self.setWindowTitle('Arrivages')
        self.view.setColumnHidden(0, True)
        self.resize(680, 376)

    def edit_row(self, index):
        pass

    def add_row(self, index):
        AddInputArray(self.parent, self.model)

class FilterFournisseurDateProxyModel(QSortFilterProxyModel):
    """ Custom proxy to filter by fournisseur and date """
    def __init__(self):
        super().__init__()
        self.date = ''
        self.fournisseur = ''

    def filterAcceptsRow(self, sourceRow, index):
        model = self.sourceModel()
        date = model.data(model.index(sourceRow, 3))
        # below : because this method is called at model submit 
        # (failed with None date value)
        if date:  
            date = date.toString('yyyy-MM-dd')
        f_true = self.fournisseur == model.data(model.index(sourceRow, 1))
        d_true = self.date == date 
        return not False in [f_true, d_true]

    def set_date_filter(self, date):
        self.date = date
        self.invalidateFilter()

    def set_fournisseur_filter(self, fournisseur):
        self.fournisseur = fournisseur
        self.invalidateFilter()

class AddInputArray(QDialog):
    def __init__(self, parent, model):
        super().__init__(parent)
        self.model = model

        self.calendar = QCalendarWidget()
        self.fournisseur = QComboBox()
        self.fournisseur.setModel(parent.models.fournisseurs)
        self.fournisseur.setModelColumn(1)

        self.table = QTableView()

        # We choose to subclass QSortProxyModel to have 2 different 
        # filters. An other (simpler) way is to chain 2 instances, but it is not
        # possible here because of the QSqlRelationaldelegate.
        self.proxy_model = FilterFournisseurDateProxyModel()
        self.proxy_model.setSourceModel(model)
        self.table.setModel(self.proxy_model)
        self.table.setItemDelegate(QSqlRelationalDelegateBehindProxy())
        
        self.table.setColumnHidden(0, True) # id
        self.table.setColumnHidden(1, True) # fournisseur
        self.table.setColumnHidden(3, True) # date
        self.add_button = QPushButton('+')
        self.remove_button = QPushButton('-')
        self.finish_button = QPushButton('Terminé')

        layout = QVBoxLayout()
        head_layout = QHBoxLayout()
        head_layout.addWidget(self.calendar)
        head_layout.addWidget(self.fournisseur)
        layout.addLayout(head_layout)
        layout.addWidget(self.table)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.remove_button)
        buttons_layout.addWidget(self.finish_button)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        self.add_button.clicked.connect(self.add_row)
        self.remove_button.clicked.connect(self.remove_row)
        self.finish_button.clicked.connect(self.terminated)
        self.fournisseur.currentTextChanged.connect(self.set_fournisseur_filter)
        self.calendar.selectionChanged.connect(self.set_date_filter)

        self.set_date_filter()
        self.set_fournisseur_filter()

        self.exec_()

    def set_fournisseur_filter(self):
        self.proxy_model.set_fournisseur_filter(self.fournisseur.currentText())

    def set_date_filter(self):
        date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        self.proxy_model.set_date_filter(date)

    def add_row(self):
        if self.model.isDirty():
            submited = self.model.submitAll()
        inserted = self.model.insertRow(self.model.rowCount())
        if inserted: 
            row = self.fournisseur.currentIndex()
            idx = self.fournisseur.model().index(row, 0)
            id_ = idx.data()
            date_inserted = self.model.setData(
                self.model.index(self.model.rowCount() -1, 3),
                self.calendar.selectedDate())
            fournisseur_inserted = self.model.setData(
                self.model.index(self.model.rowCount() -1, 1),
                id_)
            if not date_inserted or not fournisseur_inserted:
                logging.warning(self.model.lastError().text())
        if not inserted:
            logging.warning(
                'Row not inserted in model {0}'.format(self.model))

    def remove_row(self):
        select = self.table.selectionModel()
        row = select.currentIndex().row()
        self.model.removeRow(row)
        self.model.submitAll()

    def terminated(self):
        submited = self.model.submitAll()
        if not submited:
            error = self.model.lastError()
            logging.warning(error.text())
        self.close()

class MalleForm(MappedQDialog):
    def __init__(self, parent, model, models, index=None):
        super().__init__(parent, model)

        self.setWindowTitle('Malle')
        self.contenu_malles_model = models.contenu_malles
        self.models = models
        self.malle_log_model = models.malle_log
        self.db = parent.db

        self.widgets['reference'] = QLineEdit()
        self.widgets['category_id'] = QComboBox()
        self.widgets['type_id'] = QComboBox()
        self.widgets['lieu_id'] = QComboBox() 
        self.widgets['section'] = QLineEdit()
        self.widgets['shelf'] = QLineEdit()
        self.widgets['slot'] = QLineEdit()
        self.widgets['observation'] = QTextEdit()
        add_lieu_button = QPushButton('+')

        self.widgets['type_id'].setModel(models.malles_types)
        self.widgets['type_id'].setModelColumn(
            models.malles_types.fieldIndex('denomination'))
        self.widgets['lieu_id'].setModel(models.lieux)
        self.widgets['lieu_id'].setModelColumn(
            models.lieux.fieldIndex('nom'))
        self.widgets['category_id'].setModel(models.categories)
        self.widgets['category_id'].setModelColumn(
            models.categories.fieldIndex('name'))
        
        self.mapper.setItemDelegate(MalleDelegate(self))
        
        for i, k in enumerate(self.widgets):
            #logging.debug(str(self.widgets[k]) + ' ' + str(i))
            if type(self.widgets[k]) == QTextEdit: # needs plainText property
                self.mapper.addMapping(
                    self.widgets[k],
                    i,
                    QByteArray(b'plainText'))
            else:
                self.mapper.addMapping(self.widgets[k], i) 
        
        form_layout_left = QFormLayout()
        form_layout_left.addRow('Référence', self.widgets['reference'])
        form_layout_left.addRow('Catégorie', self.widgets['category_id'])
        form_layout_left.addRow('Type', self.widgets['type_id'])
        lieu_layout = QHBoxLayout()
        lieu_layout.addWidget(self.widgets['lieu_id'])
        lieu_layout.addWidget(add_lieu_button)
        form_layout_left.addRow('Lieu', lieu_layout)
        form_layout_right = QFormLayout()
        form_layout_right.addRow('Allée', self.widgets['section'])
        form_layout_right.addRow('Étagère', self.widgets['shelf'])
        form_layout_right.addRow('Emplacement', self.widgets['slot'])
        layout = QHBoxLayout()
        layout.addLayout(form_layout_left)
        layout.addLayout(form_layout_right)
        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(self.widgets['observation'])
        self.widgets['observation'].setPlaceholderText('Observation')
        self.setLayout(main_layout)

        add_lieu_button.clicked.connect(self.add_lieu)

        if index:
            self.mapper.setCurrentIndex(index.row())
        else:
            self.add_row()

    def submited(self):
        submited = self.mapper.submit()
        if submited:
            submited = self.model.submitAll()
            if submited:
                self.model.select()
                self.accept()
                logging.info('Malle added.')
                contenu = ContenuMalle(
                    self,
                    self.contenu_malles_model,
                    self.db,
                    self.widgets['reference'].text())
            else:
                error = self.model.lastError()
                logging.warning(error.text())
                if error.nativeErrorCode() == '23505':
                    QMessageBox.warning(
                        self, "Erreur", "Cette référence existe déjà.")

        else:
            error = self.model.lastError()
            logging.debug(error.text())

    def add_lieu(self):
        self.parent().add_lieu()

        # below: To fix the just added lieu which doesn't want to be stored in the 
        # model if the relationModel doesn't contains it...
        self.model.relationModel(2).select()

class MalleFormDialog(MalleForm):
    def __init__(self, parent, model, models, index=None):
        super().__init__(parent, model, models, index)
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            self)
        buttons.accepted.connect(self.submited)
        buttons.rejected.connect(self.undo)
        self.layout().addWidget(buttons)

class MalleFormWithContenu(MalleForm):
    def __init__(self, parent, model, models, index=None):
        super().__init__(parent, model, models, index)
        logging.debug(index.row())
        malle_ref = model.data(model.index(index.row(), 0))
        logging.debug(parent)
        self.contenu_malle = ContenuMalle(
            parent, 
            models.contenu_malles, 
            parent.db,
            malle_ref)
        self.layout().addWidget(self.contenu_malle)
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            self)
        buttons.accepted.connect(self.submited)
        buttons.rejected.connect(self.undo)
        self.layout().addWidget(buttons)
        
        self.exec_()

class ContenuMalle(QWidget):
    def __init__(self, parent, model, db, malle_ref=None):
        super(ContenuMalle, self).__init__(parent)
        
        self.parent = parent
        self.model = model
        self.malle_log_model = parent.models.malle_log
        self.db = db
        self.model.select()
        self.malle_ref = malle_ref
        self.model.setFilter("malle_ref = '"+str(malle_ref)+"'")

        self.title_label = QLabel("Contenu de la malle " + str(malle_ref))
        self.malle_log_button = QPushButton("Journal d'entretien")

        self.products_table = QTableView()
        self.products_table.setModel(self.model)
        self.products_table.setItemDelegateForColumn(5, EtatDelegate()) 
        self.products_table.setColumnHidden(0, True)
        self.products_table.setColumnHidden(1, True)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.products_table)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.malle_log_button)
        self.layout.addLayout(buttons_layout)
        self.setLayout(self.layout)

        self.malle_log_button.clicked.connect(self.open_malle_log)
    
    def add_row(self, values=False):
        inserted = self.model.insertRow(self.model.rowCount())
        record = self.model.record()
        record.setValue('malle_ref', self.malle_ref)
        logging.debug(values)
        if values:
            record.setValue('nom', values['produit_id'])
            record.setValue('quantity', values['quantity'])
            record.setValue('etat', 1)
        record.setGenerated('id', False)
        record_is_set = self.model.setRecord(self.model.rowCount() -1, record)
        if not inserted:
            logging.warning(
                'Row not inserted in model {0}'.format(self.model))

    def remove_row(self):
        select = self.products_table.selectionModel()
        row = select.currentIndex().row()
        self.model.removeRow(row)
        self.model.submitAll()

    def open_malle_log(self):
        HSaveDialog(
            self, MalleLogArray(self, self.malle_log_model, self.malle_ref)).exec_()

class MalleLogArray(DisplayTableView):
    def __init__(self, parent, model, malle_ref):
        super().__init__(parent, model)

        self.setWindowTitle("Journal d'entretien")
        self.malle_ref = malle_ref

        self.view.hideColumn(0) # hide id
        self.view.hideColumn(2) # hide malle_ref
        model.setFilter("malle_ref = '" + malle_ref + "'")
        
        add_button = QPushButton('+')
        remove_button = QPushButton('-')

        button_layout = QHBoxLayout()
        button_layout.addWidget(add_button)
        button_layout.addWidget(remove_button)
        self.layout().insertLayout(1, button_layout)

        add_button.clicked.connect(self.add_row)
        remove_button.clicked.connect(self.remove_row)

    def add_row(self):
        def retrieve_current_user_id():
            user_model = self.parent.parent.models.users
            current_user = self.parent.parent.connected_user[0]
            return user_model.get_id_by_name(current_user)

        inserted = self.proxy.insertRow(self.proxy.rowCount())
        if inserted:
            user_id_inserted = self.model.setData(
                self.model.index(self.model.rowCount() -1, 1),
                retrieve_current_user_id())
            ref_inserted = self.model.setData(
                self.model.index(self.model.rowCount() -1, 2),
                self.malle_ref)
            datetime_inserted = self.model.setData(
                self.model.index(self.model.rowCount() -1, 3),
                QDateTime.currentDateTime())

    def remove_row(self):
        selected = self.view.selectionModel()
        row = selected.currentIndex().row()
        self.proxy.removeRow(row)

class ComboBoxCompleterDelegate(QSqlRelationalDelegate):
    def __init__(self, parent=None, relation_model=2):
        super().__init__(parent)
        self.relation_model = relation_model

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.setEditable(True)
        editor.setModel(index.model().relationModel(self.relation_model))
        editor.setModelColumn(1)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().relationModel(self.relation_model).data(index)
        if value:
            editor.setCurrentIndex(int(value))

class AddMalleType(MappedQDialog):
    def __init__(self, parent, model):
        super(AddMalleType, self).__init__(parent, model)

        self.contenu_type_model = parent.models.contenu_type
        self.widgets['denomination'] = QLineEdit()
        self.widgets['observation'] = QTextEdit()
        self.widgets['denomination'].setPlaceholderText('ex: Pédagogique')
        self.init_mapping()

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
            ContenuType(
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

        self.setWindowTitle('Contenu de la malle type')
        self.model = model
        self.model.select()
        self.type_id = type_id
        self.model.setFilter("type_id = "+str(type_id))

        self.title_label = QLabel(
            "Contenu type d'une malle "+ denomination)

        self.products_table = QTableView()
        self.products_table.setModel(self.model)
        self.products_table.setItemDelegate(QSqlRelationalDelegate())
        completer_delegate = ComboBoxCompleterDelegate(self)
        self.products_table.setItemDelegateForColumn(2, completer_delegate)
        self.products_table.setColumnHidden(0, True)
        self.products_table.setColumnHidden(1, True)

        self.add_button = QPushButton('+')
        self.remove_button = QPushButton('-')
        self.finish_button = QPushButton('Terminé')
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.products_table)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.remove_button)
        buttons_layout.addWidget(self.finish_button)
        self.layout.addLayout(buttons_layout)
        self.setLayout(self.layout)
        
        self.add_button.clicked.connect(self.add_row)
        self.remove_button.clicked.connect(self.remove_row)
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
        #if self.model.isDirty():
        #    submited = self.submit_row()
        inserted = self.model.insertRow(self.model.rowCount())
        record = self.model.record()
        record.setGenerated('id', False)
        record.setValue('type_id', self.type_id)
        record_is_set = self.model.setRecord(self.model.rowCount() -1, record)
        if not inserted:
            logging.warning(
                'Row not inserted in model {0}'.format(self.model))
    
    def remove_row(self):
        reply = QMessageBox.question(
            None, 'Sûr(e) ?', "Détruire un produit dans un type détruit "\
            + "également tous les produits contenus dans les malles de ce type. "\
            + "Êtes-vous sûr(e) ?", 
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)
        if reply == QMessageBox.No:
            return False
        select = self.products_table.selectionModel()
        row = select.currentIndex().row()
        self.model.removeRow(row)
        submited = self.model.submitAll()
        if not submited:
            logging.warning(self.model.lastError().text())

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

class LieuForm(MappedQDialog):
    def __init__(self, parent, model, index=None):
        super().__init__(parent, model)

        self.setWindowTitle('Lieu')
        self.widgets['nom'] = QLineEdit()
        self.widgets['ville'] = QLineEdit()
        self.widgets['cp'] = QLineEdit()
        self.widgets['numero'] = QLineEdit()
        self.widgets['rue'] = QLineEdit()

        self.widgets['cp'].setValidator(CPValidator) 
        self.widgets['numero'].setValidator(QIntValidator()) 

        self.init_mapping()
        self.auto_layout()
        self.auto_default_buttons()
        
        if index:
            self.mapper.setCurrentIndex(index.row())
        else:
            self.add_row()
        self.exec_()
       
    def submited(self):
        mapper_submited = self.mapper.submit()
        model_submited = self.model.submitAll()
        if mapper_submited and model_submited:
            self.accept()
        else:
            QMessageBox.warning(
                self,
                "Erreur",
                "Les informations sembles incorrectes.\n"\
                + "\ndétails de l'erreur:\n"\
                + self.model.lastError().text())
            logging.warning(self.model.lastError().text())

class ReservationForm(MappedQDialog):
    def __init__(self, parent, model):
        super().__init__(parent, model)

        self.setWindowTitle('Réservation')
        self.widgets['sejour_id'] = QComboBox()
        self.widgets['date_start'] = QCalendarWidget()
        self.widgets['date_stop'] = QCalendarWidget()
        self.widgets['observation'] = QTextEdit()

        self.widgets['sejour_id'].setModel(model.relationModel(1))
        self.widgets['sejour_id'].setModelColumn(1)
        self.mapper.setItemDelegate(QSqlRelationalDelegate(self))
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

class QSqlRelationalDelegateBehindProxy(QSqlRelationalDelegate):
    """ Magic delegate to have a QSqlRelationalDelegate behind a 
    QSortFilterProxyModel. Copied from https://stackoverflow.com/questions/28231773/qsqlrelationaltablemodel-with-qsqlrelationaldelegate-not-working-behind-qabstrac """
    def createEditor(self, parent, option, index):
        proxy = index.model()
        base_index = proxy.mapToSource(index)
        return super().createEditor(parent, option, base_index)

    def setEditorData(self, editor, index):
        proxy = index.model()
        base_index = proxy.mapToSource(index)
        return super().setEditorData(editor, base_index)

    def setModelData(self, editor, model, index):
        base_model = model.sourceModel()
        base_index = model.mapToSource(index)
        return super().setModelData(editor, base_model, base_index)

class MalleDelegate(QItemDelegate):
    """ Like QSqlRelationalDelegate behaviour """
    def setModelData(self, editor, model, index):
        if index.column() == 2 or index.column() == 1:
            idx = editor.model().index(editor.currentIndex(), 0)
            data = editor.model().data(idx)
            model.setData(index, data, Qt.EditRole)
        else:
            super().setModelData(editor, model, index)
