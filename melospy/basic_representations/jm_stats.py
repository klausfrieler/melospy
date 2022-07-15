from functools import cmp_to_key
from math import atan2, copysign, cos, exp, floor, log, pi, sin, sqrt

import numpy as np


def circ_mean(fVec):
    s = [sin(f*2*pi) for f in fVec]
    c = [cos(f*2*pi) for f in fVec]

    return atan2(mean(s), mean(c))/2/pi

def mean_frac(fVec):
    return circ_mean([x-floor(x) for x in fVec])

def circ_stats(vec, circ_max=None, axis=None):
    #see https://en.wikipedia.org/wiki/Directional_statistics

    if np.ma.isMaskedArray(vec) and vec.mask.shape!=():
        N = np.sum(~vec.mask, axis)
    else:
        if axis is None:
            N = vec.size
        else:
            N = vec.shape[axis]

    if N == 0:
        return (None, None, None, None, None)

    if circ_max != None:
        circ_max = np.float32(circ_max)
        vec = vec/circ_max*2*np.pi

    im = np.mean(np.sin(vec), axis)
    re = np.mean(np.cos(vec), axis)
    NAN = None
    INF = None
    #NAN = np.nan
    #INF= np.inf
    if abs(im)<np.finfo(np.float).eps and abs(re)<np.finfo(np.float).eps:
        theta = NAN
    else:
        theta = np.arctan2(np.mean(np.sin(vec), axis), np.mean(np.cos(vec), axis))
    #print vec
    R = np.sqrt(np.sum(np.sin(vec), axis)**2 + np.sum(np.cos(vec), axis)**2)/N
    V = 1.-R
    S = np.sqrt(-2*np.log(R)) if R>np.finfo(np.float).eps else INF
    delta = (1-R*R)/(2*R*R) if R>np.finfo(np.float).eps else INF
    if theta != NAN:
        inv_theta = circ_max*theta/2/np.pi
        if inv_theta<0:
            inv_theta += circ_max
    else:
        inv_theta = NAN
    return (inv_theta, R, V, S, delta)


def simple_histogram(vec, order="None", density=False, counts_only=False):
    from .jm_util import get_huron_code
    if vec is None:
        return None
    N = len(vec)+.0
    if N <= 0:
        return None
    factor = 1.0/N if density else 1.
    values = list(np.unique(np.ravel(vec)))       # get ALL unique values
    if isinstance(vec, np.ndarray):
        vec = list(vec.flatten())
    hist = [(v, vec.count(v)*factor) for v in values]

    order = order.lower()[0:3]
    if order =="inc":
        hist.sort(key=cmp_to_key(lambda x, y: -get_huron_code(x[1], y[1])))
    elif order =="dec":
        hist.sort(key=cmp_to_key(lambda x, y: get_huron_code(x[1], y[1])))
    if counts_only:
        hist = [v[1] for v in hist]

    return hist

def entropy(vec, unit="norm", n_classes=None):
    """ Computes entropy of raw data. """

    #print N, counts, probs#
    probs = simple_histogram(vec, density=True, counts_only=True)

    if probs is None:
        return None
    if n_classes is None:
        n_classes = len(probs)

    if n_classes <= 1:
        return 0.

    ent = 0.
    factor = 1.
    if unit == "bit":
        factor = 1.0/np.log(2)
    elif unit == "norm":
        factor = 1.0/np.log(n_classes)
    # Compute standard entropy.
    # add eps against division by zero
    probs = probs + np.finfo(float).eps
    ent = -1.0*np.sum(probs*np.log(probs))*factor
    return ent

def harmonic_mean(vec):
    if vec is None or len(vec) == 0:
        raise ValueError("Expected numerical vector")
    ret = len(vec)/np.sum(1./np.array(vec))
    return ret

def geometric_mean(vec):
    if vec is None or len(vec) == 0:
        raise ValueError("Expected numerical vector")
    ret = pow(np.prod(vec), 1.0/len(vec))
    return ret

def flatness(vec, decibel=False):
    """
        Computes 'spectral' flatness of raw nominal data as ratio of the
        harmonic mean to the arithmetic mean of the histogram.
    . """

    #print N, counts, probs#
    probs = simple_histogram(vec, density=True, counts_only=True)

    if probs is None:
        return None

    probs = probs + np.finfo(float).eps
    num = geometric_mean(probs)
    denom = mean(probs)
    flatness = num/denom
    if decibel:
        flatness = np.log10(flatness)
    return flatness

def mode(vec):
    """ computes mode of a numpy array"""
    counts= simple_histogram(vec, order="dec")
    if counts is None:
        return None
    modes = [counts[0]]
    for i in range(1, len(counts)):
        if counts[i][1] >= modes[0][1]:
            modes.append(counts[i])
        else:
            break
    if len(modes)>1:
        return np.array([c[0] for c in modes])
    return modes[0][0]

def mean(x):
    if len(x) == 0:
       return None
    return float(sum(x))/len(x)

def median(x):
    return np.median(x)

def var(x):
    sum1 = 0
    sum2 = 0
    N = len(x)
    if N <= 1:
        return None
    for i in range(N):
        v = float(x[i])
        sum1 += v
        sum2 += v*v
    return sum2/(N-1) - sum1*sum1/N/(N-1)
    #return numpy.var(x, ddof = 1)

def sd(x):
    v = var(x)
    if v is None:
        return None
    from .jm_util import float_equal

    if v <= 0. or float_equal(abs(v), 0, prec=10):
        return 0
    return sqrt(v)
    #return numpy.std(x, ddof = 1)


def zipf_coefficient(vec):
    """
        Computes Zipf coefficient of a distribution via a linear regression
        of the log-log rank-ordered histogram
    """
    if vec is None or len(vec)==0 or np.unique(vec).size<2:
        return None
    hist = np.array(simple_histogram(vec, order="dec", counts_only=True))
    alpha = np.polyfit(np.log(np.arange(1, hist.size+1)), np.log(hist), 1)
    return -alpha[0]
