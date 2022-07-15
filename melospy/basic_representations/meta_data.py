""" Class for Meta Data"""

class MetaData(object):
    """ Abstract base class for all sorts of meta data as part of a song"""

    def __init__(self):
        pass

    #sub classes should override this to give access to their sub classes of actual information
    def getInfoTypes(self):
        return []

    def getSubInfo(self, name):
        if name in self.getInfoTypes():
            getter = "self.get" + name + "()"

            return eval(getter)
        else:
            raise ValueError("Unknown Sub-Info: "  + str(name))

    def getField(self, name):
        infos = self.getInfoTypes()
        for i in infos:
            obj = self.getSubInfo(i)
            #print "Searching for {} in {} for {}, self:{}".format(name, type(obj), i, type(self))
            if hasattr(obj, name) or hasattr(obj, "__" +name):
                #if i ==  "CompositionInfo":
                #    print "Info: {}, : Field: {}".format(i, "_" + i + "__" + name)
                return obj.__dict__["_" + i + "__" + name]
                #return eval(getter)

        raise ValueError("Field '{}' not found.".format(name))

    def setField(self, name, val):
        infos = self.getInfoTypes()
        for i in infos:
            obj = self.getSubInfo(i)
            if hasattr(obj, name):
                #print "Found {} in {} for val {}".format(name, i, val)
                #print "Getter: {}, val: {}".format(getter, eval(getter))
                obj.__dict__["_" + i + "__" + name] = val
                #eval(setter)
                #print repr(obj.__dict__)
                return self
        raise ValueError("Field '{}' not found.".format(name))
