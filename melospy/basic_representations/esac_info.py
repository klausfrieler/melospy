""" Class for EsAC Info"""
from melospy.basic_representations.jm_util import get_NA_str, get_safe_value_from_dict


class EsacInfo(object):
    """ Class for EsAC info => meta data for EsAC tunes"""

    def __init__(self, collection = "",
                 melid = "",
                 esacid = "",
                 key = "",
                 unit = "",
                 signature = "",
                 title = "",
                 region = "",
                 function = "",
                 comment = "",
                 cnr = "",
                 source = "",
                 tunefamily = "",
                 text = "",
                 melstring =""):
        self.collection = collection
        self.melid = melid
        self.esacid = esacid
        self.title = title
        self.region = region
        self.function  = function
        self.comment = comment
        self.cnr = cnr
        self.source = source
        self.key = key
        self.unit = unit
        self.signature = signature
        self.tunefamily = tunefamily
        self.text = text
        self.melstring = melstring
        self.basefilename = None


    def clone(self):
        ret = EsacInfo()
        ret.__dict__ = {k:self.__dict__[k] for k in self.__dict__}
        return ret

    @staticmethod
    def fromDict(esac_info_dict):
        esac_info = EsacInfo()
        for key in esac_info_dict:
            eval("esac_info.set" + key + "('" + str(esac_info_dict[key]) + "')")
        return esac_info

    def getCollection(self):
        return self.__collection

    def setCollection(self, collection):
        self.__collection = collection
        return self

    def getMelid(self):
        return self.__melid

    def setMelid(self, melid):
        self.__melid = melid
        return self

    def getEsacid(self):
        return self.__esacid

    def setEsacid(self, esacid):
        self.__esacid = esacid
        return self

    def getTitle(self):
        return self.__title

    def setTitle(self, title):
        self.__title = title
        return self

    def getRegion(self):
        return self.__region

    def setRegion(self, region):
        self.__region = region
        return self

    def getFunction(self):
        return self.__function

    def setFunction(self, function):
        self.__function = function
        return self

    def getComment(self):
        return self.__comment

    def setComment(self, comment):
        self.__comment = comment
        return self

    def getCnr(self):
        return self.__cnr

    def setCnr(self, cnr):
        self.__cnr = cnr
        return self

    def getSource(self):
        return self.__source

    def setSource(self, source):
        self.__source = source
        return self

    def getKey(self):
        return self.__key

    def setKey(self, key):
        self.__key = key
        return self

    def getUnit(self):
        return self.__unit

    def setUnit(self, unit):
        self.__unit = unit
        return self

    def getSignature(self):
        return self.__signature

    def setSignature(self, signature):
        self.__signature = signature
        return self

    def getTunefamily(self):
        return self.__tunefamily

    def setTunefamily(self, tunefamily):
        self.__tunefamily = tunefamily
        return self

    def getText(self):
        return self.__text

    def setText(self, text):
        self.__text = text
        return self

    def getMelstring(self):
        return self.__melstring

    def setMelstring(self, melstring):
        self.__melstring = melstring
        return self

    def getField(self, key):
        val = get_safe_value_from_dict(self.__dict__, key.lower(), default="")
        return val

    def setField(self, key, val):
        try:
            self.__dict__[key.lower()] = val
        except:
            print("EsacInfo has no field '{}'".format(key))
            pass
        return self

    def __eq__(self, other):
        if isinstance(other, type(None)):
            return False
        for v in self.__dict__:
            if self.__dict__[v] != other.__dict__[v]:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "\n".join([
          "Collection:  " + get_NA_str(self.collection),
          "Mel-ID:      " + get_NA_str(self.melid),
          "EsAC-ID:     " + get_NA_str(self.esacid),
          "Title:       " + get_NA_str(self.title),
          "Key:         " + get_NA_str(self.key),
          "Unit:        " + get_NA_str(self.unit),
          "Signature:   " + get_NA_str(self.signature),
          "Source:      " + get_NA_str(self.source),
          "Region:      " + get_NA_str(self.region),
          "Function:    " + get_NA_str(self.function),
          "Comment:     " + get_NA_str(self.comment),
          "CNR:         " + get_NA_str(self.cnr),
          "Tunefamily:  " + get_NA_str(self.tunefamily),
          "Text:        " + get_NA_str(self.text)
          ])

    collection  = property(getCollection, setCollection)
    melid       = property(getMelid, setMelid)
    esacid      = property(getEsacid, setEsacid)
    title       = property(getTitle, setTitle)
    region      = property(getRegion, setRegion)
    function    = property(getFunction, setFunction)
    comment     = property(getComment, setComment)
    cnr         = property(getCnr, setCnr)
    source      = property(getSource, setSource)
    key         = property(getKey, setKey)
    unit        = property(getUnit, setUnit)
    signature   = property(getSignature, setSignature)
    tunefamily  = property(getTunefamily, setTunefamily)
    text        = property(getText, setText)
    melstring   = property(getMelstring, setMelstring)
