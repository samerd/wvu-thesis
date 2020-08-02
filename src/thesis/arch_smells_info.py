'''
Created on Jun 7, 2020

@author: samerd
'''
import re


class BaseSmellInfo:

    def get_cause(self):
        return ""


class FeatureConcentrationInfo(BaseSmellInfo):
    REGEX = re.compile(
        r"component are: (.*) LCC \(Lack of Component Cohesion\) = ([\.\d]+)")

    def __init__(self, smell_cause):
        self.related_classes = 0
        self.lcc = 0
        self._parse(smell_cause)

    def _parse(self, smell_cause):
        match = self.REGEX.search(smell_cause)
        if match:
            self.lcc = float(match.group(2))
        else:
            print("FC: No match")

    def get_value(self):
        return self.lcc


class GodComponentInfo(BaseSmellInfo):
    REGEX = re.compile(
        r"Number of classes in the component are: (\d+)")
    REGEX2 = re.compile(
        r"The total LOC of the component: (\d+)")

    def __init__(self, smell_cause):
        self.count = 0
        self.cause = "classes"
        self._parse(smell_cause)

    def _parse(self, smell_cause):
        match = self.REGEX.search(smell_cause)
        if match:
            self.count = int(match.group(1))
        else:
            match = self.REGEX2.search(smell_cause)
            if match:
                self.count = int(match.group(1))
                self.cause = "LOC"
            else:
                print("GC: No match")

    def get_value(self):
        return self.count

    def get_cause(self):
        return self.cause


class UnstableDependencyInfo(BaseSmellInfo):
    REGEX = re.compile(
        r"less stable component\(s\): (.*)")

    def __init__(self, smell_cause):
        self.count = 0
        self._parse(smell_cause)

    def _parse(self, smell_cause):
        match = self.REGEX.search(smell_cause)
        if match:
            self.count = len(match.group(1).split())
        else:
            print("UD: No match")

    def get_value(self):
        return self.count


class CyclicDependencyInfo(BaseSmellInfo):
    REGEX = re.compile(
        r"The participating components in the cycle are: (.*)")

    def __init__(self, smell_cause):
        self.count = 0
        self._parse(smell_cause)

    def _parse(self, smell_cause):
        match = self.REGEX.search(smell_cause)
        if match:
            self.count = len(match.group(1).split())
        else:
            print("UD: No match")

    def get_value(self):
        return self.count


class AmbiguousInterfaceInfo(BaseSmellInfo):

    def __init__(self, smell_cause):
        self.count = 0
        self._parse(smell_cause)

    def _parse(self, smell_cause):
        pass

    def get_value(self):
        return self.count


class DenseStructureInfo(BaseSmellInfo):
    REGEX = re.compile(
        r"Average degree = ([\d\.]+)\.")

    def __init__(self, smell_cause):
        self.degree = 0
        self._parse(smell_cause)

    def _parse(self, smell_cause):
        match = self.REGEX.search(smell_cause)
        if match:
            self.degree = float(match.group(1))
        else:
            print("DS: No match")

    def get_value(self):
        return self.degree


class ScatteredFunctionalityInfo(BaseSmellInfo):

    def __init__(self, smell_cause):
        self.count = 0
        self._parse(smell_cause)

    def _parse(self, smell_cause):
        pass

    def get_value(self):
        return self.count


class SmellsInfoFactory:
    mapping = {
        "Feature Concentration": FeatureConcentrationInfo,
        "God Component": GodComponentInfo,
        "Unstable Dependency": UnstableDependencyInfo,
        "Cyclic Dependency": CyclicDependencyInfo,
        "Ambiguous Interface": AmbiguousInterfaceInfo,
        "Dense Structure": DenseStructureInfo,
        "Scattered Functionality": ScatteredFunctionalityInfo,
    }

    @classmethod
    def create_smell_info(cls, smell_type, smell_cause):
        if smell_type in cls.mapping:
            return cls.mapping[smell_type](smell_cause)
        return None
