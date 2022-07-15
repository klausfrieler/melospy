""" GenRegExp Class, for generalized regular expressions
    Helper class for unicode translation of melody transformations
"""    

import re


class GenreException(Exception):
    def __init__(self, msg):
        self.msg = msg
        
class IntegerToUnicode(object):

    def __init__(self, offset=256, minval=-128):
        self.offset = offset
        self.minval = minval

    def __call__(self, intvec):
        if not isinstance(intvec, list):
            intvec = [intvec]
        coded = "".join([chr(int(round(v)) - self.minval + self.offset) for v in intvec])
        return coded

class CharacterToUnicode(object):

    def __init__(self, offset=256):
        self.offset = offset
        self.minval = chr('A')
        pass        

    def __call__(self, string):
        if not isinstance(string, list):
            string = [string]
        coded = "".join([chr(int(round(v))-self.minval+self.offset) for v in intervals])
        return coded

class IntegerToString(object):

    def __init__(self):
        pass        

    def __call__(self, intvec):
        if not isinstance(intvec, list):
            intvec = [intvec]
        coded = "".join([str(v) for v in intvec])
        return coded

class CharacterToString(object):

    def __init__(self):
        pass        

    def __call__(self, string): 
        return string

class EncoderFactory(object):

    def __init__(self, debug=False):
        self.debug = debug

    def create(self, valtype):
        if  valtype == "int":
            #print "EF: other"
            if self.debug:
                return IntegerToString()
            return IntegerToUnicode()
        elif  valtype == "string":
            #print "EF: cdpc"
            if self.debug:
                return CharacterToUnicode()
            return CharacterToString()
        else:
            raise ValueError("Invalid value type: '{}'".format(valtype))
        return None
                            
class GenRegExp(object):

    def __init__(self, valtype=None, debug=False):
        self.debug = debug
        self.encoder = EncoderFactory(debug=debug).create(valtype)
        self.pattern = ""

    def compile(self, genregexp):
        tmp = []
        #print type(self.encoder)
        for v in genregexp:
            if isinstance(v, int):
                #print "int"
                tmp.append(self.encoder(v))
            else:
                #print "no int"
                tmp.append(str(v))
        #print "compile", tmp
        tmp = r"".join(tmp)
        self.pattern = tmp
        try:
            self.genre = re.compile(tmp, re.UNICODE)
        except Exception as e:
            raise GenreException(str(e.args[0]))
            
    def finditer(self, vector):
        coded = self.encoder(vector)
        #print coded
        return self.genre.finditer(coded)        
