'''
Created on Apr 5, 2020

@author: Samir Deeb
'''
import sqlite3

DB_PATH = "C:\\Users\\samerd\\OneDrive - Mellanox\\SQLite-Database\\"\
    "technicalDebtDataset.db"
DB_NAME = "technicalDebtDataset"


class DbConnection:
    regex_map = dict()

    def __init__(self, table_name, order_by=None, query_filter=None):
        self._query = self._build_query(table_name, order_by, query_filter)
        self._db = None
        self._cursor = None

    @staticmethod
    def _build_query(table_name, order_by, query_filter):
        query = "SELECT * FROM %s" % table_name
        if query_filter:
            query += (" " + query_filter)
        if order_by:
            query += " ORDER BY "
            query += ",".join(order_by)
        print(query)
        return query

    def connect(self):
        self._db = sqlite3.connect(DB_PATH)
        self._cursor = self._db.cursor()
        self._cursor.execute(self._query)

    def disconnect(self):
        self._db.close()

    def fetch(self):
        return self._cursor.fetchone()
