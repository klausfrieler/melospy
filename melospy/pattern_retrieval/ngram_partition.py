""" Class implementation of NGram-Partition"""
import csv
from math import log

import melospy.basic_representations.jm_util as jm_util
from melospy.basic_representations.melody import *
from melospy.pattern_retrieval.ngram import *
from melospy.pattern_retrieval.ngram_position import *

from . import intspan

#import numpy as np

class NGramPartition(object):
    """Container list for ngram-positions from a partition"""

    def __init__(self, seq_rep=None, seqid=None, minN=0, maxN=0, minOccur=0, minSource=0, ngram_database=None):
        """ Initialize module """
        self.__list = []
        self.__rep = seq_rep
        self.__seqid = seqid
        self.maxN = maxN
        self.minN = minN
        self.minOccur = minOccur
        self.minSource = minSource
        self.ngram_database = ngram_database

    def add(self, ngram_pos, sort=False):
        """ Adds a ngram_pos. Either finds in list or adds new element"""
        #print "Try adding {} to list of {}".format(str(ngram_pos), len(self))
        if len(self) == 0:
            if self.__seqid == None or ngram_pos.seqid == self.__seqid:
                self.__list.append(ngram_pos)
                self.__seqid = ngram_pos.seqid
        else:
            if ngram_pos.seqid == self.__seqid and ngram_pos not in self.__list:
                self.__list.append(ngram_pos)
                #print "added: ", ngram_pos
                if sort:
                    self.sort()
                #print "Added {} to list".format(str(ngram_pos))
        return self

    def extend(self, ngram_positions):
        """ extends partition by a list of ngram_positions"""
        #print "{}, {},  {}".format(str(ngram_pos),  self.__rep[ngram_pos.seqid], len(self.__rep[ngram_pos.seqid]))
        for n in ngram_positions:
            self.add(n)
        self.sort()
        return self

    def unsafe_add(self, ngram):
        """ adds a at ngram_pos, without checking anything"""
        self.__list.append(ngram)
        #print "Added new Ngram {}:{} to list".format(newNgram.getValue(), str(ngram_pos))
        return self

    def getSeqId(self):
        return self.__seqid

    def removeDoubleIds(self):
        """ Remove all NGrams with same startid and smaller length and  freq"""
        self.sort()
        remove = [False for _ in range(len(self))]
        for i  in range(len(self)-1):
            if self[i].startid == self[i+1].startid:
                remove[i+1] = True
        tmp =[]
        for i in range(len(remove)):
            if not remove[i]:
                tmp.append(self[i])
        self.__list = tmp
        return self

    def sort(self):
        """ Sort Ngram positions by ascending startids, descending N and descending freq (in that order)"""
        #print "Before:\n", self
        self.__list = sorted(self.__list, key=lambda p: (p.startid, -p.N, -p.freq))
        #print "After:\n", self
        return self

    def findByTag(self, tag):
        ret =[n for n in self.__list if n.tag == tag]
        return ret

    def findByValue(self, ngram_pos):
        ret =[]
        #print "Searching:{}".format(ngram_pos.getValue(self.__rep))
        for n in self.__list:
            if n.getValue(self.__rep) == ngram_pos.getValue(self.__rep):
                #print "Found :{}, {}".format(n, n.getValue(self.__rep))
                ret.append(n)
        return ret

    def innerFreq(self, val):
        ret =[]
        if isinstance(val, str):
            ret = self.findByTag(val)
        elif isinstance(val, NGramPosition):
            ret = self.findByValue(val)
        else:
            raise ValueError("Expected tag or NGram position, got {}".format(type(val)))
        #print "Call innerFreq", val, " len", len(ret)
        return len(ret)

    def getList(self):
        return self.__list

    def getSeqRep(self):
        return self.__rep

    def exportCSV(self, filename, melody, indexOffset = 0, lengthOffset = 0):
        onsets = melody.getOnsets()
        durations = melody.getDurations()
        with open(filename, 'w') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',', lineterminator="\n", quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for n in self.__list:
                start_onset = onsets[n.startid + indexOffset]
                end_onset   = onsets[n.endid +lengthOffset + indexOffset]
                max_dur     = durations[n.endid + lengthOffset + indexOffset]
                dur = end_onset + max_dur - start_onset
                value = str(n.tag)
                label = n.N
                row = [ start_onset, dur, value, label]
                csvwriter.writerow(row)


    def getStats(self, prec=3):
        name = self.__rep.getNameFromId(self.__seqid)
        notecount   = len(self.__rep[self.__seqid])

        if len(self) == 0:
            #print "I am so empty...."
            patcount    = 0
            coverage    = 0
            avg_N       = 0
            avg_overlap = 0
            over_cover  = 0
            log_excess_prob = 0.
        else:
            patcount    = len(self)
            coverage    = round(self.coverage(), prec)
            avg_N       = round(self.averageN(), prec)
            avg_overlap = round(self.averageOverlap(), prec)
            over_cover  = round(self.overCoverage(), prec)
            log_excess_prob = round(self.excessProbability(use_log=True), prec)

        return [name, notecount, self.minN, self.maxN, self.minOccur, self.minSource, patcount, coverage, avg_N, avg_overlap, over_cover, log_excess_prob]

    def exportStats(self, filename, melodyRep, append=False, sep=";", ngram_db=None):
        mode = "a" if append else "w"

        if mode == "w":
            with open(filename, mode) as textfile:
                textfile.write("id;note_count;min_N;max_N;min_occur; min_source;pattern_count;coverage;avg_N;avg_overlap;over_coverage;log_excess_prob\n")
                mode = "a"

        with open(filename, mode) as textfile:
            #name = self.__rep.getKeyFromId(self.__seqid)
            #if len(name) == 0:
            #    name = self.__seqid
            #notecount   = len(self.__rep[self.__seqid])
            #print "Name: {}, notecount: {}".format(name, notecount)
            #stats   = [name, notecount]
            #tmp     = self.getStats(prec = 5)
            #stats.extend(tmp)
            stats = self.getStats(prec = 5)
            row = sep.join([str(v) for v in stats])+ "\n"
            #print "Row: ", row
            textfile.write(row)

    def exportText(self, filename, append=False, melodyRep=None, indexOffset=0,  separateRecords=False, melFilter=None, sep="|"):
        mode = "a" if append else "w"
        if mode == "w":
            with open(filename, mode) as textfile:
                if melodyRep:
                    textfile.write("id;tag;start;N;freq;metricalpos;value\n")
                else:
                    textfile.write("id;tag;start;N;freq;value\n")
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
                    row = "{}{}{}{}{}{}{}{}{}{}{}{}{}\n".format(name, sep, n.tag, sep, n.startid, sep, n.N, sep, n.freq, sep, str(mp), sep, str(n.getValue(self.__rep)))
                else:
                    n.setTag(self.__rep.getKeyFromId(n.seqid))
                    row = "{}{}{}{}{}{}{}{}{}{}{}\n".format(name, sep, n.tag, sep, n.startid, sep, n.N, sep, n.freq, sep, str(n.getValue(self.__rep)))

                textfile.write(row)
            if separateRecords:
                textfile.write("-"*80+"\n")

    def _get_name_from_rep(self, seqid):
        try:
            name = self.__rep.getKeyFromId(seqid)
        except:
            name  = ""
        if len(name) == 0:
            name = str(seqid)
        return name

    def full_export(self, melodyRep, indexOffset=0, lengthOffset=0):
        ret = []
        for n in self.__list:
            melody = melodyRep[n.seqid] if melodyRep else None
            name = self._get_name_from_rep(n.seqid)

            if melody:
                mp = melody[n.startid + indexOffset].getMetricalPosition()
            else:
                mp = None

            real_start = n.startid + indexOffset
            real_end = n.endid + lengthOffset + indexOffset

            if melody:
                start_onset, dur = melody.getRegionFromIDs(real_start, real_end)
            else:
                start_onset, dur = 0, 0
            value = n.getValue(self.__rep)
            tag = n.tag
            row = [name,
                   real_start,
                   real_end,
                   n.N,
                   start_onset,
                   dur,
                   mp,
                   value,
                   tag]
            ret.append(row)
        return ret

    def exportText2(self, filename, melody = None, indexOffset = 0, sep = "|"):
        with open(filename, 'w') as textfile:
            for n in self.__list:
                if melody:
                    mp = melody[n.startid + indexOffset].getMetricalPosition()
                    row = "{}{}{}{}{}\n".format(str(n), sep, str(mp), sep, n.getValue(self.__rep))
                else:
                    row = "{}{}{}\n".format(str(n), sep, n.getValue(self.__rep))

                textfile.write(row)

    def toIntSpan(self):
        ret = IntSpan()
        for n in self:
            ret.add(n.toIntSpan())
        return ret

    def coverage(self, items = None):
        if items == None:
            items = IntSpan(list(range(len(self.__rep[self.__seqid]))))
        #print "items:", items
        #print "self: ", self.toIntSpan()
        #print "cover:", self.toIntSpan().coverage(items)
        return self.toIntSpan().coverage(items)

    def averageN(self):
        return float(self.lengthSum())/len(self)

    def averageOverlap(self):
        sum = 0
        if len(self)<=1:
            return 0
        for i in range(len(self)-1):
            ispan1 = self[i].toIntSpan()
            ispan2 = self[i+1].toIntSpan()
            sum += len(ispan1.intersection(ispan2))
        return float(sum)/(len(self)-1)

    def lengthSum(self):
        return sum([_.N for _ in self.__list])

    def overCoverage(self):
        if len(self)==0:
            return 0
        return self.lengthSum()/(self.coverage()*len(self.__rep[self.__seqid]))-1.0

    def excessProbability(self, use_log=True):
        if len(self)==0 or self.ngram_database == None:
            return 0
        ret = 0
        for n in self:
            pv = self.ngram_database.getProbability(n.getValue(self.__rep))
            apv = self.ngram_database.getAPrioriProbability(n.getValue(self.__rep), use_log =False)
            ep = self.ngram_database.getExcessProbability(n.getValue(self.__rep), use_log=use_log)
            #print "N: {}, p= {}, p_0 = {}, log(p/p_0)={}".format(n.getValue(self.__rep), pv, apv, ep)
            ret += ep
        return ret/len(self)

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
        #print debug

        self.__list = ret
        return self

    def filterTrills(self, min_period=2, max_period=2, strict=True, transform=None):

        def is_trill(vec, min_period=min_period, max_period=max_period, transform=transform):
            #print "="*60
            tmp = vec.getValue(self.__rep)
            tolerance = 1.0 if strict else 1./(len(tmp)-2)
            val = jm_util.is_trill(tmp, min_period, max_period, tolerance, transform)
            return val
            #period = symbolic_period_detection(tmp, max_period=max_period, tolerance=tolerance)
            #if period>=min_period and period<=max_period:
            #    if transform == "interval":
            #        s = sum(vec[0:period])
            #        if s == 0:
            #            return True
            #    else:
            #        return True
            #return False
        #print "found trill filter", min_period, max_period, strict, transform
        return self.filter(is_trill)

    def filterScales(self, transform, directed=True, mode="scale"):

        def is_scale_like(vec, transform=transform, directed=directed, mode=mode):
            #print "="*60
            tmp = vec.getValue(self.__rep)
            return jm_util.is_scale_like(tmp, transform.lower(), mode=mode)

        if transform.lower() not in ["interval", "pitch"]:
            print("Unsupported transform for scale-filter: {}".format(transform))
            return self
        return self.filter(is_scale_like)

    def filterArpeggios(self, transform, directed=True):
        return self.filterScales(transform, directed, mode="arpeggio")

    def __len__(self):
        """Len of an Ngram is the number of occurences in the repository"""
        return len(self.__list)

    def __str__(self):
        s = "\n-------\n".join([str(n) for n in self.__list])
        return s

    def __getitem__(self, i):
        return self.__list[i]

    """ Properties """
    seqid   = property(getSeqId)
