#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Diabolik Stock
Logiciel de gestion du matériel pour l'association Diabolo
"""

from PyQt5 import QtSql
from PyQt5.QtWidgets import (
    QApplication, qApp, QMainWindow, QAction, QTabWidget, QTableView, 
    QAbstractItemView)
from PyQt5.QtGui import QIcon
from models import Models
from db import Query
from views import AddMalle, AddMalleType, AddInput, AddFournisseur
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
            'add_fournisseur': self._add_action(
                '&Fournisseur', self.add_fournisseur),
            'add_produit': self._add_action('&Produit', self.add_input),
            'add_malle_type': self._add_action(
                '&Malle type', self.add_malle_type),
            'add_malle': self._add_action('&Malle', self.add_malle)
        }

        fileMenu = menubar.addMenu('&Fichier')
        fileMenu.addAction(connectAction)
        fileMenu.addAction(exitAction)
        edit_menu = menubar.addMenu('&Édition')
        view_menu = menubar.addMenu('&Vue')
        addMenu = menubar.addMenu('&Ajouter')
        addMenu.addAction(self.db_actions['add_fournisseur'])
        addMenu.addAction(self.db_actions['add_produit'])
        addMenu.addAction(self.db_actions['add_malle_type'])
        addMenu.addAction(self.db_actions['add_malle'])

        self.statusBar().showMessage('')
        self.setMinimumSize(850,300)
        self.show()
        
        self.models = False
        self.db = Query(self)
        self.connect_db()
        
        self.tabs = QTabWidget()
        self.tables = {
            'fournisseurs': self._add_table_model(self.models.fournisseurs, 'fournisseurs'),
            'produits': self._add_table_model(self.models.inputs, 'inputs')
            }
        
        self.setCentralWidget(self.tabs)

    def _add_table_model(self, model, name, size=None):
        table = QTableView(self)
        table.setModel(model)
        table.setItemDelegate(QSqlRelationalDelegate())
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabs.addTab(table, name)
        return table

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

    def add_input(self):
        AddInput(self, self.models.inputs)

    def add_malle(self):
        AddMalle(self, self.models.malles)
    
    def add_malle_type(self):
        AddMalle(self, self.models.malles_types)

if __name__ == '__main__':
    import sys, os
    
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(
        logging.Formatter('%(levelname)s :: %(message)s'))
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stdout_handler)
    
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec_())
