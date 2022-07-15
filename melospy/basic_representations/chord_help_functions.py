""" Help functions for chord processing """

import re


def findListItemInStringAfterSortingListInDescendingItemLengthOrder(s, l):
    """ 
    1) Sorts list in descending order its item lengths.
    2) Step through list and find first appearance of list item as substring
    in a given string.
    
    Example: Given the list ['b5', '', 'sus', '#5', 'm'] that contains 
    chord triad labels, we want to look for '' (representing major chords) 
    last, since this will always be found and therefore should be checked for last.
    """
    sortedValues = sorted(l, key = len, reverse = True)
    #sortedValues = l
    #print str(sortedValues)
    #print "Checking String: "+ s
    s = s.lower()
    for val in sortedValues:
        #print str(val) + " Len " + str(len(val)) 
        #return "nope"
        if isinstance( val, str ):
            #print "String: " + str(val)
            val = val.lower()
            if s.find(val)>-1:
                return val
        if isinstance( val, list):
            #print "List: " + str(val)
            for v in val:
              v = v.lower()
              #print str(v) + ": "+str(s.find(v))              
              if s== v:
                #print "Found!" + v
                return v;
    return None
