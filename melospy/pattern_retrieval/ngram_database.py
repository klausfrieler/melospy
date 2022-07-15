""" Class implementation of NGramDatabase, part of the NGram-Database subproject"""

import time
from math import log

from melospy.pattern_retrieval.genre import *
from melospy.pattern_retrieval.ngram import *
from melospy.pattern_retrieval.ngram_list import *
from melospy.pattern_retrieval.ngram_partition import *
from melospy.pattern_retrieval.ngram_position import *
from melospy.pattern_retrieval.ngram_refrep import *


class NGramDatabase(object):

    def __init__(self, seq_rep=None, maxN=30, transform="", build=True, verbose=True, proc_hooks=None):
        """ Initialize module """
        if  seq_rep and not isinstance(seq_rep, NGramRefRepository):
            if not isinstance(seq_rep, list):
                raise ValueError("NGramDatabase only for non-empty lists/strings of non-empty standard lists/strings.")
            if len(seq_rep) == 0:
                raise ValueError("Repository empty.")
            if not (isinstance(seq_rep[0], list) or isinstance(seq_rep[0], str)):
                raise ValueError("NGramDatabase only for non-empty lists of non-empty standard lists.")
            if not all(seq_rep):
                raise ValueError("Empty element in repository.")

        self.__pruned   = 0
        self.__rep      = seq_rep
        self.maxN     = maxN
        self.effMaxN  = maxN
        self.__list     = []
        self.verbose = verbose
        self.__transform = transform
        self.proc_hooks = proc_hooks

        if seq_rep and build:
            self.build()
            self.setPositionFreq()

    def getPruned(self):
        return self.__pruned

    def setPruned(self, pruned):
        self.__pruned = pruned
        return self

    def getTransformation(self):
        return self.__transform

    def setTransformation(self, transform):
        self.__transform = transform
        return self

    def build(self):
        return self.fast_build()

    def add(self, ngramlist):
        N = ngramlist.getN()
        if N > self.maxN:
            raise ValueError("maximal N = {}, got {}".format(self.maxN, N))
        if len(self.__list) == 0:
            if N != 1:
                raise ValueError("expected NGramList of N = 1, got {}".format(N))
        else:
            lastN = self.__list[-1].getN()
            if N != lastN+1:
                raise ValueError("expected NGramList of N={}, got {}".format(lastN+1, ngramlist.getN()))
            lastRep = self.__list[-1].getRep()
            if lastRep != ngramlist.getRep():
                raise ValueError("Repository of new element does not match")

        self.__list.append(ngramlist)
        self.setPositionFreq()
        return self

    def unsafe_add(self, ngramlist):
        self.__list.append(ngramlist)
        self.setPositionFreq()
        return self

    def build_unigrams(self, sort=True):
        #build unigrams
        self.__list = []
        if self.verbose:
            print("Building unigrams...")
        nl = NGramList(1, self.__rep)
        #t = Timer()
        #t.start()
        if self.proc_hooks and "database" in self.proc_hooks:
            self.proc_hooks["database"](1, self.maxN)
        for i in range(len(self.__rep)):
            #print "Checking... ", i
            seq = self.__rep[i]
            for j in range(len(seq)):
                ngram_pos = NGramPosition(i, j, 1)
                nl.addNGramPosition(ngram_pos, safe=False)

        #t.end(msg="Done. {} melodies".format(len(self.__rep)))

        if len(nl) != 0:
            #print "N = 1\n=====\n{}".format(nl)
            if sort:
                nl.sortByFreq()
            self.__list.append(nl)

    def fast_build(self, sort=True):
        self.__list = []
        if self.__rep == None or len(self.__rep) == 0:
            raise ValueError("No repository given")
        #build unigrams
        self.build_unigrams(sort=sort)
        #nl = NGramList(1, self.__rep)
        #for i in range(len(self.__rep)):
        #    seq = self.__rep[i]
        #    for j in range(len(seq)):
        #        ngram_pos = NGramPosition(i, j, 1)
        #        nl.addNGramPosition(ngram_pos)

        #if len(nl) != 0:
            #print "N = 1\n=====\n{}".format(nl)

        #self.__list.append(nl)
        #return
        for N in range(2, self.maxN+1):
            if self.verbose:
                print("Building {}-grams...".format(N))
                #pass
            if self.proc_hooks and "database" in self.proc_hooks:
                self.proc_hooks["database"](N, self.maxN)
            nl = NGramList(N, self.__rep)
            last = self.__list[-1]
            #print len(last)
            offset = 0
            for ngram in last:
                #print "="*15
                #print ngram.getValue()
                tmp_token = []
                offset = len(nl)
                for pos in ngram:
                    #print "*"*15
                    #print "Checking pos: {} ({})".format(pos, pos.getValue(self.__rep))
                    tok = self.get_next_token(pos.seqid, pos.startid, N)
                    #print "Next token: {}".format(tok)
                    if tok == None:
                        continue
                    newpos = NGramPosition(pos.seqid, pos.startid, N)
                    if not tok in tmp_token:
                        tmp_token.append(tok)
                        new_ngram = NGram(N, self.__rep)
                        new_ngram.unsafe_add(newpos)
                        nl.add(new_ngram)
                        #print "Added new ngram: {}".format(new_ngram)
                    else:
                        i = tmp_token.index(tok)
                        #print "Found: {}, {}".format(i, (nl[i+offset]))
                        nl[i+offset].add(newpos)
                    #print "Tokens: {}".format(tmp_token)
                    #print "#NGrams: {}".format(len(nl))
            if len(nl) != 0:
                #print "N = {}\n=====\n{}".format(N, nl)
                if sort:
                    nl.sortByFreq()
                self.__list.append(nl)

    def prune(self, minOccur=2):
        for i, nl in enumerate(self.__list):
            if i == 0:
                continue
            nl.prune(minOccur)
        self.__pruned = minOccur-1
        self.setEffectiveMaxN()
        return self

    def setPositionFreq(self):
        for nl in self.__list:
            nl.setPositionFreq()
            #print "Setting freq\n", nl[0][0]
        return self

    def find(self, value, incremental=True):
        if value is None or len(value) == 0 or len(value)>self.maxN:
            return None
        n = self.__list[len(value)-1].find(value)
        if not n and self.__pruned > 0 and incremental:
            n = self.findIncremental(value)

        return n

    def findSuffixes(self, value, suffixlen=1):
        """ find all suffixes with extra len suffix len for value"""
        return self.findInfixes(value, infixlen=suffixlen, suffix=True)

    def findPrefixes(self, value, prefixlen=1):
        """ find all prefixes with extra len 'prefixlen' for 'value'"""
        return self.findInfixes(value, infixlen=prefixlen, suffix=False)

    def findInfixes(self, value, infixlen=1, suffix=True):
        """ find all suffixes or prefixes with extra len 'infixlen' for 'value'"""
        if suffix:
            return self.findEnvelope(value, prefixlen=0, suffixlen=infixlen)
        else:
            return self.findEnvelope(value, prefixlen=infixlen, suffixlen=0)

    def findEnvelope(self, value, prefixlen=1, suffixlen=1):
        """ find all suffixes or prefixes with extra len 'infixlen' for 'value'"""
        assert suffixlen >= 0
        assert prefixlen >= 0
        common = NGramBag(self.__rep)
        total_len = len(value) + prefixlen + suffixlen
        if total_len > self.maxN:
            return common

        ngram_pos = self.find(value)
        if not ngram_pos:
            #print "Value not found!"
            return None

        nl = self.__list[total_len-1]
        for n in nl:
            if suffixlen > 0:
                val = n.getValue()[prefixlen:-suffixlen]
            else:
                val = n.getValue()[prefixlen:]

            if val == value:
                #print "Found {}".format(n.getValue())
                common.add(n)

        #if we are pruned we have to add all ngrams with freq = 1 manually
        #well, nothing is for free....
        if self.__pruned > 0:
            values = [n.getValue() for n in common]
            for n in ngram_pos:
                startid = n.startid-prefixlen
                if startid < 0:
                    continue
                seqid = n.seqid
                try:
                    tmp_pos = NGramPosition(seq_id=seqid, start_id=startid, N=total_len, freq=1)
                    if tmp_pos.getValue(self.__rep) in values:
                        #print "Found {}".format(tmp_pos.getValue(self.__rep))
                        continue
                except:
                    continue
                ng = NGram(total_len, self.__rep)
                ng.add(tmp_pos)
                #print "Added ngram: {}".format(ng)
                common.add(ng)


        return common

    def genreSearch(self, pattern):
        #print "Pattern: ", pattern
        ef = EncoderFactory()
        encoder = ef.create(self.__rep.valtype)
        if encoder == None:
            raise RuntimeError("Invalid transform: '{}'".format(self.__transform))
        genre = GenRegExp(self.__rep.valtype, debug=False)
        #print "valtype", self.__rep.valtype
        genre.compile(pattern)
        #genreDebug = GenRegExp(self.__transform, debug=False)
        result = NGramBag(self.__rep)
        #print len(self.__rep)
        for seqid, seq in enumerate(self.__rep):
            #print "seq", seqid, seq
            if self.proc_hooks and "search" in  self.proc_hooks:
                self.proc_hooks["search"](seqid, len(self.__rep))
            for m in genre.finditer(seq):
                #print "m = ", m.start(), m.end()
                if m.end() == m.start():
                    continue
                ngrampos = NGramPosition(seqid, m.start(), m.end()-m.start())
                tag = ngrampos.getValue(self.__rep)
                ngrampos.setTag(tag)
                #print "genreSeach found:", ngrampos
                result.addNGramPos(ngrampos)
        #result.setPositionFreq()
        result.setPositionFrequencies(self.__rep)
        return result

    def findInRep(self, ngram_pos, val):
        ng      = None
        N       = len(val)
        seqid   = ngram_pos.seqid
        startid = ngram_pos.startid
        if startid < 0:
            return None
        seq  = self.__rep[seqid][startid:startid+N]
        #print "findInRep seq.", seq, "val: ",val
        if seq == val:
            ng = NGram(N, self.__rep)
            ng.add(NGramPosition(seqid, startid, N))
            #print "findInRep Found ", ng
        return ng

    def findIncremental(self, value):
        ret         = None
        lastfound   = None
        #print "findIncremental Value: ", value, " len: ", len(value)
        for i in range(len(value)):
            val = value[:i+1]
            #print "findIncrementalLoop Val: ", val
            found = self.find(val, incremental = False)
            if not found:
                if i == 0:
                    return None
                else:
                    #print "lastfound: ", lastfound
                    for npos in lastfound:
                        n = self.findInRep(npos, value)
                        if n:
                            return n
            else:
                lastfound = found
        return ret

    def getAPrioriProbability(self, value, use_log=True):
        if value is None or len(value) == 0:
            return 0.

        unigrams = self.__list[0]
        unigram_count = unigrams.positionCount()
        if unigram_count == 0:
            raise RuntimeError("NGramDatabase empty!")
        #print "Value:  {}".format(value)
        denom = 1.
        prob = 1.
        for v in value:
            tmp  = unigrams.find(v)
            #print "tmp:", v, tmp.value
            if tmp == None:
                return 1. if use_log else 0.
            freq = tmp.getFreq()
            if use_log:
                prob  += log(freq)
                denom += log(unigram_count)
            else:
                prob = prob * freq
                denom = denom * unigram_count
        ret = prob-denom if use_log else float(prob)/float(denom)
        return ret

    def getProbability(self, value):
        ngram = self.find(value)
        if ngram is None:
            return 0.
        l = len(value)-1
        ngram_count = self.__list[l].positionCount()
        freq = float(ngram.getFreq())
        #print "Value:  ", value
        #print "Ngramcount :", ngram_count
        #print "Freq:", freq
        return float(freq)/ngram_count

    def getExcessProbability(self, value, use_log=True):
        pv = self.getProbability(value)
        apv = self.getAPrioriProbability(value, use_log=False)
        if float_equal(apv, 0, prec=12):
            ratio = 1.0
            #print "APV:", value, pv, apv
        else:
            ratio = pv / apv
        if use_log:
            return log(ratio)
        return ratio

    def setEffectiveMaxN(self):
        self.effMaxN = len(self.__list)

    def getEffectiveMaxN(self):
        return len(self.__list)

    def is_built(self):
        return len(self.__list) != 0

    def getMaximalNGram(self, minN=None, minOccur=1, minSource=1):
        ng = []
        maxN = 0
        for i in range(len(self.__list)-1, -1, -1):
            nl = self.__list[i]
            tmp = [n for n in nl if len(n)>=minOccur and n.sourceCount()>=minSource]
            ng.extend(tmp)
            if not minN:
                if len(ng) > 0:
                    maxN = i+1
                    break
            else:
                if i < minN:
                    break
        if maxN > 0:
            print("Found {} patterns of length {}".format(len(ng), maxN))
        return ng


    def getMaximalNGramPartition(self, seqid, normalize=False, minN=1, minOccur=2, minSource=1):
        ngl = self.getMaximalNGram(minN=minN, minOccur=minOccur, minSource=minSource)
        #print "MxNGr\n", "\n".join([str(n) for n in ngl])
        ngrams = []
