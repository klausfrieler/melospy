import random

from melospy.pattern_retrieval.ngram_database import *


class NGramDBCache(object):

    def __init__(self):
        self.dbs = {}

    def set(self, key, ngramDB):
        self.dbs[key] = ngramDB

    def get(self, key):
        return self.dbs[key]

    def __getitem__(self, key):
        return self.get(key)

class SimulateNGramDB(object):

    def __init__(self, verbose=False, seed=None):
        #self.cache = NGramDBCache()
        self.verbose = verbose
        self.seed = seed

    def make_random_rep(self, sample, valtype, count=100, elements=100, type="plain"):
        ret = []
        if isinstance(elements, list):
            count == len(elements)
        else:
            elements = [elements for _ in range(count)]
        for i in range(count):
            ret.append([random.choice(sample) for _ in range(elements[i])])
        if type == "plain":
            return ret
        nr = NGramRefRepository(valtype)
        nr.extend(ret)
        return nr

    def simulate(self, ngram_db, maxN, transform, sample_len=0,
                 display_name ="SIMUL", average_elems=True):
        #try:
        #   ndb = self.cache[transform]
        #   if self.verbose:
        #       print "Found simulated db in cache for " + transform
        #   return ndb
        #except:
        #    pass
        random.seed(self.seed)
        rep = ngram_db.getRep()
        valtype = ngram_db.getRep().valtype
        sample = rep.sample(sample_len)
        if self.verbose:
            print("Len sample:", len(sample))
            print("Position count:", ngram_db[0].positionCount())
        count = len(rep)
        if average_elems:
            elements = int(round(float(sum([len(v) for v in rep]))/count, 3))
        else:
            elements = [len(v) for v in rep]

        if self.verbose:
            print("Count:{}, elements: {}, maxN = {}, transform = {}".format(count, elements, maxN, transform))

        new_rep = self.make_random_rep(sample, valtype, count, elements, type="full")
        new_rep.setKeys([display_name + "_" + str(i) for i in range(count)])

        if self.verbose:
            print("Rep keys:", new_rep.getKeys())
            print("Building simulation database...")
        ndb = NGramDatabase(new_rep, maxN=maxN, transform=transform)

        #self.cache.add(transform, ndb)
        if self.verbose:
            print("Done.")
        return ndb


    def simulate2(self, ngram_db, maxN, transform, order, display_name="SIMUL"):
        random.seed(self.seed)
        if self.verbose:
            print("Simulating NGramDB for '{}' with maxN = {} using Markov process of order {}".format(transform, maxN, order))
        #try:
        #   ndb = simulated_dbs[(transform, order)]
        #   print "Found simulated db in cache for " + transform
        #   return ndb
        #except:
        #    pass
        element_lengths = [len(v) for v in ngram_db.getRep()]
        count = len(element_lengths)
        new_rep = NGramRefRepository(ngram_db.getRep().valtype)
        for i in range(count):
            if self.verbose:
                print("Simulating vector #{} with  {} elements...".format(i, element_lengths[i]))
            start = time.process_time()
            vec = ngram_db.simulate_seq_markov(length=element_lengths[i], order=order)
            dt = (time.process_time()-start)
            if self.verbose:
                print("... done in {}s ({} s per element)".format(round(dt, 3), round(dt/element_lengths[i], 5)))
            new_rep.add(vec)
        #print "Count:{}, elements: {}, maxN = {}, transform = {}".format(count, elements, maxN, transform)

        new_rep.setKeys([display_name + "_" + str(i) for i in range(count)])
        #print "Rep keys:", new_rep.getKeys()
        if self.verbose:
            print("Building Markov-based simulation database ({}:{})...".format(transform, maxN))
        ndb = NGramDatabase(new_rep, maxN=maxN, transform=transform)
        #simulated_dbs[(transform,order)] = ndb
        if self.verbose:
            print("Done.")
        return ndb
