#!/usr/bin/python3
# -*- coding: utf-8 -*- 

"""
Export Stock as pdf file
"""

import logging
from collections import OrderedDict
from PyQt5.QtCore import QDateTime, QDate
from PyQt5.QtPrintSupport import QPrinter
from .utils import html_doc

def create_pdf(filename='bonDeCommande.pdf', db=None):
    html = header() + html_commande(db)
    print(html)
    doc = html_doc(html)
    printer = QPrinter()
    printer.setOutputFileName(filename)
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setPageSize(QPrinter.A4)
    doc.print_(printer)

def header():
    html = "<h1>Bon de commande</H1>"
    html += "<p>Date d'émission : " 
    html += QDate.currentDate().toString('dd/MM/yyyy') + '</p>'
    return html

def html_commande(db):
    html = ''
    db.exec_("SELECT * FROM bon_de_commande")
    res = db._query_to_lists(5)
    fournisseurs = list(set([tuple(i[0:3]) for i in res]))
    logging.debug('fournisseurs:' + str(fournisseurs))
    fournisseurs_dic = OrderedDict()
    for i in fournisseurs:
        fournisseurs_dic[i[0]] = {'contact':{'mail':i[1], 'phone':i[2]}, 'produits':[]}
    logging.debug('fournisseurs:' + str(fournisseurs_dic))
    for row in res:
        fournisseurs_dic[row[0]]['produits'].append(row[3:])
    logging.debug('fournisseurs:' + str(fournisseurs_dic))
    for name, v in fournisseurs_dic.items():
        html += "<h3>" + name + "</h3>"
        html += "<p>" + v['contact']['mail'] + ' - ' 
        html += v['contact']['phone'] + '</p>'
        html += '<table border=1>'
        for product in v['produits']:
            html += '<tr><th>Produit</th><th>Quantité</th></tr>'
            html += '<tr>'
            for col in product:
                html += '<th>'
                html += str(col)
                html += '</th>'
            html += '</tr>'
        html += '</table>'
    return html
    
if '__main__' == __name__:
    from PyQt5.QtWidgets import QApplication
    import sys
    from db import Query
    db = Query()
    db.connect()
    app = QApplication(sys.argv)
    create_pdf(db=db)
