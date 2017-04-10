#!/usr/bin/python3
# -*- coding: utf-8 -*- 

from PyQt5.QtSql import (
    QSqlQueryModel, QSqlDatabase, QSqlQuery, QSqlRelationalTableModel,
    QSqlRelation, QSqlTableModel)
from PyQt5.QtCore import Qt, qDebug, qWarning
import logging

DEBUG_SQL = True

class Query(QSqlQueryModel):
    def __init__(self, parent=None):
        super(Query, self).__init__(parent)

        self.db = QSqlDatabase.addDatabase('QPSQL')

    def connect(self):
        self.db.setHostName("localhost")
        self.db.setDatabaseName("testdiabostock")
        self.db.setUserName("hoccau")
        self.db.setPassword('password')
        ok = self.db.open()
        if ok:
            self.query = QSqlQuery()
            return True
        else:
            logging.warning(self.db.lastError().databaseText())
            return False

    def exec_(self, request=None):
        """ Execute a request and return True if no error occur """
        if request:
            req = self.query.exec_(request)
        else:
            req = self.query.exec_()
            request = self.query.lastQuery()
        if DEBUG_SQL:
            logging.info(str(req) + ":" + request)
            if req == False:
                logging.warning(self.query.lastError().databaseText())
        return req

    def get_fournisseurs(self):
        self.query.exec_("SELECT NOM, ID FROM fournisseurs")
        return self._query_to_dic()

    def get_(self, values=[], table=None, condition=None, distinct=False):
        sql_values = ",".join(values)
        if condition == None:
            condition = ""
        else:
            condition = " WHERE "+str(condition)
        if distinct:
            distinct = "DISTINCT"
        else:
            distinct = ""
        self.exec_("SELECT "+distinct+' '+sql_values+" FROM "+table + condition)
        records = []
        while self.query.next():
            dic = {}
            for i, value in enumerate(values):
                dic[value] = self.query.value(i) 
            records.append(dic)
        return records
   
    def get_last_id(self, table):
        self.exec_("SELECT id FROM "+table+" ORDER BY id DESC LIMIT 1")
        while self.query.next():
            return self.query.value(0)

    def set_(self, dic={}, table=None):
        self.query.prepare(
            "INSERT INTO "+table+"("+",".join(dic.keys())+")\
            VALUES ("\
            +','.join([':'+x for x in list(dic.keys()) ])+")"
            )
        for k, v in dic.items():
            self.query.bindValue(':'+k, v)
        q = self.query.exec_()
        return q

    def update(self, datas={}, table='', qfilter_key=None, qfilter_value=None):
        l = []
        for k, v in datas.items():
            l += [str(k) + "='" + str(v)+"'"]
        success = self.exec_("UPDATE "+table+" SET "+', '.join(l)+\
        ' WHERE '+qfilter_key+" = '"+qfilter_value+"'")
        logging.info('update success'+ success)
        return success
    
    def delete(self, table, qfilter_key, qfilter_value):
        self.exec_('DELETE FROM '+table+' WHERE '+qfilter_key+' = '+"'"+qfilter_value+"'")

    def _query_to_dic(self):
        """ return a dict which contains query results """
        dic = {}
        while self.query.next():
            dic[self.query.value(0)] = self.query.value(1)
        return dic

    def _query_to_lists(self, nbr_values=1):
        """ return a list which contains records as lists 

            Args:
                nbr_values: excepted number of values.
        """
        list_ = []
        while self.query.next():
            record = []
            for i in range(nbr_values):
                record.append(self.query.value(i))
            list_.append(record)
        return list_

    def _query_to_list(self):
        """ return a list of values. The query must return one-value records """
        list_ = []
        while self.query.next():
            list_.append(self.query.value(0))
        return list_

if __name__ == '__main__':
    
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(
        logging.Formatter('%(levelname)s :: %(message)s'))
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stdout_handler)

    m = Query()
    res = m.connect()
    logging.info(res)
