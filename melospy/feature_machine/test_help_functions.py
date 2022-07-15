""" Various auxiliary functions needed in the Melopy feature modules """

import numpy as np


def includesOnlyNumericItems(x):
    try:
        np.max(x)
        return True
    except (TypeError, ValueError, NotImplementedError):
        return False
        
def isEncapsulatedSequence(x):
    try:
        len(x[0])
    except (TypeError, IndexError):
        return False
    return True
    
    
def size(x):
    if includesOnlyNumericItems(x) and not isEncapsulatedSequence(x):
        return x.size
    else:
        return len(x)

def my_array_equal(v1,v2,epsilon=1e-10):
    """ Function compares two NumPy arrays for equality """
    return np.max(np.abs(v1-v2)) < epsilon

def get_nominal_histogram(inputVec):

    uniqueValues = []
    histVec = []
    coerced = False
    try:                
        tmpVec = [k.tolist() for k in inputVec]
        coerced = True
    except AttributeError:
        tmpVec = inputVec

    for i in range(len(tmpVec)):
        try:
            idx = uniqueValues.index(tmpVec[i])
            histVec[idx] += 1
        except ValueError:
            uniqueValues.append(tmpVec[i])
            histVec.append(1)

    if coerced:
        uniqueValues = [np.array(k) for k in uniqueValues]

    return histVec, uniqueValues
    
def dict_from_keys_vals(keys, vals):
    d = {}
    for i in range(len(keys)):
        v = None
        try:
            v = vals[i]
        except:
            pass
        d[keys[i]] = v
    return d

def entropy(vec, norm = False):
    histVec, uv = get_nominal_histogram(vec)
    if len(uv) == 0:
        return 0
    s = sum(histVec)
    probs = [v/s for v in histVec]
    H = -1.0*np.sum(p * np.log2(p) for p in probs) 
    if norm:
        H /= len(uv)
    return H

def unique(vec):
    """ Implements unique functionality for non-numeric lists / tuples """
    uniqueElems = []
    for item in vec:
        if item not in uniqueElems:
            uniqueElems.append(item)
    return uniqueElems
