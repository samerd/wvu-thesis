'''
Created on Jun 24, 2020

@author: samerd
'''
from thesis.base_commit_mgr import BaseCommitMgr


class CommitReleaseMgr(BaseCommitMgr):

    def __init__(self, project):
        super(CommitReleaseMgr, self).__init__(
            project, "GIT_COMMIT_RELEASE_2")

    def _handle_record(self, data):
        commit = data[1]
        release = data[3]
        self._commits[commit] = release

    def get_commit_release(self, commit):
        return self._commits.get(commit)
