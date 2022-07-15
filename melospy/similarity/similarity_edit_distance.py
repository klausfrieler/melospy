""" Class for similarity based on edit distance """
import numpy as np


def delta_fun(v1, v2):
    return int(v1 != v2)
    
class SimilarityEditDistance(object):
    
    def __init__(self, ins_del_cost=1, sub_cost=delta_fun):
        self.ins_del_cost = ins_del_cost
        self.sub_cost = sub_cost 
    
    def process(self, vec1, vec2, method="ed"):
        ed = self.editDistance(vec1, vec2)
        return 1. - np.float(ed)/np.float(self.ins_del_cost*max([len(vec1), len(vec2)]))

    def editDistance(self, vec1, vec2):
        """ Implementation of the Edit-distance taken from http://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python, 13.07.2013 """
        one_ago = None
        #print "|".join([str(v) for v in vec1])
        #print "|".join([str(v) for v in vec2])
        this_row = list(range(1, len(vec2) + 1)) + [0]
        #print this_row
        for x in range(len(vec1)):
            two_ago, one_ago, this_row = one_ago, this_row, [0] * len(vec2) + [x+1]
            for y in range(len(vec2)):
                del_cost = one_ago[y] + self.ins_del_cost
                ins_cost = this_row[y-1] + self.ins_del_cost
                sub_cost = one_ago[y-1] + self.sub_cost(vec1[x], vec2[y])
                #print "del: {}, ins: {}, sub: {}".format(del_cost, ins_cost, sub_cost)
                this_row[y] = min(del_cost, ins_cost, sub_cost)
            #print this_row
        return this_row[len(vec2) - 1]
