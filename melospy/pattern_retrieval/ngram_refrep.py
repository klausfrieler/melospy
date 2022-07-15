""" Class implementation of NGramRefRepository, part of the NGram-Database subproject"""

#from ngram import *
#from ngram_list import *
#from ngram_partition import *
import random

from .ngram_position import *


class NGramRefRepository(object):
    
    def __init__(self, valtype):
        """ Initialize module """
        self.__rep = []
        self.__keys = []
        self.__valtype = valtype
        
    def add(self, seq, key=None, updateCodeBook=True):        
        if not (isinstance(seq, list) or isinstance(seq, str)): 
            raise ValueError("NGramRefRepository only for non-empty lists of non-empty standard lists.")
        if len(self.__rep) == 0:
            self.__rep = [seq]
            self.buildCodeBook()
            self.setType()
        else:
            if len(seq) == 0:
                #raise ValueError("Sequence empty")
                #print "Sequence empty"
                return self
            if self.__types  != self.parse_type(seq[-1]):
                raise TypeError("New sequence does not match repository")
            self.__rep.append(seq)
            if updateCodeBook:
                self.updateCodeBook(seq)
        if key == None:
            key = len(self.__rep)
        self.__keys.append(key)
        return self
        
    def extend(self, seq_rep, keys=None):    
        if keys:
            for i, r in enumerate(seq_rep):
                self.add(r, keys[i], updateCodeBook=False) 
        else:
            for r in seq_rep:
                self.add(r, updateCodeBook=False) 
        self.buildCodeBook()
        return self

    def total_count(self, ngram_length=1):
        assert(ngram_length>=1)
        tc = 0
        for n in self.__rep:
            if ngram_length <= len(n):
                tc += len(n)-ngram_length+1
        #tc = sum(len(_) for _ in self.__rep) - (ngram_length-1)*len(self.__rep)
        #print tc
        return tc
        
    def getRep(self):
        return self.__rep

    def getCodebook(self):
        return self.__codeBook

    def getValtype(self):
        return self.__valtype

    def getDict(self):
        assert(len(self.__keys) == len(self.__rep))
        ret = {self.__keys[i]:self.__rep[i] for i in range(len(self.__rep))}
        return ret

    def getKeys(self):
        return self.__keys
        
    def setKeys(self, keys):
        if len(set(keys)) != len(keys):
            raise ValueError("Tags contains duplicate elements or do no match in length (Should be {}, but is {})".format(len(self), len(set(keys))))
        self.__keys = keys
        #print "Keys:", self.__keys

    def transformKeys(self, trans_func):
        for i in range(len(self.__keys)):
            self.__keys[i] = trans_func(self.__keys[i])
        return self
        
    def getIdFromKey(self, key):
        idx = None
        try:
            idx = self.__keys.index(key)
        except:
            pass
        return idx 

    def getKeyFromId(self, seqid):
        key = None
        try:
            key = self.__keys[seqid]
        except:
            pass
        #print "Keys:", self.__keys
        return key

    def getNameFromId(self, seqid, def_name=""):
        try:
            name = str(self.getKeyFromId(seqid))
        except:
            name  = def_name
        if len(name) == 0:
            name = str(seqid)
        #print "Seqid, Name:", seqid, name
        return name

    def getSequenceByKey(self, key):
        idx = self.getIdFromKey(key)
        if idx != None:
            return self.__rep[idx]        
        return None

    def filter_by_ngrams(self, ngram_bag, lengthOffset=0, indexOffset=0):
        new_rep = NGramRefRepository(self.valtype)
        for ngram in ngram_bag:
            for npos in ngram:
                real_start = npos.startid + indexOffset
                real_end = npos.endid + lengthOffset
                #print "real_start: {}, real_end: {}".format(real_start, real_end)
                #print len(self.__rep)-npos.seqid
                #print len(self.__rep[npos.seqid])
                seq = self.__rep[npos.seqid][real_start:(real_end+1)]
                #key = self.getKeyFromId(npos.seqid) + "_" + str(npos.startid)
                key = NGramPosition(npos.seqid, npos.startid, npos.N)
                #print "Key: ", key
                new_rep.add(seq, key)
        #print new_rep
        return new_rep
        
    def buildCodeBook(self):
        self.__codeBook = {}
        maxCode = 0
        for seq in self.__rep:
            for el in seq:
                if el not in list(self.__codeBook.values()):
                    self.__codeBook[maxCode] = el
                    maxCode += 1
        #print "Codebook:", self.__codeBook
                    
    def updateCodeBook(self, seq):
        maxCode = len(self.__codeBook)
        for el in seq:
            if el not in list(self.__codeBook.values()):
                self.__codeBook[maxCode] = el
                maxCode += 1

    def getCodedSequence(self, seqid):
        inv_codebook = dict((v, k) for k, v in list(self.__codeBook.items()))
        ret = [inv_codebook[k] for k in self.__rep[seqid]]
        return ret
        
    def setType(self):
        self.__types = self.parse_type()

    def getType(self):
        return self.__types
        
    def parse_type(self, el=None):
        if not el:
            el = self.__rep[0][0]
        tmp_types = [type(el).__name__]
        if isinstance(el, str):
            return tmp_types
        try:
            for t in el:
                tmp_types.append(type(t).__name__)
        except:
            pass            
        return tmp_types
        
    def exportText(self, filename):
        with open(filename, "w") as textfile:
            textfile.writelines(str(self))
            
    def sample(self, count=0):
        tmp = []
        for vec in self:
            tmp.extend(vec)
        if count <= 0:
            return tmp
        ret = [random.choice(tmp) for _ in range(count)]
        return ret             
        
    def __str__(self):        
        s = "\n".join(["{}:{}".format(self.__keys[k], self.__rep[k]) for  k in range(len(self.__rep))])            
        return s
        
    def __len__(self):
        return len(self.__rep)

    def __getitem__(self, i):
        return self.__rep[i]
        
    
    rep         = property(getRep)
    keys        = property(getKeys)
    dict        = property(getDict)
    valtype     = property(getValtype)
    codebook    = property(getCodebook)
