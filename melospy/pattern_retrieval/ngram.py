""" Class implementation of NGram"""
import os
from math import log

from melospy.basic_representations.note_event import *
from melospy.input_output.midi_writer import *
from melospy.pattern_retrieval.ngram_position import *
from melospy.pattern_retrieval.ngram_refrep import *

#import numpy as np

class NGram(object):
    """
    An Ngram is an abstract entity, based on some repository of sequences
    (lists). It's represented by list of NgramPositions which indicate,
    where the Ngram can be found in the repository. All NGramPositions
    point to the same value of the NGram (which is not explicitly stored!)

    The sequence repository should be NGramRefRepository object or a
    list of sequences

    """
    def __init__(self, N=None, seq_rep=None, tag=""):
        """ Initialize module """
        self.__N = N
        self.__list = []
        self.__rep = seq_rep
        self.__tag = tag

    def add(self, ngram_pos):
        """
        Adds a NGram_Position with a maximum of checks.
        NGramPosition is only added if not already contained, to ensure
        a list of unique elements

        Args:
            ngram_pos: A NGramPosition object
        Returns:
            self
        """
        if self.__N != ngram_pos.N:
            raise RuntimeError("N does not match current NGram")
        #print "{}, {},  {}".format(str(ngram_pos),  self.__rep[ngram_pos.seqid], len(self.__rep[ngram_pos.seqid]))
        if self.__rep:
            if (ngram_pos.startid+ngram_pos.N)>len(self.__rep[ngram_pos.seqid]):
                raise RuntimeError("NGram position extends over sequence end")
            if len(self) != 0 and self.getValue() != ngram_pos.getValue(self.__rep):
                raise RuntimeError("NGram position with value {} does not fit current NGram with value {}".format(self.getValue(), ngram_pos.getValue(self.__rep)))

        if self.containsPosition(ngram_pos):
            #print "Already in Ngram position list"
            return self
        self.__list.append(ngram_pos)
        return self

    def extend(self, ngram_pos_list):
        """
        Extends NGram with a list of NGramPositions with maximum checks.

        Args:
            ngram_pos_list: List of NGramPosition objects
        Returns:
            self
        """
        for npos in ngram_pos_list:
            self.add(npos)
        return self

    def unsafe_add(self, ngram_pos, really_unsafe=False):
        """
            Adds an NGramPosition. Unlike add, method does not check,
            if the NGramPosition is already in the list,
            but checks if the value fits. Introduced for speed.
        Args:
            ngram_pos: NGramPosition object
        Returns:
            self
        """
        if really_unsafe:
            self.__list.append(ngram_pos)
            return self

        if self.__rep and len(self) != 0 and self.getValue() != ngram_pos.getValue(self.__rep):
            raise RuntimeError("NGram positions {} with value '{}' does not fit current NGram with value".format(ngram_pos, ngram_pos.getValue(self.__rep), self.getValue()))
        self.__list.append(ngram_pos)
        return self

    def unsafe_extend(self, ngram_pos_list):
        """ Extends a ngram with a list of NGramPositions without safety check
        Args:
            ngram_pos_list: List of NGramPosition objects
        Returns:
            self
        """
        for npos in ngram_pos_list:
            self.unsafe_add(npos)
        return self

    def fits(self, ngram_pos):
        """
        Checks if the NGramPosition fits to the NGram.
        Introduced for speed.

        Args:
            ngram_pos: NGramPosition object
        Returns:
            True: if NGramPosition fits
            False: otherwise
        """
        if self.__N != ngram_pos.N:
            return False
        if self.getValue() == ngram_pos.getValue(self.__rep):
            return True
        return False

    def containsPosition(self, ngram_pos, strict=True):
        """
        Checks if the NGramPosition is already contained in list.
        This is also possible for a NGramPosition of different length,
        if flag 'strict' is not set.

        Args:
            ngram_pos: NGramPosition object
            strict: Flag, if lengths should match
        Returns:
            True: if NGramPosition is in internal list
            False: otherwise
        """
        if strict and self.__N != ngram_pos.N:
            return False
        for n in self.__list:
            #NGramPosition object operator == is overloaded
            if strict:
                if n == ngram_pos:
                    return True
            else:
                if n.coord_eq(ngram_pos):
                    return True
        return False

    def filterBySeqId(self, seqid):
        """
        Filter all NGramPosition that belong to a certain sequence

        Args:
            seqid: Id of sequence with respect to repository
        Returns:
            ret: NGram object
        """
        ret = NGram(self.N, self.__rep)
        for n in self.__list:
            if n.seqid == seqid:
                ret.unsafe_add(n)
        return ret

    def containsSequenceId(self, seqid):
        """
        Checks if NGram contains an NGramPosition
        that comes from to a certain sequence

        Args:
            seqid (int):
                Id of sequence with respect to repository
        Returns:
            **True**: if an NGramPosition for the seqid is found

            **False**: otherwise
        """
        for n in self.__list:
            if n.seqid == seqid:
                return True
        return False


    def hasOverlap(self, ngram):
        """
        Check if any NGramPosition in a NGram
        has overlap with any NGramPosition in the currecnt NGRam

        Args:
            ngram: NGram object
        Returns:
            True: if any overlap between any two NGramPositions is found
            False: otherwise
        """
        for n in self.__list:
            for m in ngram.__list:
                if n.hasOverlap(m):
                    return True
        return False

    def isSubNGram(self, ngram):
        """
        Check if an NGram is proper subset of current NGram.
        This is the case if all NGramPositions of ngram are contained
        in some NGramPOsition of the current NGram

        Args:
            ngram: NGram object
        Returns:
            True: if all NGramPositions in ngram are contained in current NGram
            False: otherwise
        """
        #print self
        #print ngram
        if self.__N > ngram.__N:
            return False
        if len(self.__list) != len(ngram.__list):
            return False
        found = 0
        for pos1 in self.__list:
            for pos2 in ngram.__list:
                #print "pos1:{}, pos2:{}, {}".format(pos1, pos2, pos2.contains(pos1))
                if pos2.contains(pos1):
                    found += 1
                    continue

        return found == len(ngram.__list)

    def remove(self, ngram_pos):
        """
        Remove NGramPosition, as compared by value.

        Args:
            ngram_pos: NGramPosition object to removed
        Returns:
            self
        """
        ret = []
        for n in self.__list:
            if n != ngram_pos:
                ret.append(n)
        self.__list = ret
        return self

    def sourceCount(self):
        """
        Count number of different sources for NgramPositions
        in this this NGram.

        Args:
        Returns:
            number of different source sequences
        """
        return len(set(self.getSeqIds()))

    def singleSource(self):
        """
        Check if all NGramPosition belonging to this NGram
        come fromt a sinlge source sequence in the repository

        Args:
            None
        Returns:
            True: if NGram is single sourced
            False: otherwise
        """
        return self.sourceCount() == 1

    def getSeqRep(self):
        return self.__rep

    def getList(self):
        return self.__list

    def getN(self):
        return self.__N

    def setN(self, N):
        self.__N = N
        return self

    def getFreq(self):
        return len(self.__list)

    def getProb(self):
        return self.__list[0].getProbability()

    def getWeight(self):
        return self.N * log(self.freq)

    def getTag(self):
        return self.__tag

    def setTag(self, tag):
        self.__tag = tag
        return self

    def setTagsAsSeqKey(self):
        if isinstance(self.__rep, NGramRefRepository):
            for n in self.__list:
                tag = self.__rep.getKeyFromId(n.getSeqId())
                n.setTag(tag)
        return self

    def getRepKeyFromId(self, seqid):
        return self.__rep.getKeyFromId(seqid)

    def getValue(self):
        if len(self) == 0 or self.__rep == None:
            return None
        return self.__list[0].getValue(self.__rep)

    def getSeqIds(self):
        seq_ids = [ngram.seqid for ngram in self.__list]
        return seq_ids

    def getStartIds(self):
        start_ids = [ngram.startid for ngram in self.__list]
        return start_ids

    def getPositions(self):
        return self.__list

    def setPositionTags(self, tag):
        for n in self.__list:
            n.setTag(tag)
        return self

    def getStats(self):
        stats = [self.getValue(), self.getN(), self.getFreq(), self.getProb(), self.sourceCount()]
        return stats

    def propagateFreq(self):
        for pos in self.__list:
            pos.setFreq(len(self))
        return self

    def propagateFrequencies(self, totalCount):
        for pos in self.__list:
            pos.setFrequencies(len(self), totalCount)
        return self

    def propagateTag(self):
        self.setPositionTags(self.__tag)
        return self

    def commonPositions(self, ngram):
        """
        Returns a list of common NGramPositions,
        checks only for coordinates.

        Args:
            ngram: NGram object
        Returns:
            List of NGramPositions
        """
        ret = []
        for n in self.__list:
            for m in ngram:
                if n.coord_eq(m):
                    ret.append(n)
        return ret

    def exportText(self, filename, append=False, melodyRep=None, indexOffset=0,  separateRecords = False, melFilter=None, sep ="|"):
        mode = "a" if append else "w"
        if mode == "w":
            with open(filename, mode) as textfile:
                if melodyRep:
                    textfile.write("id;start;N;freq;metricalpos;value\n")
                else:
                    textfile.write("id;start;N;freq;value\n")
                mode = "a"
        with open(filename, mode) as textfile:
            for n in self.__list:
                melody = melodyRep[n.seqid] if melodyRep else None
                name = self.__rep.getKeyFromId(n.seqid)
                if len(name) == 0:
                    name = n.seqid
                if melody:
                    if melFilter and melFilter(melody[n.startid + indexOffset]):
                        continue
                    mp = melody[n.startid + indexOffset].getMetricalPosition()
                    row = "{}{}{}{}{}{}{}{}{}{}{}\n".format(name, sep, n.startid, sep, n.N, sep, n.freq, sep, str(mp), sep, n.getValue(self.__rep))
                else:
                    n.setTag(self.__rep.getKeyFromId(n.seqid))
                    row = "{}{}{}{}{}{}{}{}{}\n".format(name, sep, n.startid, sep, n.N, sep, n.freq, sep, n.getValue(self.__rep))

                textfile.write(row)
            if separateRecords:
                textfile.write("-"*80+"\n")

    def exportSnippetList(self, filename,  melodyRep, refRep=None, append=False, indexOffset=0, lengthOffset=0):
        mode = "a" if append else "w"
        if mode == "w":
            with open(filename, mode) as textfile:
                textfile.write("id;startpos;endpos\n")
                mode = "a"

        if not refRep:
            refRep =  self.__rep
            if not refRep:
                raise RuntimeError("exportSnippets needs repository to work!")

        with open(filename, mode) as textfile:
            for n in self.__list:
                melody = melodyRep[n.seqid]
                start = melody[n.startid+ indexOffset].getOnset()
                end = melody[n.endid + indexOffset + lengthOffset].getOnset()+ melody[n.endid + indexOffset + lengthOffset].getDuration()
                filename = refRep.getKeyFromId(n.seqid)
                row = "{};{};{}\n".format(os.path.splitext(filename)[0], start, end)
                #print row
                textfile.write(row)

    def exportNotetrack(self, melodyRep, gap=2, indexOffset=0, lengthOffset=0):
        nt = NoteTrack()
        onset_offset = 0
        #print "Export Notetrack for {} positions with off=({},{})".format(len(self), indexOffset, lengthOffset)
        for n in self.__list:
            melody      = melodyRep[n.seqid]
            start       = melody[n.startid + indexOffset].getOnset()
            end         = melody[n.endid + indexOffset + lengthOffset].getOffset()
            total_dur   = end - start + gap
            for i in range(n.startid, n.endid + lengthOffset + 1):
                pitch = melody[i].getPitch()
                onset = melody[i].getOnset() - start + onset_offset
                duration = melody[i].getDuration()
                ne =  NoteEvent(pitch, onset, duration)
                nt.append(ne)
                #print "Added ({}, {}, {})".format(onset, pitch, duration)
            onset_offset = onset_offset + total_dur
            #print "New offset:", onset_offset
        #print "Len Notetrack: ", len(nt)
        return nt

    def exportStats(self, filename, append=False, sep =";"):
        mode = "a" if append else "w"
        if mode == "w":
            with open(filename, mode) as textfile:
                textfile.write("value;N;freq\n")
                mode = "a"

        with open(filename, mode) as textfile:
            stats = [self.getValue(), self.getN(), self.getFreq()]
            row = sep.join([str(v) for v in stats])+ "\n"
            #print "Row: ", row
            textfile.write(row)

    def filter(self, filter_function):
        """
        Filter internal list of NGramPosition by a externally defined
        filter_function. Changes current NGram

        Args:
            filter_function: Boolean function that returns False for elements
            to keep.
        Ret:
            self
        """

        ret = [n for n in self if not filter_function(n)]
        self.__list = ret
        return self

    def __len__(self):
        """
        Length of an Ngram is the number of occurences in the repository

        Args:
        Ret:
            Length of internal list (int)
        """
        return len(self.__list)

    def __eq__(self, ngram):
        """
        Two NGrams are defined as "equal" if their values coincide.

        Args:
            ngram: NGram to compare to
        Ret:
            Bool
        """
        if ngram == None or len(self) == 0 or self.__N != ngram.__N:
            return False
        v1 = self.getValue()
        v2 = ngram.getValue()
        if v1 != None and v2 != None:
            return v1 == v2
        #repository free version
        for ngram in self.__list:
            for ngram2 in ngram.__list:
                if ngram.seq_id  == ngram2.seq_id and ngram.start_id == ngram2.start_id:
                    return True
        return False

    def __ne__(self, ngram):
        return not self.__eq__(ngram)

    def __getitem__(self, i):
        return self.__list[i]

    def __str__(self):
        s = "\n".join([str(n) for n in self.__list])
        if len(self.__tag) == 0:
            return "Value: {}\n{}".format(self.getValue(), s)
        else:
            return "Tag:{}, value: {}\n{}".format(self.__tag, self.getValue(), s)

    """ Properties """
    N       = property(getN, setN)
    tag     = property(getTag, setTag)
    freq    = property(getFreq)
    value   = property(getValue)
