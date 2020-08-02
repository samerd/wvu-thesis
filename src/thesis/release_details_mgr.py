'''
Created on Jun 18, 2020

@author: samerd
'''


class ReleaseInfo:

    # pyling: disable=too-few-public-methods
    def __init__(self):
        self.proj = None
        self.release = None
        self.ref_months = None
        self.total_months = None
        self.ref_percentage = None
        self.effort = None

    @classmethod
    def from_row(cls, row):
        instance = cls()
        row_data = row.split(",")
        instance.proj = row_data[0]
        instance.release = row_data[1]
        instance.ref_months = float(row_data[2])
        instance.total_months = float(row_data[3])
        instance.ref_percentage = float(row_data[4])
        if instance.ref_percentage <= 2:
            instance.effort = "Very Low"
        elif instance.ref_percentage <= 5:
            instance.effort = "Low"
        elif instance.ref_percentage <= 10:
            instance.effort = "Medium"
        elif instance.ref_percentage <= 20:
            instance.effort = "High"
        else:
            instance.effort = "Very High"

        return instance


class ReleaseDetailsMgr:

    def __init__(self):
        self._mapping = dict()

    def load(self, fname):
        with open(fname) as filep:
            for line in filep:
                info = ReleaseInfo.from_row(line)
                self._mapping[(info.proj, info.release)] = info

    def get_release_info(self, proj, release):
        return self._mapping.get((proj, release))
