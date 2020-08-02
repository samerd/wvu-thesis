'''
Created on May 25, 2020

@author: samerd
'''
import os

from scipy.stats.stats import spearmanr

from thesis import get_dataset_dir


class Stats:

    def __init__(self):
        self.complexity = list()
        self.nloc = list()
        self.lines_added = list()
        self.records = 0


class Calculator:

    def __init__(self, file_name):
        self._data = dict()
        self.total = Stats()
        self._load(file_name)

    def _load(self, file_name):
        with open(file_name) as fp:
            for line in fp:
                ll = line.split(",")
                if not ll[5] or not ll[6]:
                    continue
                proj_stats = self._data.setdefault(ll[0], Stats())
                proj_stats.lines_added.append(int(ll[4]))
                proj_stats.nloc.append(int(ll[5]))
                proj_stats.complexity.append(int(ll[6]))
                proj_stats.records += 1

    def print_status(self):
        for proj, proj_stats in self._data.items():
            if proj_stats.records < 150:
                continue
            corr1, pval1 = spearmanr(
                proj_stats.lines_added, proj_stats.complexity)
            corr2, pval2 = spearmanr(proj_stats.lines_added, proj_stats.nloc)
            print('%s,%.2f,%.4f,%.2f,%.4f,%d' % (
                proj, corr1, pval1, corr2, pval2, proj_stats.records))
            self.total.lines_added.extend(proj_stats.lines_added)
            self.total.complexity.extend(proj_stats.complexity)
            self.total.nloc.extend(proj_stats.nloc)
            self.total.records += len(proj_stats.nloc)
        corr1, pval1 = spearmanr(self.total.lines_added, self.total.complexity)
        corr2, pval2 = spearmanr(self.total.lines_added, self.total.nloc)
        print('%s,%.2f,%.4f,%.2f,%.4f,%d' % (
            "All-Projects", corr1, pval1, corr2, pval2, self.total.records))


if __name__ == "__main__":
    dataset_dir = get_dataset_dir()
    ref_miner_dir = os.path.join(dataset_dir, "ref_miner")
    ref_miner_file = os.path.join(ref_miner_dir, "ref_miner.csv")

    calc = Calculator(ref_miner_file)
    calc.print_status()
