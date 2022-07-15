""" Class for PopSongMetaData"""

from melospy.basic_representations.meta_data import *
from melospy.basic_representations.popsong_info import *


class PopSongMetaData(MetaData):
    """ Class for PopSongMetaData"""

    def __init__(self, popSongInfo = None):
        self.setPopSongInfo(popSongInfo)

    def clone(self):
        return PopSongMetaData(self.getPopSongInfo().clone())

    def getInfoTypes(self):
        return ["PopSongInfo"]

    def getPopSongInfo(self):
        return self.__psi

    def setPopSongInfo(self, psi):
        if psi == None or isinstance(psi, PopSongInfo ):
            self.__psi= psi
        else:
            raise TypeError("Expected 'PopSong' object or 'None'.")
        return self

    def __str__(self):
        sep = "\n================================="
        return "\n".join([
          "\nPopsong Metadata:   " + sep, get_NA_str(self.__psi)])

    popsonginfo  = property(getPopSongInfo, setPopSongInfo)
