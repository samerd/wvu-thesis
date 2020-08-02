'''
Created on Jun 7, 2020

@author: samerd
'''
from __future__ import (absolute_import, division)
from thesis.arch_smells_info import SmellsInfoFactory


class BaseSmellsParser:

    def __init__(self, fname):
        self.fname = fname
        self._count = 0
        self.data = dict()
        self._parse()

    def get_smells_count(self):
        return self._count

    def _parse(self):
        with open(self.fname) as fp:
            next(fp)
            for line in fp:
                self._parse_line(line)
                self._count += 1

    def _parse_line(self, line):
        raise NotImplementedError(self._parse_line.__name__)


class ArchSmellsParser(BaseSmellsParser):

    def _parse_line(self, line):
        _, package, smell_type, _ = \
            line.strip().split(",", 3)
        pkg_data = self.data.setdefault(package, dict())
        pkg_data.setdefault(smell_type, 0)
        pkg_data[smell_type] += 1


class ArchSmellsParserEx(BaseSmellsParser):

    def _parse_line(self, line):
        _, package, smell_type, smell_cause = \
            line.strip().split(",", 3)
        pkg_data = self.data.setdefault(package, dict())
        smell_info = SmellsInfoFactory.create_smell_info(
            smell_type, smell_cause)
        if smell_info:
            smell_info, smell_cause = \
                smell_info.get_value(), smell_info.get_cause()
        else:
            smell_info = 0, ""
        pkg_data[smell_type] = smell_info, smell_cause


class DesignSmellsParser(BaseSmellsParser):

    def _parse_line(self, line):
        _, package, _, smell_type, _ = \
            line.strip().split(",", 4)
        pkg_data = self.data.setdefault(package, dict())
        pkg_data.setdefault(smell_type, 0)
        pkg_data[smell_type] += 1


class ImplSmellsParser(BaseSmellsParser):

    def _parse_line(self, line):
        _, package, _, _, smell_type, _ = \
            line.split(",", 5)
        pkg_data = self.data.setdefault(package, dict())
        pkg_data.setdefault(smell_type, 0)
        pkg_data[smell_type] += 1


class MetricsMgr:

    def __init__(self, file_name):
        self._packages = set()
        self._pkg_classes = dict()
        self._classses = 0
        self._loc = 0
        self._pkg_loc = dict()
        self._parse(file_name)

    def _parse(self, file_name):
        with open(file_name) as fp:
            next(fp)
            for line in fp:
                ll = line.split(",")
                pkg = ll[1]
                loc = int(ll[7])
                self._packages.add(pkg)
                self._pkg_classes.setdefault(pkg, 0)
                self._pkg_classes[pkg] += 1
                self._pkg_loc.setdefault(pkg, 0)
                self._pkg_loc[pkg] += loc
                self._classses += 1
                self._loc += loc

    def get_pkg_count(self):
        return len(self._packages)

    def get_classes_count(self):
        return self._classses

    def get_total_loc(self):
        return self._loc

    def get_pkg_classes(self, pkg):
        return self._pkg_classes.get(pkg, 0)

    def get_pkg_loc(self, pkg):
        return self._pkg_loc[pkg]

    def iter_packages(self):
        return iter(self._packages)

# class PkgAnalyzer:
#
#     def __init__(self, file_name):
#         self.effort_data = dict()
#         self._load(file_name)
#
#     def _load(self, file_name):
#         with open(file_name) as fp:
#             for line in fp:
#                 ll = line.split(",")
#                 proj = ll[0]
#                 release = ll[1]
#                 pkg = ll[2]
#                 ph = float(ll[4])
#                 key = proj, release
#                 proj_data = self.effort_data.setdefault(key, dict())
#                 proj_data[pkg] = ph
#
#     def get_pkgs_ranks(self, proj, release, packages):
#         key = proj, release
#         pkgs_data = dict()
#         proj_data = self.effort_data.get(key)
#         for pkg in packages:
#             ph = proj_data.get(pkg, 0)
#             pkgs_data[pkg] = [ph, 0]
#         sorted_rank = sorted(
#             pkgs_data.items(), key=lambda x: x[1][0], reverse=True)
#         rank = 1
#         for pkg, _ in sorted_rank:
#             pkgs_data[pkg][1] = rank
#             rank += 1
#         return pkgs_data


