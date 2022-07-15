""" Class implementation of NGramBag. General container of NGrams"""
from melospy.basic_representations.jm_util import symbolic_period_detection
from melospy.pattern_retrieval.ngram import *
from melospy.pattern_retrieval.ngram_position import *


class NGramBag(object):
    """General Container for NGrams """

    def __init__(self, seq_rep=None):
        """ Initialize module """
        self.__list = []
        self.__rep = seq_rep

    def getRep(self):
        return self.__rep

    def getList(self):
        return self.__list

    def add(self, ngram):
        """
        Adds a NGram instance, no checks

        Args:
            ngram: NGram instance
        Ret:
            self
        """
        self.__list.append(ngram)
        #print "Added new Ngram {}:{} to list".format(newNgram.getValue(), str(ngram_pos))
        return self

    def addNGramPos(self, ngrampos):
        ngram = self.find(ngrampos.getValue(self.__rep))
        if ngram != None:
            #print "Found in NGramBag"
            ngram.add(ngrampos)
            #print  ngram
        else:
            #print "Not found in NGramBag"
            ngram = NGram(ngrampos.N, self.__rep)
            ngram.add(ngrampos)
            self.add(ngram)
            #print "Added:", ngram
        return self

    def extend(self, ngrams):
        """
        Adds list of NGrams, no checks.

        Args:
            ngrams: List of NGrams instances
        Ret:
            self
        """
        for n in ngrams:
            self.__list.append(ngram)
        #print "Added new Ngram {}:{} to list".format(newNgram.getValue(), str(ngram_pos))
        return self

    def prune(self, minOccur=2):
        """
        Remove all ngrams with frequency less than minOccur. Modifies object.

        Args:
            minOccur: minimum frequency
        Ret:
            self
        """
        self.__list= [n for n in self.__list if n.getFreq()>=minOccur]
        return self

    def find(self, value):
        """
        Find a certain NGram value.

        Args:
            value: value to find
        Ret:
            NGram: first NGram that matches value
            None: if value could not be found
        """
        if self.__list == None or len(self.__list) == 0:
            return None

        if isinstance(self.__list[0].getValue(), list)\
            and not isinstance(value, list):
            value = [value]
        for n in self.__list:
            if n.getValue() == value:
                return n
        return None

    def filter(self, filter_function):
        """
        Filter internal list of NGrams by a externally defined
        filter_function. Modifies current NGramBag!

        Args:
            filter_function: Boolean function that returns False for elements
            to keep.
        Ret:
            self
        """

        ret = []
        for n in self:
            #print "N: ", n.getValue(self.__rep)
            #print "Filtered: ", filter_function(n)
            if not filter_function(n):
                ret.append(n)
        self.__list = ret
        return self

    def filter_by_positions(self, ngram_pos, mode="match"):
        allowed_modes = ["match", "find", "exclude"]
        if mode not in allowed_modes:
            raise ValueError("Invalid mode: {}".format(mode))

        if not isinstance(ngram_pos, list):
            ngram_pos = [ngram_pos]
        #print "filter_by_positions called. mode:", mode
        ret = NGramBag(self.__rep)
        pos_dict = self.get_ngram_pos_dict()
        pos_dict_keys = set(pos_dict.keys())
        test_pos_list = [(npos.seqid, npos.startid, npos.N) for npos in ngram_pos]
        result_keys = []
        if mode == "match":
            result_keys = pos_dict_keys.intersection(set(test_pos_list))
        else:
            for n in pos_dict:
                for npos_test in ngram_pos:
                    if pos_dict[n].contains(npos_test):
                        result_keys.append(n)
        #print "Result keys:", result_keys
        if mode == "exclude":
            result_keys = pos_dict_keys.difference(set(result_keys))
            #print "Result keys:", result_keys
        for key in result_keys:
            ret.addNGramPos(pos_dict[key])

        return ret

    def get_ngram_pos_dict(self):
        ret = {}
        for n in self:
            for npos in n:
                key = (npos.seqid, npos.startid, npos.N)
                ret[key] = npos
        return ret


    def filterTrills(self, min_period=2, max_period=2):

        def is_trill(vec, min_period=min_period, max_period=max_period):
            period = symbolic_period_detection(vec.getValue(), max_period=max_period)
            #print "Period: ", period
            if period>=min_period and period<=max_period:
                return True
            return False

        return self.filter(is_trill)

    def getMaxWeightNGram(self, minSource=2, threshold=None):
        maxPat = []
        maxW = 0
        for n in self:
            if n.sourceCount()<minSource:
                continue
            pw = n.getWeight()
            v = {abs(v) for v in n.getValue()}
            #print "N:", n.getValue(), "V:", v
            if v == {1, 2} or v == {1}:
                continue
            #if pw>0:
            #    print "NGram:", n, " pattern weight:", pw
            if threshold != None:
                if pw >= threshold:
                    maxPat.append(n)
            else:
                if pw > maxW:
                    maxPat = [n]
                    maxW = pw
                    #print "Nex Max NGram:", n, " pattern weight:", pw
        return maxPat

    def sortByFreq(self):
        """
        Sort Ngram positions by
            - descending freq
            - descending N
            - ascending startid
        in that order
        """
        #print "Before:\n", self
        self.__list = sorted(self.__list, key=lambda p: (-p.freq, -p.N))
        #print "After:\n", self
        return self

    def setPositionFreq(self):
        for n in self.__list:
            n.propagateFreq()
            #print "NGramlist settint freq\n", str(n[0])
        return self

    def setPositionFrequencies(self, nrefrep=None):
        for n in self.__list:
            total_count = 0
            if nrefrep != None:
                total_count = nrefrep.total_count(n.N)
            #print "Total count", total_count, n.value, len(nrefrep)
            if total_count != 0:
                n.propagateFrequencies(total_count)
            else:
                n.propagateFreq()
            #print "NGramlist settint freq\n", str(n[0])
        return self

    def exportText(self, filename, melodyRep=None, append=False, indexOffset=0, separateRecords=False, melFilter=None):
        first = True
        for n in self.__list:
            if first:
                n.exportText(filename, append=append, melodyRep=melodyRep, indexOffset=indexOffset, separateRecords=separateRecords, melFilter=melFilter)
                first = False
            else:
                n.exportText(filename, append=True, melodyRep=melodyRep, indexOffset=indexOffset, separateRecords=separateRecords, melFilter=melFilter )

    def exportMIDI(self, filename, melodyRep, append=False, gap=2, indexOffset=0, lengthOffset=0):

        notetrack = NoteTrack()
        for n in self.__list:
            nt = n.exportNotetrack(melodyRep, gap=gap, indexOffset = indexOffset, lengthOffset = lengthOffset)
            notetrack.concat(nt, gap=gap)
        midi_writer = MIDIWriter()
        try:
            midi_writer.writeMIDIFile(notetrack, filename)
        except:
            raise
        print("Successfully written {} with {} elements from {} ngrams and {} positions".format(filename, len(notetrack), len(self), self.positionCount()))

    def positionCount(self):
        """
        Sum all lengths of all NGrams in the bag

        Args:

        Ret:
            Integer sum
        """
        return sum([len(n) for n in self])

    def sample(self, count=1):
        ret = []
        sample_space = []
        for i, n in enumerate(self):
            sample_space.extend([i]*n.freq)
        idz = [random.choice(sample_space) for _ in range(count)]
        for i in idz:
            ret.append(self[i].getValue())
        return ret

    def __len__(self):
        """Number Ngrams in the NgramBag"""
        return len(self.__list)

    def __str__(self):
        s = "\n-------\n".join([str(n) for n in self.__list])
        return s

    def __getitem__(self, i):
        return self.__list[i]


    """ Properties """
    rep     = property(getRep)
    list    = property(getList)
