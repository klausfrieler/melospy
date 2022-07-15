""" Class implementation of NGramPosition, part of the NGram-Database subproject"""

from .intspan import *


class NGramPosition(object):

    def __init__(self, seq_id= None, start_id=None, N=None, tag="", freq=None, prob=None):
        """ Basic object of the NGram module.
            A NGramPosition is defined with respect to a repository of sequences,
            which must be externally provided and maintained,
            A NGramPosition is defined by the id of a sequence in the
            repository, the start id in this sequence and the
            length N. For convenience an NGramPosition can also get
            a tag and store its frequency of occurence in the repository.
        """
        self.__seq_id   = seq_id
        self.__start_id = start_id
        self.__N        = N
        self.__tag      = tag
        self.__freq     = freq
        self.__prob     = prob

    def getSeqId(self):
        return self.__seq_id

    def setSeqId(self, seq_id):
        self.__seq_id = seq_id
        return self

    def getStartId(self):
        return self.__start_id

    def setStartId(self, start_id):
        self.__start_id = start_id
        return self

    def getEndId(self):
        return self.__start_id+self.__N-1

    def getN(self):
        return self.__N

    def setN(self, N):
        if N != None and N<=0:
            raise ValueError("N must be >0, found {}".format(N))
        self.__N = N
        return self

    def getTag(self):
        return self.__tag

    def setTag(self, tag):
        self.__tag = tag
        return self

    def getFreq(self):
        return self.__freq

    def setFreq(self, freq):
        if freq != None and freq<=0:
            raise ValueError
        self.__freq = freq
        return self

    def getProbability(self):
        return self.__prob

    def setProbability(self, prob):
        #print "setProbability called"
        if not prob or prob<=0:
            raise ValueError
        self.__prob = prob
        return self

    def setFrequencies(self, freq, totalCount):
        #print "setFrequencies called"
        if not totalCount or totalCount <= 0:
            raise ValueError("Total count must be positive integer, got {}".format(totalCount))
        self.__freq = freq
        self.__prob = float(freq)/float(totalCount)
        #print float(freq)/float(totalCount), freq, totalCount
        return self

    def getValue(self, seq_rep):
        if len(seq_rep[self.__seq_id]) < self.__start_id + self.__N:
            raise RuntimeError("NGram position {} too long.".format(str(self)) )
        return seq_rep[self.__seq_id][self.__start_id:self.__start_id+self.__N]

    def flatten(self, with_tag=True):
        flat = [n.seqid, n.startid, n.N, n.freq]
        if with_tag:
            flat.append(n.tag)
        return flat

    def hasOverlap(self, ngram_pos):
        return self.overlap(ngram_pos) != 0

    def overlap(self, ngram_pos):
        """
        Checks if a NGramPosition has overlap with the current
        NGramPosition.
        Args:
            ngram_pos: NGramPosition object
        Returns:
            Amount of overlap (number of elements in intersection)
        """
        if self.__seq_id != ngram_pos.__seq_id:
            return 0
        ispan1 = IntSpan.from_start_length(self.startid, self.N)
        ispan2 = IntSpan.from_start_length(ngram_pos.startid, ngram_pos.N)
        overlap = len(ispan1.intersection(ispan2))
        return overlap

    def contains(self, ngram_pos):
        """
        Checks if a NGramPosition is fully contained in current NGramPosition.

        Args:
            ngram_pos: NGramPosition object
        Returns:
            True: if ngram_pos is contained
            False: otherwise
        """
        if self.__seq_id != ngram_pos.__seq_id:
            return False
        ispan1 = IntSpan.from_start_length(self.startid, self.N)
        ispan2 = IntSpan.from_start_length(ngram_pos.startid, ngram_pos.N)
        #fully contained if intersection equals second int span
        contained = len(ispan2) == len(ispan1.intersection(ispan2))
        return contained

    def containsNGrams(self, ngram):
        """
        Checks if an NGram is fully contained in current NGramPosition.

        Args:
            ngram: NGram object
        Returns:
            True: if all NGramPositions of NGram are contained
            False: otherwise
        """
        found  = 0
        for pos in ngram:
            if self.contains(pos):
                found += 1
        return found == len(ngram)

    def toIntSpan(self):
        return IntSpan("{}-{}".format(self.startid, self.getEndId()))

    def coord_eq(self, ngram_pos):
        """
        Checks if two NGramPositions have the same starting point in the same sequence

        Args:
            ngram_pos: NGramPosition object
        Returns:
            True: if coordinate are equal (N can be different)
            False: otherwise
        """
        return self.__seq_id == ngram_pos.__seq_id and self.__start_id == ngram_pos.__start_id

    def get_onset_and_duration(self, melodyRep, indexOffset=0):
        melody = melodyRep[self.getSeqId()]
        onset = melody[self.getStartId() + indexOffset].getOnset()
        offset = melody[self.getStartId() + self.getN() - 1].getOffset()
        duration = offset - onset

        return onset, duration

    def __str__(self, sep="|"):
        vals  = [self.__seq_id, self.__start_id,  self.__N, self.__tag, self.__freq, self.__prob]
        s = sep.join([str(_) for _ in vals])
        s = s.replace("None", "--")
        return s

    def __eq__(self, ngram_pos):
        if ngram_pos == None:
            return False
        return self.__seq_id == ngram_pos.__seq_id\
                and self.__start_id == ngram_pos.__start_id\
                and self.__N == ngram_pos.__N

    def __ne__(self, ngram_pos):
        return not self.__eq__(ngram_pos)

    """ Properties """
    seqid   = property(getSeqId, setSeqId)
    startid = property(getStartId, setStartId)
    N       = property(getN, setN)
    endid   = property(getEndId)
    tag     = property(getTag, setTag)
    freq    = property(getFreq, setFreq)
    prob    = property(getProbability, setProbability)
    value   = property(getValue)
