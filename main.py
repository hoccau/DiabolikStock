#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Diabolik Stock
Logiciel de gestion du matériel pour l'association Diabolo
"""

from PyQt5 import QtSql
from PyQt5.QtWidgets import (
    QApplication, qApp, QMainWindow, QAction, QMessageBox, QFileDialog)
from PyQt5.QtGui import QIcon
from models import (
    Models, Malles, MallesTypesWithMalles, Fournisseurs, Inputs, ProduitsModel,
    ContenuChecker, Sejours)
from db import Query
from views import (
    AddMalle, AddMalleType, AddInput, AddFournisseur, AddProduct, StartupView,
    DisplayTableViewDialog, MallesDialog, MallesTypesDialog, SejourForm, 
    ContenuCheckerDialog, LieuForm, ReservationForm)
from PyQt5.QtSql import QSqlRelationalDelegate
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

        exitAction = self._add_action('&Quitter', qApp.quit, 'Ctrl+Q')
        connectAction = self._add_action('&Connection', self.connect_db, 'Ctrl+C')
        self.db_actions = {
            'export_commandes': self._add_action('&Commandes', self.export_commandes),
            'add_fournisseur': self._add_action(
                '&Fournisseur', self.add_fournisseur),
            'add_produit': self._add_action('&Produit', self.add_product),
            'add_input': self._add_action('&Entrée de produit', self.add_input),
            'add_malle_type': self._add_action(
                '&Malle type', self.add_malle_type),
            'add_malle': self._add_action('&Malle', self.add_malle),
            'add_sejour': self._add_action('&Séjour', self.add_sejour),
            'add_reservation': self._add_action('&Reservation', self.add_reservation),
            'view_malles':self._add_action('&Malles', self.display_malles),
            'view_malles_types':self._add_action(
                '&Types de malles', self.display_malles_types),
            'view_fournisseurs':self._add_action(
                '&Fournisseurs', self.display_fournisseurs),
            'view_produits':self._add_action('&Produits', self.display_produits),
            'contenu_checker':self._add_action(
                '&Contenu des malles', self.contenu_checker),
            'view_sejours':self._add_action('&Séjours', self.display_sejours)
        }

        fileMenu = menubar.addMenu('&Fichier')
        fileMenu.addAction(connectAction)
        export_menu = fileMenu.addMenu('&Exporter')
        export_menu.addAction(self.db_actions['export_commandes'])
        fileMenu.addAction(exitAction)
        edit_menu = menubar.addMenu('&Édition')
        view_menu = menubar.addMenu('&Vue')
        view_menu.addAction(self.db_actions['view_malles'])
        view_menu.addAction(self.db_actions['view_malles_types'])
        view_menu.addAction(self.db_actions['view_fournisseurs'])
        view_menu.addAction(self.db_actions['view_produits'])
        view_menu.addAction(self.db_actions['contenu_checker'])
        view_menu.addAction(self.db_actions['view_sejours'])
        addMenu = menubar.addMenu('&Ajouter')
        addMenu.addAction(self.db_actions['add_fournisseur'])
        addMenu.addAction(self.db_actions['add_produit'])
        addMenu.addAction(self.db_actions['add_input'])
        addMenu.addAction(self.db_actions['add_malle_type'])
        addMenu.addAction(self.db_actions['add_malle'])
        addMenu.addAction(self.db_actions['add_sejour'])
        addMenu.addAction(self.db_actions['add_reservation'])

        self.statusBar().showMessage('')
        self.setMinimumSize(850,300)
        self.show()
        
        self.models = False
        self.db = Query(self)
        self.connect_db()

        self.setCentralWidget(StartupView(self))

    def _add_action(self, name, function_name, shortcut=None):
        action = QAction(name, self)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(function_name)
        return action

    def view_rapport(self):
        RapportDialog(self)

    def connect_db(self):
        connected = self.db.connect()
        if not connected:
            QMessageBox.warning(self, "Erreur", "La connection à\
            la base de données a échouée.")
        else:
            logging.info('connection à la base de donnée réussie')
            self.models = Models(self.db.db)
            return True

    def set_infos(self):
        InfosCentreDialog(self)

    def add_fournisseur(self):
        AddFournisseur(self, self.models.fournisseurs)

    def add_product(self):
        AddProduct(self, self.models.produits, self.models.fournisseurs)

    def add_input(self):
        AddInput(self, self.models.inputs)

    def add_malle(self):
        AddMalle(self, self.models.malles, self.models.malles_types)
    
    def add_malle_type(self):
        AddMalleType(self, self.models.malles_types)

    def add_sejour(self):
        SejourForm(self, self.models.sejours, self.models.lieux)

    def add_lieu(self):
        dialog = LieuForm(None, self.models.lieux)

    def add_reservation(self):
        dialog = ReservationForm(None, self.models.reservations)

    def display_malles(self):
        model = Malles(self, self.db.db)
        MallesDialog(self, model)

    def display_malles_types(self):
        MallesTypesDialog(self, MallesTypesWithMalles())

    def display_fournisseurs(self):
        dialog = DisplayTableViewDialog(self, Fournisseurs(self, self.db.db))
        dialog.exec_()

    def display_inputs(self):
        dialog = DisplayTableViewDialog(self, Inputs(self, self.db.db))
        dialog.exec_()

    def display_produits(self):
        dialog = DisplayTableViewDialog(self, ProduitsModel())
        dialog.exec_()

    def contenu_checker(self):
        dialog = ContenuCheckerDialog(self, self.models)
        dialog.exec_()

    def display_sejours(self):
        dialog = DisplayTableViewDialog(self, self.models.sejours)
        dialog.exec_()

    def get_pdf_filename(self):
        filename, _format = QFileDialog.getSaveFileName(
            self, "Exporter au format PDF", None, 'PDF(*.pdf)')
        if filename:
            if filename[-4:] != '.pdf':
                filename += '.pdf'
        return filename

    def export_commandes(self):
        from export import commandes
        filename = self.get_pdf_filename()
        commandes.create_pdf(filename, self.db) 

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
