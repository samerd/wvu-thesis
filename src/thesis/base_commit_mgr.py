'''
Created on Aug 2, 2020

@author: samerd
'''
from thesis.db_connection import DbConnection


class BaseCommitMgr:

    def __init__(self, project, tbl_name):
        self._project = project
        self._commits = dict()
        self._load_table(tbl_name)

    def _load_table(self, tbl_name):
        query_filter = "Where projectID='%s'" % self._project
        conn = DbConnection(tbl_name, None, query_filter)
        conn.connect()
        data = conn.fetch()
        while data:
            self._handle_record(data)
            data = conn.fetch()
        conn.disconnect()

    def _handle_record(self, data):
        pass