#        print "getMaximalNGramPartition\n", "="*15
#        print "-"*15
        tags = "abcdefghijklmnopqrstuvwxyz"
        i = 0
        #if self.verbose:
        #    print "Testing seqid {} for minN = {}".format(seqid, minN)
        for i, n in enumerate(ngl):
            #if self.proc_func:
            #    self.proc_func(i, len(ngl))
            if not n.containsSequenceId(seqid):
                continue
            subngram = False
            #print "-"*15
            #print "Testing: {}".format(n.getValue())
            for tmp in ngrams:
#                print "vs: {}".format(tmp.getValue())
                #print n, tmp
                if n.isSubNGram(tmp):
                    subngram = True
#                    print "Real subngram"
                    break
            if not subngram:
#                print "{} Added".format(n.getValue())
                if (i//26 + 1)<4:
                    n.setTag(tags[i % 26]*(i//26 + 1))
                else:
                    n.setTag("{}{}".format(tags[i % 26], i//26 + 1))
                i += 1
                ngrams.append(n)
#            else:
#                print "{} not added".format(n.getValue())
        if len(ngrams)==0:
            #print "No max. ngrams found or invalid seqid: {}".format(seqid)
            if normalize:
                return NGramPartition(self.__rep, seqid, minN, self.maxN, minOccur, minSource)
            else:
                return []
        comp = []
        for n in ngrams:
            comp.append(n.filterBySeqId(seqid))
        #print "post check"
        for i in range(len(comp)):
            if len(comp[i])==0:
                continue
            #print "Testing: ", comp[i]
            for j in range(len(comp)-1, i, -1):
                if len(comp[j])==0:
                    continue
                #print "vs ", comp[j]
                for pos_i in comp[i].getPositions():
                    for pos_j in comp[j].getPositions():
                        if pos_i.contains(pos_j):
                            comp[j].remove(pos_j)
                            #print "removed ", pos_j, pos_i
        #freq_ret = []
        ret = []
        for i in range(len(comp)):
            if len(comp[i])>0:
                ngrams[i].propagateFreq()
                ret.append(ngrams[i])
                #freq_ret.append(freq[i])
        #print "before norm", "\n".join([str(p) for p in ret])
        if normalize:
            part = NGramPartition(self.__rep, seqid, minN, self.maxN, minOccur, minSource, ngram_database=self)
            for n in ret:
                n.propagateTag()
                part.extend(n.getPositions())
            #print "norm\n", "\n".join([str(p)+ ":" + str(p.getValue(self.__rep)) for p in part])
            ret = part
        return ret

    def get_followers(self, ngram_bag):
        ret = []
        for npos  in ngram_bag:
            try:
                ret.append(self.__rep[npos.seqid][npos.startid + npos.N])
            except:
                pass
        if len(ret) > 0 and isinstance(ret[0], str):
            ret = "".join(ret)
        return ret

    def get_next_token(self, seq_id, start_id, N):
        if start_id + N > len (self.__rep[seq_id]):
            return None
        return self.__rep[seq_id][start_id + N-1]

    def getRep(self):
        return self.__rep

    def setRep(self, refrep):
        self.__rep = refrep
        return self

    def simulate_seq_markov(self, length, order=1):
        #start = time.process_time()
        vec = []
        if not self.is_built():
            raise RuntimeError("Cannot simulate with unbuilt database")
        unigrams = self[0]
        for i in range(length):
            if len(vec)< order:
                start = time.process_time()
                element = unigrams.sample()[0]
                #print "Sample unigram took {}s".format(time.process_time()-start)
                if isinstance(element, str) and i == 0:
                    vec = ""
                    vec += element
                if self.verbose:
                    print("Took element {} from unigrams".format(element))
            else:
                start = time.process_time()
                env = self.find(vec[-order:])
                #env = self.findSuffixes(vec[-order:], 1)
                #print "find suffix took {}s".format(time.process_time()-start)
                if env == None or len(env) == 0:
                    if self.verbose:
                        print("Could not find suffix for {}".format(vec[-order:]))
                    element = unigrams.sample()[0]
                    if self.verbose:
                        print("Took element {} from unigrams".format(element))
                else:
                    if self.verbose:
                        print("Len: ", len(env))
                        print("|".join(["{}:{}".format(_.getValue(self.refrep), _.freq) for _ in env]))
                    start = time.process_time()
                    #ngram = env.sample()[0]
                    #element = ngram[-1]
                    followers = self.get_followers(env)
                    #print followers
                    #print "getting followers from NGRam Bag took{}s".format(time.process_time()-start)
                    if len(followers)>0:
                        element = random.choice(followers)
                    else:
                        element = unigrams.sample()[0]
                    if self.verbose:
                        print("Took element {} from suffix".format(element))
            if isinstance(element, str):
                vec += element
            else:
                try:
                    vec.append(element[0])
                except:
                    vec.append(element)

        return vec

    def printStatistics(self):
        print("Vectors in repository: {}".format(len(self.__rep)))
        print("max N: {}".format(self.maxN))
        if len(self.__list) == 0:
            print("Database not yet built")
            return
        tmpMax = self.maxN
        if len(self.__list)<=tmpMax:
            tmpMax = len(self.__list)
        total = 0
        for i in range(1, tmpMax+1):
            print("Different N-grams of length {}:{}".format(i, len(self.__list[i-1])))
            total += len(self.__list[i-1])
        print("Total No. of different N-grams {}".format(total))

    def exportText(self, filename, melody_rep=None, indexOffset=0):
        first = True
        for nl in self.__list:
            if self.verbose:
                print("Writing NGramlist with N = {}".format(nl.getN()))
            if first:
                nl.exportText(filename, append=False, melody_rep=melody_rep, indexOffset=indexOffset)
                first = False
            else:
                nl.exportText(filename, append=True, melody_rep=melody_rep, indexOffset=indexOffset )

    def __str__(self):
        s = "\n=====\n".join([str(nl) for nl in self.__list])
        return s

    def __getitem__(self, i):
        return self.__list[i]

    transform   = property(getTransformation, setTransformation)
    pruned      = property(getPruned, setPruned)
    refrep      = property(getRep)
