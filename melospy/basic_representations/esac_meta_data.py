""" Class for EsacMetaData"""

from melospy.basic_representations.esac_info import EsacInfo
from melospy.basic_representations.jm_util import get_NA_str
from melospy.basic_representations.meta_data import MetaData


class EsacMetaData(MetaData):
    """ Class for EsacMetaData"""

    def __init__(self, esacInfo=None):
        self.setEsacInfo(esacInfo)

    def clone(self):
        return EsacMetaData(self.getEsacInfo().clone())

    def getInfoTypes(self):
        return ["EsacInfo"]

    def getEsacInfo(self):
        return self.__esac_info

    def setEsacInfo(self, esac_info):
        if esac_info == None or isinstance(esac_info, EsacInfo):
            self.__esac_info = esac_info
        else:
            raise TypeError("Expected 'Esac' object or 'None'.")
        return self

    def identifier(self):
        return self.getField("esacid")

    # def __str__(self):
    #     sep = "\n================================="
    #     return "\n".join([
    #         "\nEsac Metadata:   " + sep, get_NA_str(self.__esac_info)])

    esacinfo = property(getEsacInfo, setEsacInfo)
