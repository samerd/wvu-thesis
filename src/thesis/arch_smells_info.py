'''
Created on Jun 7, 2020

@author: samerd
'''
import re


class BaseSmellInfo:
    description = ""

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
            lcc = match.group(2)
            self.lcc = float(lcc)
            self.description = "LCC: %s" % lcc
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
        self.description = "%s: %d" % (self.cause, self.count)

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
            packages = match.group(1).split("; ")
            self.count = len(packages)
            self.description = "Packages(%d): %s" % (
                self.count, ";".join(packages))
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
            packages = match.group(1).split("; ")
            self.count = len(packages)
            self.description = "Packages(%d): %s" % (
                self.count, ";".join(packages))
        else:
            print("UD: No match")

    def get_value(self):
        return self.count


class AmbiguousInterfaceInfo(BaseSmellInfo):
    REGEX = re.compile(r"class: (\w+)")

    def __init__(self, smell_cause):
        self.count = 0
        self._parse(smell_cause)

    def _parse(self, smell_cause):
        match = self.REGEX.search(smell_cause)
        if match:
            class_name = match.group(1)
            self.count = 1
            self.description = "Class: %s" % class_name
        else:
            print("AI: No match")

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
            self.description = "Average degree: %d" % self.degree
        else:
            print("DS: No match")

    def get_value(self):
        return self.degree


class ScatteredFunctionalityInfo(BaseSmellInfo):
    REGEX = re.compile(r"Following components realize the same concern: (.*)")

    def __init__(self, smell_cause):
        self.count = 0
        self._parse(smell_cause)

    def _parse(self, smell_cause):
        match = self.REGEX.search(smell_cause)
        if match:
            packages = match.group(1).split("; ")
            self.count = len(packages)
            self.description = "Packages(%d): %s" % (
                self.count, ";".join(packages))
        else:
            print("SF: No match")

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

    @classmethod
    def get_smell_types(cls):
        return sorted(cls.mapping.keys())
