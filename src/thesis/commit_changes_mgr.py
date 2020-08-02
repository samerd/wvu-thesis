'''
Created on Jun 18, 2020

@author: samerd
'''
from thesis.base_commit_mgr import BaseCommitMgr


class CommitInfo:

    def __init__(self, project, commit_hash):
        self.project = project
        self.commit_hash = commit_hash
        self.changes = list()

    def add_change(self, change):
        self.changes.append(change)


class CommitChangeInfo:

    def __init__(self):
        self.file_path = None
        self.change_type = None
        self.lines_added = 0
        self.nloc = 0
        self.complexity = 0
        self.package = None

    @classmethod
    def extract_package(cls, file_path):
        if not file_path.endswith(".java"):
            return None
        path_list = file_path.split("/")
        last_index = len(path_list) - 1

        first_index = 0
        while first_index < last_index:
            if path_list[first_index] in ('org', 'com'):
                break
            first_index += 1
        if last_index > first_index:
            return ".".join(path_list[first_index:last_index])
        return None

    def load_info(self, record):
        self.file_path = record[3]
        self.change_type = record[4]
        if record[6]:
            self.lines_added = int(record[6])
        if record[8]:
            self.nloc = int(record[8])
        if record[9]:
            self.complexity = int(record[9])
        self.package = self.extract_package(self.file_path)


class PackageEffortsInfo:

    def __init__(self):
        self.lines_added = 0


class CommitChangesTable(BaseCommitMgr):

    def __init__(self, project):
        super(CommitChangesTable, self).__init__(
            project, "GIT_COMMITS_CHANGES")

    def _handle_record(self, data):
        commit_hash = data[1]
        change = CommitChangeInfo()
        change.load_info(data)
        if commit_hash not in self._commits:
            self._commits[commit_hash] = CommitInfo(
                self._project, commit_hash)
        self._commits[commit_hash].add_change(change)

    def extract_release_packages(self, commit_release_tbl):
        release_efforts = dict()
        for commit, commit_info in self._commits.items():
            release = commit_release_tbl.get_commit_release(commit)
            release_data = release_efforts.setdefault(release, dict())
            for change in commit_info.changes:
                if not change.package:
                    continue
                if change.package not in release_data:
                    release_data[change.package] = PackageEffortsInfo()
                release_data[change.package].lines_added += change.lines_added
        return release_efforts

    def get_commit_details(self, commit):
        return self._commits.get(commit, "")

    def __iter__(self):
        return iter(self._commits)

    def keys(self):
        return self._commits.keys()

    def items(self):
        return self._commits.items()

    def values(self):
        return self._commits.values()
