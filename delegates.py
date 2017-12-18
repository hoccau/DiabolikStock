#!/usr/bin/python3
# -*- coding: utf-8 -*- 

"""
Diabolik Stock | QT Delegates
"""

from PyQt5.QtWidgets import QStyledItemDelegate, QItemDelegate, QComboBox
from PyQt5.QtSql import QSqlRelationalDelegate

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

class ComboBoxCompleterDelegate(QSqlRelationalDelegate):
    def __init__(self, parent=None, relation_model=2):
        super().__init__(parent)
        self.relation_model = relation_model

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.setEditable(True)
        model = index.model()
        editor.setModel(model.relationModel(self.relation_model))
        editor.setModelColumn(1)
        return editor

    def setEditorData(self, editor, index):
        model = index.model()
        value = model.relationModel(self.relation_model).data(index)
        if value:
            editor.setCurrentIndex(int(value))

    def __init__(self, parent=None, relation_model=2):
        super().__init__(parent)
        self.relation_model = relation_model

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        editor.setEditable(True)
        model = index.model()
        editor.setModel(model.relationModel(self.relation_model))
        editor.setModelColumn(1)
        return editor

    def setEditorData(self, editor, index):
        model = index.model()
        value = model.relationModel(self.relation_model).data(index)
        if value:
            editor.setCurrentIndex(int(value))

class QSqlRelationalDelegateBehindProxy(QSqlRelationalDelegate):
    """ Magic delegate to have a QSqlRelationalDelegate behind a 
    QSortFilterProxyModel. Copied from https://stackoverflow.com/questions/28231773/qsqlrelationaltablemodel-with-qsqlrelationaldelegate-not-working-behind-qabstrac """
    def createEditor(self, parent, option, index):
        proxy = index.model()
        self.base_index = proxy.mapToSource(index)
        return super().createEditor(parent, option, self.base_index)

    def setEditorData(self, editor, index):
        proxy = index.model()
        self.base_index = proxy.mapToSource(index)
        return super().setEditorData(editor, self.base_index)

    def setModelData(self, editor, model, index):
        self.base_model = model.sourceModel()
        self.base_index = model.mapToSource(index)
        return super().setModelData(editor, self.base_model, self.base_index)

class ComboBoxCompleterProxiedDelegate(ComboBoxCompleterDelegate):
    def __init__(self, parent, relation_model=2):
        ComboBoxCompleterDelegate.__init__(self, parent, relation_model)

    def createEditor(self, parent, option, index):
        proxy = index.model()
        base_index = proxy.mapToSource(index)
        return ComboBoxCompleterDelegate.createEditor(
            self, parent, option, base_index)
    
    def setEditorData(self, editor, index):
        proxy = index.model()
        base_index = proxy.mapToSource(index)
        return  ComboBoxCompleterDelegate.setEditorData(self, editor, base_index)
    
    def setModelData(self, editor, model, index):
        base_model = model.sourceModel()
        base_index = model.mapToSource(index)
        return ComboBoxCompleterDelegate.setModelData(
            self, editor, base_model, base_index)

class MalleDelegate(QItemDelegate):
    """ Like QSqlRelationalDelegate behaviour """
    def setModelData(self, editor, model, index):
        if index.column() == 2 or index.column() == 1:
            idx = editor.model().index(editor.currentIndex(), 0)
            data = editor.model().data(idx)
            model.setData(index, data, Qt.EditRole)
        else:
            super().setModelData(editor, model, index)

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
