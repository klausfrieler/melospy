""" Class for SimpleMetaData"""

from melospy.basic_representations.composition_info import *
from melospy.basic_representations.meta_data import *


class SimpleMetaData(MetaData):
    """ Class for simple meta data"""

    def __init__(self, compositionInfo = ""):
        self.setCompositionInfo(compositionInfo)

    def clone(self):
        return SimpleMetaData(self.getCompositionInfo().clone())

    def getInfoTypes(self):
        return ["CompositionInfo"]


    def getCompositionInfo(self):
        return self.__ci

    def setCompositionInfo(self, ci):
        if ci == None or isinstance(ci, CompositionInfo ):
            self.__ci = ci
        else:
            raise TypeError("Expected 'CompositionInfo' object or 'None'.")
        return self


    def __str__(self):
        sep = "\n================================="
        return "\n".join([
          "\nCompositionInfo:   " + sep, get_NA_str(self.__ci)])

    compinfo  = property(getCompositionInfo, setCompositionInfo)
