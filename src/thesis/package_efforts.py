'''
Created on Jun 18, 2020

@author: samerd
'''
from __future__ import (absolute_import, division)

import os

from thesis import get_dataset_dir
from thesis.commit_changes_mgr import CommitChangesTable
from thesis.commit_release_mgr import CommitReleaseMgr


class PackageEffortData:

    def __init__(self):
        self.lines_added = 0
        self.ref_ph = 0
        self.total_lines_added = 0
        self.total_ph = 0
        self.percent = 0
        self.effort3 = ""
        self.effort5 = ""

    def set_total_lines(self, lines_added):
        self.total_lines_added = lines_added
        self.total_ph = 2.94 * lines_added / 1000. * 176
        if lines_added:
            self.percent = self.lines_added * 100 / self.total_lines_added
            if self.percent <= 8:
                self.effort3 = "Low"
            elif self.percent <= 40:
                self.effort3 = "Medium"
            else:
                self.effort3 = "High"

            if self.percent <= 4:
                self.effort5 = "Very Low"
            elif self.percent <= 13:
                self.effort5 = "Low"
            elif self.percent <= 35:
                self.effort5 = "Medium"
            elif self.percent <= 70:
                self.effort5 = "High"
            else:
                self.effort5 = "Very High"

    def __str__(self):
        return "%.d,%.2f,%.d,%.2f,%.2f" % (
            self.lines_added,
            self.ref_ph,
            self.total_lines_added,
            self.total_ph,
            self.percent)


class PackageEffortsAnalyzer:

    def __init__(self, projects):
        self.efforts_mapping = dict()
        self.projects = projects

    @classmethod
    def generate(cls, input_file, output_file):
        fout = open(output_file, "w")
        efforts_mapping = dict()
        projects = set()
        with open(input_file) as filep:
            for line in filep:
                line_attrs = line.split(",")
                key = (line_attrs[0], line_attrs[1], line_attrs[2])
                projects.add(line_attrs[0])
                if key not in efforts_mapping:
                    efforts_mapping[key] = PackageEffortData()
                else:
                    print("Duplicate entry")
                pkt_efforts = efforts_mapping[key]
                pkt_efforts.lines_added = float(line_attrs[3])
                pkt_efforts.ref_ph = float(line_attrs[4])

        for proj in projects:
            commit_changes_tbl = CommitChangesTable(proj)
            commit_release_tbl = CommitReleaseMgr(proj)
            pkg_data = commit_changes_tbl.extract_release_packages(
                commit_release_tbl)
            for rel, rel_data in pkg_data.items():
                for pkg, pkg_data in rel_data.items():
                    key = (proj, rel, pkg)
                    pkg_info = efforts_mapping.get(key)
                    if not pkg_info:
                        continue
                    pkg_info.set_total_lines(pkg_data.lines_added)
                    fout.write(
                        "%s,%s,%s,%s\n" % (proj, rel, pkg, str(pkg_info)))
        fout.close()

    def load(self, fname):
        with open(fname) as fp:
            for line in fp:
                ll = line.split(",")
                if ll[0] not in self.projects:
                    continue
                key = (ll[0], ll[1], ll[2])
                pkt_efforts = self.efforts_mapping[key] = PackageEffortData()
                pkt_efforts.lines_added = float(ll[3])
                pkt_efforts.ref_ph = float(ll[4])
                pkt_efforts.total_lines_added = float(ll[5])
                pkt_efforts.total_ph = float(ll[6])
                pkt_efforts.percent = float(ll[7])

    def get_pkg_efforts(self, proj, rel, pkg):
        return self.efforts_mapping.get((proj, rel, pkg))

    def get_pkgs_ranks(self, proj, release, packages):
        pkgs_data = dict()
        for pkg in packages:
            key = proj, release, pkg
            pkg_info = self.efforts_mapping.get(key)
            if not pkg_info:
                ph = 0
            else:
                ph = pkg_info.ref_ph
            pkgs_data[pkg] = [ph, 0]
        sorted_rank = sorted(
            pkgs_data.items(), key=lambda x: x[1][0], reverse=True)
        rank = 1
        for pkg, _ in sorted_rank:
            pkgs_data[pkg][1] = rank
            rank += 1
        return pkgs_data


if __name__ == "__main__":
    ref_miner_dir = os.path.join(get_dataset_dir(), "ref_miner")
    g_input_file = os.path.join(ref_miner_dir, "ref_package.csv")
    g_output_file = os.path.join(ref_miner_dir, "ref_package_ex.csv")
    PackageEffortsAnalyzer.generate(g_input_file, g_output_file)
