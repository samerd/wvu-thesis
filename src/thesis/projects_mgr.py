'''
Created on Jun 24, 2020

@author: samerd
'''
from thesis.db_connection import DbConnection


class ProjectsMgr:

    def __init__(self):
        self._projects = list()
        self._load_table()

    def _load_table(self):
        conn = DbConnection("PROJECTS")
        conn.connect()
        data = conn.fetch()
        while data:
            project = data[0]
            self._projects.append(project)
            data = conn.fetch()
        conn.disconnect()

    def __iter__(self):
        for proj in self._projects:
            yield proj
