'''
Created on Sep 6, 2020

@author: samerd
'''
from collections import defaultdict


class TypeMetrics:

    def __init__(self):
        self.nof = 0
        self.nopf = 0
        self.nom = 0
        self.nopm = 0
        self.loc = 0
        self.wmc = 0
        self.nc = 0
        self.dit = 0
        self.fanin = 0
        self.fanout = 0

    def update(self, NOF, NOPF, NOM, NOPM, LOC, WMC, NC, DIT, FANIN, FANOUT):
        self.nof += int(NOF)
        self.nopf += int(NOPF)
        self.nom += int(NOM)
        self.nopm += int(NOPM)
        self.loc += int(LOC)
        self.wmc += int(WMC)
        self.nc += int(NC)
        self.dit += int(DIT)
        self.fanin += int(FANIN)
        self.fanout += int(FANOUT)

    @classmethod
    def get_header(cls):
        return "NOF,NOPF,NOM,NOPM,LOC,WMC,NC,DIT,FANIN,FANOUT"

    def get_data(self):
        return "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s" % (
            self.nof, self.nopf, self.nom, self.nopm, self.loc, self.wmc, self.nc,
            self.dit, self.fanin, self.fanout)


class MetricsMgr:

    def __init__(self, file_name):
        self._packages = set()
        self._pkg_classes = dict()
        self._classses = 0
        self._loc = 0
        self._pkg_stats = defaultdict(TypeMetrics)
        self._parse(file_name)

    def _parse(self, file_name):
        with open(file_name) as fp:
            next(fp)
            for line in fp:
                ll = line.split(",")
                _, pkg, _, NOF, NOPF, NOM, NOPM, LOC, WMC, NC, DIT, _, \
                    FANIN, FANOUT, _ = ll
                self._packages.add(pkg)
                self._pkg_classes.setdefault(pkg, 0)
                self._pkg_classes[pkg] += 1
                self._pkg_stats[pkg].update(
                    NOF, NOPF, NOM, NOPM, LOC, WMC, NC, DIT, FANIN,
                    FANOUT)
                self._classses += 1
                self._loc += int(LOC)

    def get_pkg_count(self):
        return len(self._packages)

    def get_classes_count(self):
        return self._classses

    def get_total_loc(self):
        return self._loc

    def get_pkg_classes(self, pkg):
        return self._pkg_classes.get(pkg, 0)

    def get_pkg_loc(self, pkg):
        return self._pkg_stats[pkg].loc

    def get_pkg_metrics(self, pkg):
        return self._pkg_stats[pkg]

    def iter_packages(self):
        return iter(self._packages)
