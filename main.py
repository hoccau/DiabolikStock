#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Diabolik Stock
Logiciel de gestion du matériel pour l'association Diabolo
"""

from PyQt5 import QtSql
from PyQt5.QtSql import QSqlRelationalDelegate
from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import (
    QApplication, qApp, QMainWindow, QAction, QMessageBox, QFileDialog,
    QInputDialog)
from PyQt5.QtGui import QIcon
from models import (
    Models, Malles, MallesTypesWithMalles, Fournisseurs, Inputs, Produits,
    Sejours)
from db import Query
from views import (
    MalleFormDialog, AddMalleType, AddInput, AddFournisseur, ProductForm, 
    StartupView, DisplayTableViewDialog, MallesArrayDialog, MallesTypesDialog, 
    SejourForm, LieuForm, ReservationForm, UsersArrayDialog, ConfigDialog, 
    ProduitsArrayDialog, InputsArray, LieuxArrayDialog, UserConnect)
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        
        self.initUI()

    def initUI(self):

        menubar = self.menuBar()
        self.setWindowTitle("Diabolik Stock")

        self.actions = {
            'exit':CtrlAction(
                QIcon(), '&Quitter', qApp.quit, 'Ctrl+Q', db_connected_required=False),
            'connect':CtrlAction(
                QIcon(), '&Connection', self.connect, 'Ctrl+C', admin_required=False),
            'disconnect':CtrlAction(
                QIcon(),
                '&Déconnection',
                self.disconnect_user,
                'Ctrl+D',
                db_connected_required=False,
                admin_required=False),
            'settings':CtrlAction(
                QIcon(),
                '&Configuration',
                self.set_config,
                '',
                db_connected_required=False,
                admin_required=False),
            'export_commandes':CtrlAction(
                QIcon(), '&Commandes', self.export_commandes),
            'export_checker': CtrlAction(
                QIcon(), '&Malle', self.export_checker),
            'export_xlsx_malles': CtrlAction(
                QIcon(), '&Type', self.export_xlsx_malles),
            'add_fournisseur': CtrlAction(
                QIcon(), '&Fournisseur', self.add_fournisseur),
            'add_produit': CtrlAction(QIcon(), '&Produit', self.add_product),
            'add_input': CtrlAction(QIcon(),'&Entrée de produit', self.add_input),
            'add_malle_type': CtrlAction(
                QIcon(),'&Malle type', self.add_malle_type),
            'add_malle': CtrlAction(QIcon(),'&Malle', self.add_malle),
            'add_sejour': CtrlAction(QIcon(),'&Séjour', self.add_sejour),
            'add_reservation': CtrlAction(QIcon(),'&Reservation', self.add_reservation),
            'view_malles': CtrlAction(
                QIcon(), '&Malles', self.display_malles, admin_required=False),
            'view_malles_types':CtrlAction(
                QIcon(),'&Types de malles', self.display_malles_types),
            'view_fournisseurs':CtrlAction(
                QIcon(),'&Fournisseurs', self.display_fournisseurs),
            'view_produits':CtrlAction(QIcon(), '&Produits', self.display_produits),
            'view_inputs':CtrlAction(QIcon(), '&Arrivages', self.display_inputs),
            'view_sejours':CtrlAction(QIcon(), '&Séjours', self.display_sejours),
            'view_lieux':CtrlAction(QIcon(), '&lieux', self.display_lieux),
            'view_users':CtrlAction(QIcon(), '&utilisateurs', self.display_users)
        }

        fileMenu = menubar.addMenu('&Fichier')
        fileMenu.addAction(self.actions['connect'])
        fileMenu.addAction(self.actions['disconnect'])
        export_pdf_menu = fileMenu.addMenu('&Exporter en PDF')
        export_pdf_menu.addAction(self.actions['export_commandes'])
        export_pdf_menu.addAction(self.actions['export_checker'])
        export_xlsx_menu = fileMenu.addMenu('&Exporter en Excel')
        export_xlsx_menu.addAction(self.actions['export_xlsx_malles'])
        fileMenu.addAction(self.actions['exit'])
        edit_menu = menubar.addMenu('&Édition')
        edit_menu.addAction(self.actions['settings'])
        view_menu = menubar.addMenu('&Vue')
        view_menu.addAction(self.actions['view_malles'])
        view_menu.addAction(self.actions['view_malles_types'])
        view_menu.addAction(self.actions['view_fournisseurs'])
        view_menu.addAction(self.actions['view_produits'])
        view_menu.addAction(self.actions['view_inputs'])
        view_menu.addAction(self.actions['view_sejours'])
        view_menu.addAction(self.actions['view_lieux'])
        addMenu = menubar.addMenu('&Ajouter')
        addMenu.addAction(self.actions['add_fournisseur'])
        addMenu.addAction(self.actions['add_produit'])
        addMenu.addAction(self.actions['add_input'])
        addMenu.addAction(self.actions['add_malle_type'])
        addMenu.addAction(self.actions['add_malle'])
        addMenu.addAction(self.actions['add_sejour'])
        addMenu.addAction(self.actions['add_reservation'])

        self.setMinimumSize(850, 300)
        self.show()
        
        self.models = False
        self.settings = QSettings('Kidivid', 'DiabolikStock')
        self.db = Query(self)
        self.connected_user = None
        self.connect()
        self.setCentralWidget(StartupView(self))

    def _add_action(self, name, function_name, shortcut=None):
        action = CtrlAction(QIcon(), name, function_name)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(function_name)
        return action

    def view_rapport(self):
        RapportDialog(self)

    def connect(self):
        connected = self.connect_db()
        if connected:
            logging.info('connected to database')
            self.connect_user()

    def connect_db(self):
        self.connected_db = self.db.connect(self.settings)
        if self.connected_db:
            logging.info('connection à la base de donnée réussie')
            self.models = Models(self.db.db)
            return True
        else:
            QMessageBox.warning(self, "Erreur", "La connection à\
            la base de données a échouée.")
            ok = ConfigDialog(self, self.settings).result()
            if ok:
                self.connect_db()
            else:
                return False

    def connect_user(self):
        user, groups = UserConnect(self, self.models.users).get_user()
        if user and groups:
            self.connected_user = (user, groups)
            self.statusBar().showMessage(user + ' connecté, group ' + str(groups))
            logging.info(
                'user:' + user + ' groups:' + str(groups) + ' connected')
            self.activate_actions()
            self.actions['disconnect'].setEnabled(True)
            self.actions['connect'].setEnabled(False)
            return True
        else:
            return False

    def disconnect_user(self):
        self.statusBar().showMessage("déconnecté")
        self.desactivate_all_actions()
        self.connected_user = None
        self.actions['connect'].setEnabled(True)

    def activate_actions(self):
        def verify_db_and_enable(action):
            if not action.db_connected_required or self.connected_db:
                action.setEnabled(True)
        
        user, groups = self.connected_user
        if 1 in groups: # if admin group
            for _, action in self.actions.items():
                verify_db_and_enable(action)
        elif 2 in groups: #if user group
            for _, action in self.actions.items():
                if not action.admin_required:
                    verify_db_and_enable(action)

    def desactivate_all_actions(self):
        for _, action in self.actions.items():
            action.setEnabled(False)
        self.actions['quit'].setEnabled(True)

    def set_config(self):
        ConfigDialog(self, self.settings)

    def add_fournisseur(self):
        AddFournisseur(self, self.models.fournisseurs)

    def add_product(self):
        ProductForm(self, self.models.produits, self.models.fournisseurs)

    def add_input(self):
        AddInput(self, self.models.inputs)

    def add_malle(self):
        malle = MalleFormDialog(self, self.models.malles, self.models)
        malle.exec_()
    
    def add_malle_type(self):
        AddMalleType(self, self.models.malles_types)

    def add_sejour(self):
        SejourForm(self, self.models.sejours, self.models.lieux)

    def add_lieu(self):
        dialog = LieuForm(None, self.models.lieux)

    def add_reservation(self):
        dialog = ReservationForm(None, self.models.reservations)

    def display_malles(self):
        MallesArrayDialog(self, self.models.malles)

    def display_malles_types(self):
        MallesTypesDialog(self, MallesTypesWithMalles())

    def display_fournisseurs(self):
        dialog = DisplayTableViewDialog(self, Fournisseurs(self, self.db.db))
        dialog.exec_()

    def display_inputs(self):
        dialog = InputsArray(self, Inputs(self, self.db.db))
        dialog.exec_()

    def display_produits(self):
        dialog = ProduitsArrayDialog(self, Produits(self, self.db.db))

    def display_lieux(self):
        dialog = LieuxArrayDialog(self, self.models.lieux)

    def display_sejours(self):
        dialog = DisplayTableViewDialog(self, self.models.sejours)
        dialog.exec_()

    def display_users(self):
        dialog = UsersArrayDialog(self, self.models.users)
        dialog.exec_()

    def set_autostock(self):
        if self.connected_db:
            self.db.enable_autostock(self.settings.value('autostock'))

    def get_pdf_filename(self):
        filename, _format = QFileDialog.getSaveFileName(
            self, "Exporter au format PDF", None, 'PDF(*.pdf)')
        if filename:
            if filename[-4:] != '.pdf':
                filename += '.pdf'
        return filename

    def get_xlsx_filename(self):
        filename, _format = QFileDialog.getSaveFileName(
            self, "Exporter au format XLSX", None, 'XLSX(*.xlsx)')
        if filename:
            if filename[-5:] != '.xlsx':
                filename += '.xlsx'
        return filename

    def export_commandes(self):
        from export import commandes
        filename = self.get_pdf_filename()
        commandes.create_pdf(filename, self.db) 

    def export_checker(self):
        from export import malle_checker
        malle_ref, ok = QInputDialog.getText(self, '', 'Entrez la référence')
        if not ok or not malle_ref:
            return False
        doc = malle_checker.create_doc(self.db, malle_ref)
        if not doc[0]:
            QMessageBox.warning(self, "Erreur", doc[1])
            return False
        from export.utils import pdf_export
        filename = self.get_pdf_filename()
        pdf_export(doc[1], filename) 

    def export_xlsx_malles(self):
        from export import xlsx_malle
        type_, ok = QInputDialog.getText(self, '', 'Entrez le type')
        if ok:
            filename = self.get_xlsx_filename()
            xlsx_malle.write_file(self.db, type_, filename)
            
class CtrlAction(QAction):
    """ Action with some access rules """
    def __init__(
        self,
        icon,
        text,
        function,
        shortcut=None,
        admin_required=True,
        user_required=True,
        db_connected_required=True,
        ):
        super().__init__(icon, text, None)
        self.admin_required = admin_required
        self.user_required = user_required
        self.db_connected_required = db_connected_required
        self.setEnabled(False)
        self.triggered.connect(function)
        if shortcut:
            self.setShortcut(shortcut)

if __name__ == '__main__':
    import sys, os
    
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(
        logging.Formatter('%(levelname)s::%(module)s:%(lineno)d :: %(message)s'))
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stdout_handler)
    
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