ARFF_HEADER = """\
@relation '%s'

@attribute Class-Count numeric
@attribute LOC numeric
@attribute Smells-Rank {'Very Low',Low,Medium,High,'Very High'}
@attribute Effort-Rank {'Very Low',Low,Medium,High,'Very High'}

@data
"""


class PackageInfo:
    RANK_3_LEVELS = ["Low", "Medium", "High"]
    RANK_5_LEVELS = ["Very Low", "Low", "Medium", "High", "Very High"]

    def __init__(self, pkg_name):
        self.pkg_name = pkg_name
        self.arch_count = 0
        self.arch_score = 0
        self.design_count = 0
        self.design_score = 0
        self.class_count = 0
        self.loc = 0
        self.smells_rank_3 = 0
        self.smells_rank_5 = 0
        self.n_smells_rank_3 = 0
        self.n_smells_rank_5 = 0
        self.effort_rank_3 = 0
        self.effort_rank_5 = 0
        self.n_effort_rank_3 = 0
        self.n_effort_rank_5 = 0

    @classmethod
    def calc_bin(cls, rank, count):
        loc5 = 4
        loc3 = 2
        percent = rank / count * 100
        if percent <= 10:
            loc5 = 0
        elif percent <= 30:
            loc5 = 1
        elif percent <= 70:
            loc5 = 2
        elif percent <= 90:
            loc5 = 3

        if percent <= 25:
            loc3 = 0
        elif percent <= 75:
            loc3 = 1
        return loc3, loc5

    def set_smells_rank(self, rank, count):
        self.n_smells_rank_3, self.n_smells_rank_5 = self.calc_bin(rank, count)
        self.smells_rank_3 = 2 - int((count - rank) / count * 3)
        self.smells_rank_5 = 4 - int((count - rank) / count * 5)

    def set_effort_rank(self, rank, count):
        self.n_effort_rank_3, self.n_effort_rank_5 = self.calc_bin(rank, count)
        self.effort_rank_3 = 2 - int((count - rank) / count * 3)
        self.effort_rank_5 = 4 - int((count - rank) / count * 5)

    @classmethod
    def get_csv_header(cls):
        return "Project,Release,Package,ClassCount,LOC,"\
            "SmellsRank3,ND-SmellsRank3,EffortRank3,ND-EffortRank3,"\
            "SmellsRank5,,ND-SmellsRank5,EffortRank5,ND-EffortRank5\n"

    @classmethod
    def get_arff_header(cls, relation):
        return ARFF_HEADER % relation

    def get_arff_3(self):
        return "%s,%s,%s,%s\n" % (
            self.class_count, self.loc,
            self.RANK_3_LEVELS[self.smells_rank_3],
            self.RANK_3_LEVELS[self.effort_rank_3])

    def get_arff_5(self):
        return "%s,%s,%s,%s\n" % (
            self.class_count, self.loc,
            self.RANK_5_LEVELS[self.smells_rank_5],
            self.RANK_5_LEVELS[self.effort_rank_5])

    def get_arff_3_nd(self):
        return "%s,%s,%s,%s\n" % (
            self.class_count, self.loc,
            self.RANK_3_LEVELS[self.n_smells_rank_3],
            self.RANK_3_LEVELS[self.n_effort_rank_3])

    def get_arff_5_nd(self):
        return "%s,%s,%s,%s\n" % (
            self.class_count, self.loc,
            self.RANK_5_LEVELS[self.n_smells_rank_5],
            self.RANK_5_LEVELS[self.n_effort_rank_5])

    def to_csv(self, project, release):
        return ",".join((
            project, release, self.pkg_name,
            str(self.class_count), str(self.loc),
            self.RANK_3_LEVELS[self.smells_rank_3],
            self.RANK_3_LEVELS[self.n_smells_rank_3],
            self.RANK_3_LEVELS[self.effort_rank_3],
            self.RANK_3_LEVELS[self.n_effort_rank_3],
            self.RANK_5_LEVELS[self.smells_rank_5],
            self.RANK_5_LEVELS[self.n_smells_rank_5],
            self.RANK_5_LEVELS[self.effort_rank_5],
            self.RANK_5_LEVELS[self.n_effort_rank_5]))
