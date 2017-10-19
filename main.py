#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Diabolik Stock
Logiciel de gestion du matériel pour l'association Diabolo
"""

from PyQt5 import QtSql
from PyQt5.QtWidgets import (
    QApplication, qApp, QMainWindow, QAction, QMessageBox, QFileDialog,
    QInputDialog)
from PyQt5.QtGui import QIcon
from models import (
    Models, Malles, MallesTypesWithMalles, Fournisseurs, Inputs, Produits,
    ContenuChecker, Sejours)
from db import Query
from views import (
    MalleFormDialog, AddMalleType, AddInput, AddFournisseur, ProductForm, 
    StartupView, DisplayTableViewDialog, MallesArrayDialog, MallesTypesDialog, 
    SejourForm, ContenuCheckerDialog, LieuForm, ReservationForm, 
    ProduitsArrayDialog, InputsArray, LieuxArrayDialog)
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
            'export_checker': self._add_action('&Malle', self.export_checker),
            'export_xlsx_malles': self._add_action(
                '&Type', self.export_xlsx_malles),
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
            'view_sejours':self._add_action('&Séjours', self.display_sejours),
            'view_lieux':self._add_action('&lieux', self.display_lieux)
        }

        fileMenu = menubar.addMenu('&Fichier')
        fileMenu.addAction(connectAction)
        export_pdf_menu = fileMenu.addMenu('&Exporter en PDF')
        export_pdf_menu.addAction(self.db_actions['export_commandes'])
        export_pdf_menu.addAction(self.db_actions['export_checker'])
        export_xlsx_menu = fileMenu.addMenu('&Exporter en Excel')
        export_xlsx_menu.addAction(self.db_actions['export_xlsx_malles'])
        fileMenu.addAction(exitAction)
        edit_menu = menubar.addMenu('&Édition')
        view_menu = menubar.addMenu('&Vue')
        view_menu.addAction(self.db_actions['view_malles'])
        view_menu.addAction(self.db_actions['view_malles_types'])
        view_menu.addAction(self.db_actions['view_fournisseurs'])
        view_menu.addAction(self.db_actions['view_produits'])
        view_menu.addAction(self.db_actions['contenu_checker'])
        view_menu.addAction(self.db_actions['view_sejours'])
        view_menu.addAction(self.db_actions['view_lieux'])
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
