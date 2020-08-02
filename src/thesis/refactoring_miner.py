'''
Created on May 9, 2020

@author: samerd
'''
import os
import re

from thesis import get_dataset_dir
from thesis.commit_changes_mgr import CommitChangesTable
from thesis.commit_release_mgr import CommitReleaseMgr
from thesis.db_connection import DbConnection
from thesis.projects_mgr import ProjectsMgr


class RefactoringMinerTable:
    class_regex = re.compile(
        r".* (([a-zA-Z_$][a-zA-Z\d_$]*\.)*[a-zA-Z_$][a-zA-Z\d_$]*)$")
    super_regex = re.compile(
        r"Extract (Superclass|Interface)\t([a-zA-Z\d_$\.]+) from classes "
        r"\[(.+)\]$")
    FILTER = \
        "Where refactoringType IN ('Extract Method', 'Extract Superclass', "\
        "'Pull Up Method', 'Extract Class', 'Move Method', "\
        "'Extract And Move Method', 'Move Class', 'Inline Method', "\
        "'Extract Subclass', 'Push Down Method', 'Extract Interface')"

    def __init__(self, project):
        self._project = project
        self._table = list()
        self._load_table()

    @classmethod
    def _class_to_file_name(cls, class_name):
        path_list = class_name.split('.')
        count = 0
        for item in path_list:
            count += 1
            if item[0].isupper():
                break
        return '/'.join(path_list[:count]) + '.java', \
            '.'.join(path_list[:count - 1])

    @classmethod
    def _extract_file_name(cls, refactoring_detail):
        match = cls.class_regex.match(refactoring_detail)
        if match:
            class_name = match.group(1)
            file_name, package = cls._class_to_file_name(class_name)
            return [(file_name, package)]
        match = cls.super_regex.match(refactoring_detail)
        file_list = list()
        if match:
            class_name = match.group(2)
            file_list.append(cls._class_to_file_name(class_name))
            classes = match.group(3).split(", ")
            for class_name in classes:
                file_list.append(cls._class_to_file_name(class_name))
        else:
            print("could not extract class name from: %s" % refactoring_detail)
        return file_list

    def _load_table(self):
        q_filter = self.FILTER + " AND projectID='%s'" % self._project
        conn = DbConnection("REFACTORING_MINER", ["projectID", "commitHash"],
                            q_filter)
        conn.connect()
        data = conn.fetch()
        while data:
            _, commit_hash, refactoring_type, refactoringDetail = data
            file_names = self._extract_file_name(refactoringDetail)
            if file_names:
                for file_name, package in file_names:
                    self._table.append(
                        (commit_hash, refactoring_type, file_name, package))
            data = conn.fetch()
        conn.disconnect()

    def __iter__(self):
        for item in self._table:
            yield item


class RefMinerMgr:

    @classmethod
    def main(cls):
        dataset_dir = get_dataset_dir()
        ref_miner_dir = os.path.join(dataset_dir, "ref_miner")
        ref_miner_file = open(
            os.path.join(ref_miner_dir, "ref_miner.csv"), "w")
        ref_release_file = open(
            os.path.join(ref_miner_dir, "ref_release.csv"), "w")
        ref_package_file = open(
            os.path.join(ref_miner_dir, "ref_package.csv"), "w")
        ref_release_summ_file = open(
            os.path.join(ref_miner_dir, "ref_release_summ.csv"), "w")

        proj_man = ProjectsMgr()

        for proj in proj_man:
            ref_data = dict()
            commit_summ = dict()
            release_sum = dict()
            release_total = dict()
            commits_files = dict()
            file_package_map = dict()
            print(proj)
            ref_tbl = RefactoringMinerTable(proj)
            commits_tbl = CommitChangesTable(proj)
            release_tbl = CommitReleaseMgr(proj)
            print('data loaded')
            for commit_hash, refactoring_type, file_name, package in ref_tbl:
                commit_details = commits_tbl.get_commit_details(commit_hash)
                if not commit_details:
                    continue
                commit_files = commits_files.setdefault(commit_hash, set())
                key = None
                for change in commit_details.changes:
                    if file_name in change.file_path:
                        key = (commit_hash, change.file_path,
                               change.change_type, change.lines_added,
                               change.nloc, change.complexity, package)
                        ref_data_item = ref_data.setdefault(key, list())
                        ref_data_item.append(refactoring_type)
                        commit_files.add(change.file_path)
                        file_package_map[change.file_path] = package
                        break
                if not key:
                    print("File %s not found in commit %s" %
                          (file_name, commit_hash))
            release_packages = dict()
            for (commit_hash, file_path, change_type, lines_added, nloc,
                 complexity, package), ref_types in ref_data.items():
                release = release_tbl.get_commit_release(commit_hash)
                rel_pkg_data = release_packages.setdefault(release, dict())
                pkg_data = rel_pkg_data.setdefault(package, 0)
                commit_loc = commit_summ.setdefault(commit_hash, 0)
                lines_added = int(lines_added)
                commit_loc += lines_added
                pkg_data += lines_added
                rel_pkg_data[package] = pkg_data
                commit_summ[commit_hash] = commit_loc
                ref_miner_file.write(
                    "%s,%s,%s,%s,%s,%s,%s,%s\n" %
                    (proj, commit_hash, file_path, change_type, lines_added,
                     nloc, complexity, ";".join(ref_types)))
            for commit, commit_details in commits_tbl.items():
                release = release_tbl.get_commit_release(commit)
                curr_change = release_total.setdefault(release, 0)
                for commit_change in commit_details.changes:
                    curr_change += commit_change.lines_added
                    # file_path = commit_change[0]
                release_total[release] = curr_change

            for commit_hash, commit_loc in commit_summ.items():
                release = release_tbl.get_commit_release(commit_hash)
                hours = 2.94 * commit_loc / 1000. * 176
                release_hours = release_sum.setdefault(release, 0)
                release_hours += hours
                release_sum[release] = release_hours
                ref_release_file.write(
                    "%s,%s,%s,%d,%0.2f\n" %
                    (proj, commit_hash, release, commit_loc, hours))
            for release, release_hours in release_sum.items():
                release_loc = release_total.get(release)
                months = release_hours / 176
                release_total_months = 2.94 * release_loc / 1000.
                percent = months / release_total_months * 100.
                ref_release_summ_file.write(
                    "%s,%s,%0.1f,%0.1f,%0.1f\n" %
                    (proj, release, months, release_total_months, percent))
            for release, release_data in release_packages.items():
                for pkg, pkg_data in release_data.items():
                    pkh_hours = 2.94 * pkg_data / 1000. * 176
                    ref_package_file.write(
                        "%s,%s,%s,%s,%0.1f\n" %
                        (proj, release, pkg, pkg_data, pkh_hours))

        ref_miner_file.close()
        ref_release_file.close()
        ref_release_summ_file.close()
        ref_package_file.close()


if __name__ == '__main__':
    RefMinerMgr.main()
