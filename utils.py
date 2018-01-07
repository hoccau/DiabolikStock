#!/usr/bin/python3
# -*- coding: utf-8 -*- 

from PyQt5.QtWidgets import QMessageBox
import logging
import sys

def displayed_error(error):
    QMessageBox.warning(None, "Erreur", error.text())
    logging.warning(error.text())

def get_logger():
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(
        logging.Formatter('%(levelname)s::%(module)s:%(lineno)d :: %(message)s'))
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stdout_handler)
