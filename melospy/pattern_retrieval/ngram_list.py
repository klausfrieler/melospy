""" Class implementation of NGramList"""
import random

from melospy.pattern_retrieval.ngram import *
from melospy.pattern_retrieval.ngram_bag import *
from melospy.pattern_retrieval.ngram_position import *


class NGramList(NGramBag):
    """
        Container list for NGrams with a common N.
        Derives from NGramBag
    """

    def __init__(self, N=None, seq_rep=None):
        """ Initialize module """
        self.__N = N
        NGramBag.__init__(self, seq_rep)
        self.value_cache = {}

    def getN(self):
        return self.__N

    def setN(self, N):
        self.__N = N

    def addNGramPosition(self, ngram_pos, safe=False):
        """
        Adds NGramPosition object (Convenience method).
        Tries to find matching NGram in list, and adds NGramPosition to it.
        If no match is found, adds a new NGram with ngram_pos as member

        Args:
            ngram_pos (NGramPosition object)
                NGramPosition to add
        Returns:
            self
        """
        if self.__N != ngram_pos.N:
            raise RuntimeError("N: {} does not match: {}".format(ngram_pos.N, self.__N))
        #print "Adding {}, {},  {}".format(str(ngram_pos),  self.__rep[ngram_pos.seqid], len(self.__rep[ngram_pos.seqid]))
        cache_gram = None
        try:
            cache_gram = self.value_cache[self.billo_hash(ngram_pos.getValue(self.rep))]
        except:
            pass

        if cache_gram == None or len(self) == 0:
            newNgram = NGram(self.N, self.rep)
            if safe:
                newNgram.add(ngram_pos)
            else:
                newNgram.unsafe_add(ngram_pos)

            self.add(newNgram)
            self.value_cache[self.billo_hash(newNgram.value)] = newNgram
            #print "Added new Ngram {}:{} to list".format(newNgram.value, str(ngram_pos))
            #print self.value_cache
        else:
            if safe:
                cache_gram.add(ngram_pos)
            else:
                cache_gram.unsafe_add(ngram_pos)

            #print "Found {}:{} in list".format(cache_gram.value, str(ngram_pos))

        return self

    def setPositionFreq(self):
        totalCount = sum([len(ngram) for ngram in self])
        #print "N: {}, Totalcount: {}".format(self.__N, totalCount)
        for ngram in self:
            ngram.propagateFrequencies(totalCount)
            #print "NGramlist settint freq\n", str(n[0])
        return self

    def billo_hash(self, val):
        return "".join([str(_) for _ in val])


    """ Properties """
    N   = property(getN, setN)
