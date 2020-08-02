'''
Created on Jul 4, 2020

@author: samerd
'''


class Calc:

    @classmethod
    def calc_levels(cls, file_name):
        mapping = dict()
        with open(file_name) as fp:
            for line in fp:
                line = line.strip()
                if not line or line.startswith('@'):
                    continue
                _, _, smells, effort = line.split(",")
                smellEfforts = mapping.setdefault(smells, dict())
                smellEfforts.setdefault(effort, 0)
                smellEfforts[effort] += 1
        print(mapping)


g_file_name = "C:\\Users\\samerd\\workspace\\wvu-thesis\\dataset\\"\
    "designite_analysis\\pkg_efforts_3_nd.arff"
Calc.calc_levels(g_file_name)

g_file_name = "C:\\Users\\samerd\\workspace\\wvu-thesis\\dataset\\"\
    "designite_analysis\\pkg_efforts_5_nd.arff"
Calc.calc_levels(g_file_name)
