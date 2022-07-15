import datetime
import glob
import os
import time
from fractions import Fraction
from math import atan2, copysign, cos, exp, floor, log, pi, sin, sqrt


def cloner(val):
    try:
        cl = val.clone()
    except:
        cl = val
    return cl

def math_mod(p, n):
    m = p % n
    if m < 0:
        m = m + n
    return m

def is_list_of_int(loi):
    try:
        dummy = [int(v) for v in loi]
    except:
        return False
    return True

def string_to_dict(x, as_list=True):
    """Checks if x is a dict or can be converted to one"""
    if isinstance(x, dict):
        if as_list:
            return [x]
        else:
            return x
    if isinstance(x, list):
        return [string_to_dict(_, as_list=False) for _ in x]
    y = x.split(":")
    if len(y) > 1:
        val = {chomp(y[0]): str(chomp(y[1]))}
    else:
        val = str(chomp(y[0]))
    if as_list:
        val = [val]
    return val

def intersection(values, all_values):
    """Intersection of two list of possible different, but compatible type"""
    v = {str(__) for __ in values}
    av = {str(__) for __ in all_values}
    inters = v.intersection(av)

    return [v for v in inters ]

def index_list_to_binary_str(ind_l, max_N, offset=0, as_string=False):
    buffer = [0 for _ in range(max_N)]
    for i in ind_l:
        buffer[i-offset] = 1
    if as_string:
        buffer = "".join([str(_) for _ in buffer])
    return buffer

def powTwoBit(number):
    number = int(number)
    return (number & (number-1) == 0) and (number != 0)

def closest_power_of_two(val):
    """find closest power of 2,
        in case of two option returns lower value
    """
    ln = int(log(val, 2))
    diff1 = abs(2**ln -val)
    diff2 = abs(2**(ln+1)-val)

    if diff1<=diff2:
        return 2**ln
    return 2**(ln+1)

def purify_period_track(period_track):
    pure = False
    if period_track== None or len(period_track) == 0:
        return period_track

    while not pure:
        idz, periods= list(zip(*period_track))
        didz = diff(idz)
        bad = None
        #print "Idz, didz, periods", idz, didz, periods
        for i in range(len(didz)):
            if didz[i] % periods[i] != 0:
                bad = (i+1)
                break
        if bad == None:
            pure = True
            break
        period_track.pop(bad)
        #print "PT:", period_track
    has_doublets = True
    while has_doublets:
        idz, periods= list(zip(*period_track))
        bad = None
        for i in range(len(periods)-1):
            if periods[i] == periods[i+1]:
                bad = i+1
                break
        if bad == None:
            has_doublets = False
            break
        period_track.pop(bad)
    #print "Purified:", period_track
    return period_track

def rayleigh1(t,  beta=2):
    if float_equal(t[0], 0):
        return 0
    return (t[0], exp(-beta*log(t[0]/.5, 2)*log(t[0]/.5, 2)))

def rayleigh2(t, beta=2, t0=.5):
    if float_equal(t[0], 0.):
        return 0.
    return (t[0], t[1]*exp(-beta*log(t[0]/t0, 2)*log(t[0]/t0, 2)))

#import numpy
def gaussification(onsets, deltaT=0.01, sigma=.040, weights=None, start=None, end=None):
    if start == None:
        start= min(onsets)-2*sigma
    if end == None:
        end = max(onsets)+2*sigma

    #print "start= ", start, " end=", end
    if weights == None:
        weights = [1 for i in range(len(onsets))]

    assert(len(weights) == len(onsets))
    t = start
    times = []
    vals = []
    while t<end:
        factor = -.5/sigma/sigma
        tmp = [exp(factor * (t_ - t)* (t_- t)) for t_ in onsets]
        val = scalar_prod(weights, tmp)
        vals.append(val)
        times.append(t)
        #print "t = {} , val = {} ".format(t, round(val, 3))
        t += deltaT

    return list(zip(times, vals))

def scalar_prod(vec1, vec2):
    assert(len(vec1) ==len(vec2))
    return sum(p*q for p, q in zip(vec1, vec2))


def simmat2form(simmat, thresh1 = 0.8, thresh2 = 0.6):
    ret = ""
    l = len(simmat)

    assert len(simmat[0]) == l
    if l==1:
        return "A"
    form = ["*" for _ in range(l)]
    form_names = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxy"
    name_pointer = 0
    s = simmat
    for i in range(0, l-1):
        if form[i] == "*":
            if name_pointer>len(form_names)-1:
                return None
            form[i] = form_names[name_pointer]
            name_pointer += 1
        #print "-"*60
        #print form
        for j in range(i+1, l):
            #print "Testing: {},{}, s={}".format(i,j, s[i][j])
            if form[j] != "*" and form[j] != form[i]:
                #print "Cont", form[i]
                continue
            if s[i][j]>thresh1:
                form[j] = form[i]
                #print "B1: ", form
            elif s[i][j]>thresh2:
                form[j] = form[i] + "'"
                #print "B2: ", form
    if form[l-1] == "*":
        if name_pointer>len(form_names)-1:
            return None
        else:
            form[l-1] = form_names[name_pointer]
    return "".join(form)

def bit_log2(val):
    if (val & (val - 1)) != 0:
        return None

    for i in range(32):
        if (val >> i) & 0x01 == 1:
            return i
    return None

def unique(seq, idfun = None):
    # ripped from http://www.peterbe.com/plog/uniqifiers-benchmark
   # order preserving
   if idfun is None:
       def idfun(x): return x
   seen = {}
   result = []
   for item in seq:
       marker = idfun(item)
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result

def hash_list(x):
    return "+".join([str(k) for k in x])

def void(*args, **kwargs):
    pass

def multi_convert(value, types, default):
    try:
        len(types)
    except:
        types = [types]
    for t in types:
        try:
            val = t(value)
            return val
        except:
            pass
    return default

def get_safe_value_from_dict(dictionary, key, default=None, toLower=False, msg= ""):
    val  = None
    if msg == "":
        msg = "Key {} not found in {}."
    try:
        val = dictionary[key]
    except:
        if default is not None:
            return default
        else:
            raise KeyError(msg.format(key, dictionary))
    if toLower and isinstance(val, str):
        val = val.lower()
    return val

def prepend_to_keys(dictionary, prefix):
    return dict([(prefix+keys, dictionary[keys]) for keys in dictionary])

def repeater(vec, mults):
    if len(vec) != len(mults):
        raise ValueError("List and muliplicities of inequal length")
    ret = []
    for i in range(len(mults)):
        ret.extend([vec[i] for _ in range(mults[i])])
    return ret

def nPVI(vec, norm = False):
    v = vec
    n = len(vec)
    if n<2:
        return 0
    elsum = sum([abs(2*(v[i+1]-v[i])/(v[i+1]+v[i])) for i in range(n-1)])/(n-1)
    if norm:
        elsum = round(100*elsum)
    return elsum

def remove_runs(vec):
    ret = []
    i = 0
    while i < len(vec):
        if len(ret)==0 or vec[i] != ret[-1]+1:
            ret.append(vec[i])
        i += 1
    return ret

def simplify_list(vec, none_element=""):
    if vec == None or len(vec) == 0:
        return vec
    ret = [vec[0]]
    for i in range(1, len(vec)):
        if vec[i] == vec[i-1]:
            ret.append(none_element)
        else:
            ret.append(vec[i])
    return ret

def cycle_list(vec, start):
    if vec == None or len(vec) == 0:
        return vec
    N = len(vec)
    ret = [vec[(i + start) % N] for i in range(N)]
    return ret

def ensure_first_element(vec):
    if vec == None or len(vec) == 0:
        return vec

    if not vec[0]:
        for i in range(len(vec)):
            if vec[i]:
                first = vec[i]
                break
        try:
            vec[0] = first
        except:
            pass
    return vec

def symbolic_autocorrelation(vec, maxlag, norm = True):
    l = len(vec)
    if l<maxlag:
        maxlag = len(vec)-1
    ret = [l]
    for i in range(1, maxlag+1):
        equal = 0
        #print "i:", i
        for j in range(0, l-i):
            #print "i+j:",i+j, " j:", j
            #print "Test:", vec[i+j] == vec[j], " eq:", equal
            if vec[i+j] == vec[j]:
                equal += 1
        #print "e/l ", equal/l
        ret.append(float(equal))
    if norm:
        ret = [_/l for _ in ret]
    return ret

def symbolic_period_detection(vec, max_period=5, tolerance=1.0):

    #print "\n"+"*"*15
    l = len(vec)
    if l<2:
        return 0
    ac = symbolic_autocorrelation(vec, max_period, norm = False)
    #print "Vec:", vec, " Ac = ", ac, "max_P", max_period
    for i in range(1, min(len(ac), max_period+1)):
        #print l-i, tolerance*(l-i), ac[i], ac[i]>=tolerance*(l-i)
        if l-i and ac[i]>=tolerance*(l-i):
            return i
    return 0

def is_trill(vec, min_period, max_period, tolerance=1.0, transform=None):
    #print "="*60
    period = symbolic_period_detection(vec, max_period=max_period, tolerance=tolerance)
    #if period>0:
    #    print "Period: ", period
    #    print "Val:", vec.getValue(self.__rep)
    #    print "Ret: ", period>=min_period and period<=max_period
    if period>=min_period and period<=max_period:
        if transform == "interval":
            s = sum(vec[0:period])
            if s == 0:
                return True
        else:
            return True
    return False

def is_scale_like(vec, transform, directed=False, mode="scale"):
    supported_transforms = ["interval", "pitch"]
    if transform not in supported_transforms:
        raise ValueError("Unsuported transform: {}".format(transform))
    if len(vec)==0:
        return False

    #we work on intervals only, so convert pitch to intervals
    if transform == "pitch":
        vec = diff(vec)

    #A scale in this sense
    #consists of a sequence of 2 and 1 semitones intervals
    #checking for this discard sign of interval
    avec = [abs(v) for v in vec]
    offset = {"scale": 1, "pentatonic": "2", "arpeggio": 3}[mode]
    elements = sorted(set(avec))
    for i, e in enumerate(elements):
        if e != i + offset:
            return False

    if not directed:
        return True
    #if directed is soecified, alls intervals must have the same direction (sign)
    signs = [copysign(1, k) for k in vec]
    if abs(sum(signs)) != len(vec):
        return False
    return True



def get_huron_code(x,y, min_diff = 0):

    if round(abs(x-y))<=min_diff:
        return 0
    if x>y:
        return -1
    if x<y:
        return 1

def get_huron_code_raw(x, y):
    if abs(x-y)<=1e-15:
        return 0
    if x > y:
        return -1
    if x < y:
        return 1

def huron_contour(vec, format="code"):
    from melospy.basic_representations.jm_stats import mean
    if not vec or len(vec) == 0:
        raise ValueError("Expected non-empty vector ")
    if len(vec) == 1:
         c = 0
    else:
        begin = vec[0]
        end   = vec[-1]
        if len(vec) > 2:
            try:
                mid = mean(vec[1:len(vec)-1])
            except:
                raise ValueError("Expected numerical vector")
            c = 3*get_huron_code(begin, mid) + get_huron_code(mid, end)
        else:
            c = get_huron_code(vec[0], vec[1])
            c = 3*c + c

    if format == "code":
        str_codes = ["desc", "desc-hor", "concave", "hor-desc", "hor", "hor-asc", "convex", "asc-hor", "asc"]
        return str_codes[c+4]
    elif format == "redcode":
        str_codes = ["desc", "desc", "concave", "desc", "hor", "asc", "convex", "asc", "asc"]
        return str_codes[c+4]

    return c+4

def abesser_contour(vec, format="code", min_diff_perc = .1):
    from melospy.basic_representations.jm_stats import median
    N = len(vec)
    if N < 4:
        return huron_contour(vec, format)
    min_diff = min_diff_perc*(max(vec)-min(vec))
    #print min_diff
    quart = [0, int(round(.25*N)), int(round(.75*N)), N]
    #print quart

    begin = median(vec[0:quart[1]])
    mid = median(vec[quart[1]:quart[2]])
    end = median(vec[quart[2]:N])
    #print "begin=", vec[0:quart[1]], begin
    #print "mid=", vec[quart[1]:quart[2]], mid
    #print "end =", vec[quart[2]:N], end
    c = 3*get_huron_code(begin, mid, min_diff) + get_huron_code(mid, end, min_diff)
    if format == "code":
        str_codes = ["desc", "desc-hor", "concave", "hor-desc", "hor", "hor-asc", "convex", "asc-hor", "asc"]
        return str_codes[c+4]
    elif format == "redcode":
        str_codes = ["desc", "desc", "concave", "desc", "hor", "asc", "convex", "asc", "asc"]
        return str_codes[c+4]

    return c+4

def print_vector(vec, sep="\n"):
    def deep_str(x):
        try:
            return ", ".join([str(e) for e in x])
        except:
            return str(x)
    print(sep.join([deep_str(v) for v in vec]))

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

def find_after_sort(searchstr, strlist):
    """
    1. Sorts list in descending order its item lengths.
    2. Step through list and find first appearance of list item as substring
    in a given string.
    1) Sorts list in descending order its item lengths.
    2) Step through list and find first appearance of list item as substring in a given string.

    Example: Given the list ['b5', '', 'sus', '#5', 'm'] that contains
    chord triad labels, we want to look for '' (representing major chords)
    last, since this will always be found and therefore should be checked for last.
    """

    sortedValues = sorted(strlist, key = len, reverse = True)
    #sortedValues = l
    #print str(sortedValues)
    #print "Checking String: "+ s
    searchstr = searchstr.lower()
    for val in sortedValues:
        #print str(val) + " Len " + str(len(val))
        #return "nope"
        if isinstance( val, str ):
            #print "String: " + str(val)
            val = val.lower()
            if searchstr.find(val)>-1:
                return val
        if isinstance( val, list):
            #print "List: " + str(val)
            for v in val:
              v = v.lower()
              #print str(v) + ": "+str(s.find(v))
              if searchstr == v:
                #print "Found!" + v
                return v;
    return None

def chomp(s):
    return s.lstrip().rstrip()

def remove_empty(vec):
    ret = [v for v in vec if v and len(v)>0]
    return ret

def remove_from_list(vec, ids):
    if not isinstance(ids, list):
        ids = [ids]
    ret =[_ for i, _ in enumerate(vec) if i not in ids]
    return ret

def find_empty(vec):
    ret = []
    for i in range(len(vec)):
        if not vec[i] or len(vec[i])== 0:
            ret.append(i)
    return ret

def try_clone(val):
    try:
        v = val.clone()
        return v
    except AttributeError:
        return val

def gcd(x, y):
    """Return greatest common divisor using Euclid's Algorithm."""
    #if not (isinstance(x, int) and isinstance(y, int)):
    #    raise Exception("jm_util.: Invalid argument(s)")
    while y:
        x, y = y, x % y
    return x

def gcd_vec(vec):
    """Return greatest common divisor of a vector of ints."""

    #if not isinstance(vec, list):
    #    raise Exception("jm_util.: Need list of integer values")

    if len(vec) == 0:
        return 0

    if len(vec) == 1:
        return vec[0]

    GCD = vec[0]
    for i in range(1, len(vec)):
        GCD = gcd(GCD, vec[i])
    return GCD

def lcm(x, y):
    """Return least common multiple."""
    #if not (isinstance(x, int) and isinstance(y, int)):
    #    raise Exception("jm_util.: Invalid argument(s)")
    tmp = x
    while (tmp % y) !=0:
        tmp += x
    return tmp

def lcm_vec(vec):
    """Return least common multiple of a vector of ints."""

    #if not isinstance(vec, list) or len(vec) == 0:
    #    raise Exception("jm_util.lcm_vector: Need list of integer values")

    if len(vec) == 1:
        return vec[0]

    LCM = vec[0]
    for i in range(1, len(vec)):
        LCM = lcm(LCM, vec[i])
    return LCM

def prime_exponent(val, prime):
    exp = 0
    while val % prime == 0:
        exp +=1
        val = val/prime
    return exp

def find_position(lof, val):
    """ for a ist of interval borders find index and length
        of interval where val falls into"""
    #if not (isinstance(val, (int, float)) and isinstance(lof, list)):
    #      raise Exception("jm_util.find_position: Invalid argument")

    for i in range(len(lof)-1):
        interval = lof[i+1] - lof[i]
        #need to do some nasty hacks due to inprecise float operations
        if float_equal(val, lof[i]):
            return i, interval
        if  val > lof[i] and val < lof[i+1]-1e-12 :
            return i, interval
    return None, None

def in_int_interval(left, right, val):
    """check if val is contained in the integer interval [left, right]
        including borders"""
    if right < left:
        right, left = left, right
    if val >= left and val <= right:
        return True
    return False

def int_interval_overlap(l1, r1, l2, r2):
    """calculates the overlap of two (closed) integer intervals."""
    if l1 > r1:
        raise ValueError("Left border '{}' of first interval must be smaller or equal than right border '{}'".format(l1, r1))
    if l2 > r2:
        raise ValueError("Left border '{}' of second interval must be smaller than right border '{}'".format(l2, r2))

    if l2 < l1:
        l1, l2, r1, r2 = l2, l1, r2, r1
    if l2 > r1:
        return 0
    if r2 <= r1:
        return r2-l2+1
    return r1-l2+1

def int_interval_contains(l1, r1, l2, r2):
    """checks if (closed) integer intervals [l2, r2] is contained in interval [l1,r1]."""
    d = int_interval_overlap(l1, r1, l2, r2)
    return d == r2-l2+1

def float_equal(x, y, prec = 12):
    """ Test to floats for equality with precision 'prec'"""
    #if not (isinstance(x, float) and isinstance(x, float)):
    #    raise Exception("jm_util:float_equal: Invalid argument(s) (use only floats!")
    return round(x-y, prec)==0

def get_NA_str(s, NA="N/A"):
    """ Give N/A for a NoneType or Empty String """
    if s is None or len(str(s)) == 0:
        return NA
    return str(s)

def get_YesNo_str(b, bool_str=("Yes", "No"), NA="N/A"):
    """ Give N/A for a NoneType or Yes/No for boolean value of b"""
    if b is None: return NA
    return bool_str[0] if b else bool_str[1]

def reformat_typename(typelist):
    if isinstance(typelist, tuple):
        return ", ".join([str(t).split(" ")[1][1:-2] for t in typelist])
    else:
        return str(typelist).split(" ")[1][1:-2]

def type_check(val, typelist, allowNone = False):
    if allowNone and val == None:
        return
    if not isinstance(val, typelist):
        raise TypeError("Expected '{}' got '{}'".format(reformat_typename(typelist), reformat_typename(type(val))))
    return

def type_check_vec(val, typelist, allowNone = False, allowNoneValue = False):
    if allowNone and val == None:
        return
    type_check(val, (list, tuple))
    for v in val: type_check(v, typelist, allowNoneValue)
    return

def safe_set(obj, name, val, typelist=None, allowNone=False):
    if typelist != None:
        type_check(val, typelist, allowNone)
    setattr(obj, name, val)
    return obj

def constant_grid(N, close=False, dT=1.0):
    grid = [i * float(dT)/N for i in range(N)]
    if close:
        grid.append(dT)
    return grid

def min_max(val, minval, maxval):
    val = val if val>=minval else minval
    val = val if val<=maxval else maxval
    return val

def scale_vec(x):
    type_check_vec(x, (int, float))
    minval = float(x[0])
    maxval = float(x[-1])
    d = maxval - minval
    if float_equal(d, 0.0):
        return None
    return [float((e-minval)/d) for e in x]

def hz_to_midi(freq, tune_freq=440.0):
    return 12*log(freq/tune_freq, 2) + 69

def midi_to_hz(midi, tune_freq=440.0):
    return 2**((midi-69)/12)*tune_freq

def s_to_ms(val, digit=2):
    return round(1000*val, digit)

def ms_to_s(val, digit=2):
    return round(val/1000, digit)

def s_to_hms(val):
    m, s = divmod(val, 60)
    h, m = divmod(m, 60)
    #return "{0:02d}:{1:02d}:{2:02d}".format(int(h), int(m), int(s))
    return str(datetime.timedelta(seconds=val))

def bpm_to_s(val):
    return 60.0/float(val)

def bpm_to_ms(val):
    return 60000.0/float(val)

def grid_match(positions, grid_pattern, offset=1):
    pattern_positions= [i + offset for i in range(len(grid_pattern)) if grid_pattern[i]]
    #print positions, pattern_positions, positions == pattern_positions
    return positions == pattern_positions

#TODO: substitute next three functions by numpy versions

def cumsum(iterable):
    values = list(iterable)
    for pos in range(1, len(values)):
        values[pos] += values[pos - 1]
    return values

def diff(x):
    #type_check_vec(x, (int, float))

    d = []
    if len(x) <= 1:
        return d
    for i in range(len(x)-1):
        d.append(x[i+1]-x[i])
    return d

def diff_vec(x, y):
    #type_check_vec(x, (int, float))
    #type_check_vec(y, (int, float))
    if len(x) != len(y):
        raise ValueError("Mismatching vector lengths")
    return [x[i]-y[i] for i in range(len(x))]

def two_three_partition(val, twoleads = True):
    type_check(val, int)
    if val <= 1:
        raise ValueError("Expected integer > =2, got {}.".format(val))

    result = []
    if twoleads:
        if val % 2 == 0:
            result = [2 for _ in range((val // 2))]
        else:
            result.append(3)
            result.extend([2 for _ in range((val-3) // 2)])
    else:
        if val % 2 == 0 and val % 3 != 0:
            if val == 2:
                result = [2]
            else:
                result = 2 * two_three_partition(val // 2)

            #result = [2 for _ in range(val/2)]
        elif val % 3 == 0:
            result = [3 for _ in range(val // 3)]
        elif val % 3 == 1:
            result = [3 for _ in range((val-4) // 3)]
            result.extend([2, 2])
        elif val % 3 == 2:
            result = [3 for _ in range((val-2) // 3)]
            result.extend([2])

    return tuple(result)

def all_the_same(iterable):
    for i in range(len(iterable)-1):
        if iterable[i] != iterable[i+1]:
            return False
    return True

#def find_first_lt(vec, val, allowEqual = True):
#    for i in range(len(vec)):
#        if val > vec[i]:
#            return i
#        if (allowEqual and float_equal(val , vec[i])):
#            return i
#    return None

def find_first_gt(vec, val, allowEqual=True):
    """ Find first element in a odered numeric vector that is
        greater than (or equal) a given value.
        Returns:
            None: if vector is empty
            0: if value is smaller than the smallest element
            -1: if  value is larger than the largest element
            index of element: else
    """
    N = len(vec)
    if N == 0:
        return None
    #if N<10: print "Vec[1-10]: {}".format(vec)
    #print "Allow equal: {}".format(allowEqual)

    if val < vec[0]:
        #print "Left out. Val:{}, vec[0]:{}".format(val, vec[0])
        return 0
    if val > vec[-1]:
        #print "Right out. Val:{}, vec[-1]:{}".format(val, vec[-1])
        return -1

    mid = N//2
    #print "val: {}, mid: {}".format(val, mid)
    if val == vec[mid]:
        #print "Exact"
        if allowEqual:
            #print "Equal: {}".format(vec[mid])
            return mid
        else:
            #print "Equal: {}".format(vec[mid+1])
            return mid+1

    if val > vec[mid]:
        #print "Bigger. mid:{}".format(mid)
        return mid + 1 + find_first_gt(vec[(mid+1):], val, allowEqual)
    else:
        #print "Smaller mid:{}".format(mid)
        tmp = find_first_gt(vec[0:mid], val, allowEqual)
        if tmp == -1:
            return mid
        else:
            return tmp

def find_last_lt(vec, val, allowEqual=True):
    """ Find last element in a ordered numeric vector that is smaller
        than (or equal to) a value
        Returns:
            None: if vector is empty
            -1: if value is smaller than the smallest element
            N-1: if  value larger than the largest element
            index of element: else
    """
    debug = False
    N = len(vec)
    if N == 0: return None
    if debug and N<10: print("flt: Vec[1-10]: {}".format(vec))
    if debug: print("flt: Allow equal: {}".format(allowEqual))

    if val < vec[0]:
        if debug: print("flt: Left out. Val:{}, vec[0]:{}".format(val, vec[0]))
        return -1
    if val > vec[-1]:
        if debug: print("flt: Right out. Val:{}, vec[-1]:{}".format(val, vec[-1]))
        return len(vec)-1

    mid = N//2
    if debug: print("flt: val: {}, mid: {}".format(val, mid))
    if allowEqual and val == vec[mid]:
        if debug: print("flt: Exact")
        return mid

    if val > vec[mid]:
        if debug: print("flt: Bigger. mid:{}".format(mid))
        return mid + find_last_lt(vec[mid:], val, allowEqual)
    else:
        if debug: print("flt: Smaller mid:{}".format(mid))
        return find_last_lt(vec[0:mid], val, allowEqual)

def find_last_gt(vec, val, allowEqual=True):
    """ Find last element in a numeric vector that is greater
        than (or equal to) a value
    """
    for i in range(len(vec)):
        #print val, vec[i], i
        if val < vec[i]:
            return i
        if (allowEqual and float_equal(val, vec[i])):
            return i
    #print val, vec[i], i
    return None

def find_closest(vec, val, max_diff=None):
    """ Find element in a ordered numeric vector that is closest
        to a given value, but optionally not more than a maximum distance
        apart.
        Returns:
            None: if list is empty
            -1: if no such element is found
            index: of element
    """
    N = len(vec)
    if N == 0:
        return None
    if val <= vec[0]:
        if max_diff != None and round(abs(vec[0]-val), 10) > round(max_diff, 10):
            return -1
        else:
            return 0

    if val >= vec[-1]:
        if max_diff != None and round(abs(vec[-1]-val), 10) > round(max_diff, 10):
            return -1
        else:
            return N-1

    for i in range(N-1):
        #print val, vec[i], i
        if vec[i] <= val and val<=vec[i+1]:
            d1 = round(abs(vec[i] - val), 10)
            d2 = round(abs(val - vec[i+1]), 10)
            if d1 <= d2:
                found = i
            else:
                found = i + 1
            #print i, d1, d2, found
            if max_diff != None and round(abs(vec[found]-val), 10) > round(max_diff, 10):
                return -1
            return found
    #print val, vec[i], i
    return None

def proportions(vec, from_points = True, digits = 3):
    """
        Transform a vector into proportions,
        setting the first interval to 1
    """

    if len(vec) == 0:
        raise ValueError("Too few points")

    if from_points:
        vec = diff(vec)

    N = len(vec)
    if N == 0:
        raise ValueError("Too few points")
    if N == 1:
        return [1]
    if vec[0]<=0:
        raise ValueError("First duration must be positive")

    res = []
    for i in range(N):
        if vec[i] < 0:
            raise ValueError("Durations must be positive")
        res.append(round(float(vec[i])/vec[0], digits))
    #print "Proportions:", len(res), len(vec)
    return  res

def durations_to_points(durs, start):
    """Convert a list of durations to a list of time points starting at 'start'
    No checks done, you're on your own.
    """
    res = [start]
    for i in range(len(durs)):
        res.append(res[i]+durs[i])
    return res

def fill_up_vector(vec, default):
    """fill gaps in vector which contains only change points
        (such chord lists in AnnotatedBeatTracks)
    """
    if len(vec) == 0:
        return vec
    ret = []
    if not vec[0]:
        vec[0] = default

    last = vec[0]
    for v in vec:
        if not v:
            ret.append(last)
        else:
            ret.append(v)
            last = v
    return ret

def fill_vector(vec, N, positions):
    """Helper function for calculation of tatum proportions
    The annotator provides a list of time points, the best division and the positions
    of these time points in the grid belonging to the division. For tatum proportions
    we need a complete list of time points, which is often missing. Hence, this function
    interpolates the missing points (in a complicated manner). Assumes a vector or points
    in the interval [0,1], with the exception, that if there is a position 0 with a
    non-zero time point, this value will substracted. This allows for the small tolerance
    necessary during annotation.
    """
    #print vec, N, positions
    locv =[v for v in vec]
    pos = [p for p in positions]
    M = len(pos)

    if pos[-1] > (N-1):
        raise ValueError("Number of elements does not match positions list")

    if vec[-1] > 1:
        raise ValueError("Expected normed list. Max value: {}".format(vec[-1]))

    if N == M:
        return vec

    offset = 0
    if pos[0] != 0:
        locv.insert(0, 0)
        pos.insert(0, 0)
        M = len(pos)
    else:
        if not float_equal(vec[0], 0):
            offset = locv[0]
            #print "Set offset to ", offset
            #raise ValueError("Expected normed list, Min value != 0")
    if pos[-1] != N-1:
        #add 1, compensated for any offset (will be subtracted later)
        locv.append(1+offset)
        pos.append(N)
        M = len(pos)
        #print "Added end elements ", M
    tmp = [0 for _ in range(N+1)]
    k = 0
    for i in range(N+1):
        if i in pos:
            tmp[i] = locv[k]-offset
            k += 1
    #print "\nhere"
    #print "Locv:", locv
    #print "pos:",pos
    #print "tmp:", tmp
    #print "M, N:", M, N
    res = []
    for i in range(1, M):
        #print i, pos[i], tmp[pos[i]]
        dp  = pos[i]-pos[i-1]
        dv = tmp[pos[i]]-tmp[pos[i-1]]
        dur = (dv)/(dp)
        if dur <= 0:
            raise ValueError("Expected normed list, found negative duration")
        #print dur
        for k in range(dp):
            res.append(dur)
    #print "Durations: {}".format(durations_to_points(res, 0))
    #print len(res), N, len(durations_to_points(res, 0))
    return durations_to_points(res, 0)

def gaps(int_arr):
    """ Detects gaps in a list of monotonic integers"""
    n = len(int_arr)
    if n == 0:
        return []
    ret = [0]
    for i in range(1, n-1):
        if int_arr[i+1] <= int_arr[i]:
            raise ValueError("Expected monotonic increasing integer array, got:".format(int_arr))
        if int_arr[i+1] == int_arr[i]+1:
            ret.append(0)
        else:
            ret.append(1)

    return ret

def snippet(s, pos, width):
    if pos < 0 or pos>=len(s):
        raise ValueError("Invalid position: {}".format(pos))

    if width <= 0:
        return s[pos]

    minp = pos - width - 1
    maxp = pos + width + 1
    if minp<0:
        minp = 0
    if maxp >= len(s):
        maxp = len(s)
    return chomp(s[minp:pos] + " >>" + s[pos] + "<< " + s[pos+1:maxp])

def break_ties_causal(vec):
    if vec == None or len(vec) == 0:
        return vec
    for i in range(len(vec)-1):
        if vec[i+1] <= vec[i]:
            vec[i+1] = vec[i]+1
    return vec

def classify_duration(dur, ref_dur, borders=None):
    reldur = dur/ref_dur
    log_dur = log(reldur, 2)
    #old
    #bin_edges = [ -1.5, -.5, .5, 1.5]
    #new
    if borders == None:
        borders = [ -1.9, -.6, .6, 1.9]
    dur_class= find_last_lt(borders, log_dur, allowEqual=False)-1
    #print "dur: {0:.3f}, refdur:{1:.3f}, reldur: {2:.3f}, logdur:{3:.3f}, durclass:{4:0.3f}".format(dur, ref_dur, reldur, log_dur, dur_class)
    return dur_class

def farey_proportion(n, m, max_num, tolerance=0.1):
    if n > m:
        a, b = farey_proportion(m, n, max_num, tolerance)
        return b, a
    prop = Fraction(n, m)
    #print prop.denominator, max_num
    if gcd(m, n) != 1 and prop.denominator <= max_num:
        return n, m
    if isinstance(tolerance, float) and tolerance % 1 != 0:
        tolerance_n = int(tolerance*m)
    else:
        tolerance_n = tolerance
    #print "tolerance: {}, m:{}, tolerance_n :{}".format(tolerance, m, tolerance_n)
    best_opt = (0, 2*m)
    min_diff = int(round(m / 2))
    start = max(n-tolerance_n, 0)
    end = min(n+tolerance_n, m)
    for i in range(start, end + 1):
        #print "Testing:", i
        if gcd(m, i) == 1:
            #print "Continue i:{}, m:{}".format(i, m)
            continue
        tmp = Fraction(i, m)
        if tmp.denominator > max_num:
            #print "Continue: ", tmp.numerator
            continue
        #print "tmp: {}, raw:{}, diff:{}".format(tmp, float(tmp/prop), diff)
        opt = tmp.numerator + tmp.denominator
        diff = abs(n-i)
        #print "i:{}, m:{}, opt: {}, tmp: {}, diff:{}, min_diff:{}".format(i, m, opt, tmp, diff, min_diff)
        if diff < min_diff or (diff == min_diff and opt < best_opt[1]):
            #print "Old: {}, min_diff: {}".format(best_opt, min_diff)
            best_opt = (i, opt)
            min_diff = diff
            #print "New: {}, min_diff: {}".format(best_opt, min_diff)
    #print "tmp", Fraction(best_opt[0], m)

    return best_opt[0], m

def best_divider(val, target):
    if target % val == 0:
        return val
    new_val_down = val

    while target % new_val_down:
        new_val_down -= 1

    new_val_up = val

    while target % new_val_up and new_val_up<=target:
        new_val_up += 1

    new_val = max(new_val_down, new_val_up)
    if target % new_val == 0:
        return new_val

    new_val = min(new_val_down, new_val_up)

    if target % new_val == 0:
        return new_val

    #should/cannot not happen!
    return -1

def pad_list(vec, value, width, right=True, inplace=False):
    #pad a vector to width width with elements values
    #to the left (right=False) or right(right=True)
    try:
        l = len(vec)
    except:
        vec = [vec]
        l = 1
    if l == 0 or width <= l:
        return vec
    if not inplace:
        v = [_ for _ in vec]
    else:
        v = vec
    pads = [value]*(width-l)
    if right:
        v.extend(pads)
    else:
        pads.extend(v)
        v = pads
    return v

def multiple_insert(vec, positions, items):
    """Inserts in a vector items at specified positions.
        There might be faster and cleverer ways...
    """
    if len(positions) != len(items):
        raise ValueError("multiple_insert: positions and item list do not match")
    if len(vec) == 0 or len(positions) == 0:
        return vec
    tmp = {}
    for i in range(len(vec)):
        tmp[i] = [vec[i]]

    for j, pos in enumerate(positions):
        try:
            tmp[pos] = tmp[pos] + items[j]
            #tmp[j] = [tmp[j]] + items[j]
        except:
            print("Skipped position {}".format(pos))
            continue
    #print tmp
    ret = []
    for k in sorted(tmp):
        ret.extend(tmp[k])
    return ret

class BeatEnumerator(object):
    """Very basic beat/bar enumerator
        Beats are counted with zero-offset
    """

    def __init__(self, period=None, bar_count=0, beat_count=0):
        if period is not None and (period <= 0 or period != int(period)):
            raise ValueError("Period must be a positive integer")
        self.period = period
        self.beat_count  = beat_count
        self.bar_count = bar_count

        if period is not None:
            self.beat_count = beat_count % period

    def inc(self):
        self.beat_count += 1
        if self.beat_count  % self.period == 0:
            self.beat_count = 0
            self.bar_count += 1
        return self

    def dec(self):
        self.beat_count -= 1
        if self.beat_count < 0:
            self.beat_count += self.period
            self.bar_count -= 1

        if self.beat_count  % self.period == 0:
            self.beat_count = 0
            self.bar_count -= 1
        return self

    def add(self, be):
        type_check(be, BeatEnumerator)
        if be.period != self.period:
            raise ValueError("Cannot add bar enumerator of different period" )
        v = self.as_int() + be.as_int()
        self.bar_count = v // self.period
        self.beat_count = v % self.period
        return self

    def reset(self):
        self.bar_count = 0
        self.beat_count = 0

    def get_values(self, zero_offset=True):
        if not zero_offset:
            return self.bar_count, self.beat_count + 1
        return self.bar_count, self.beat_count

    def as_int(self):
        return self.period * self.bar_count + self.beat_count

    def __str__(self):
        return "{}.{}.{}".format(self.period, self.bar_count, self.beat_count)

class MiniStack(object):
    """Very very basic stack, basically a named counter"""

    def __init__(self, name =""):
        self.count = 0
        self.name = name

    def empty(self):
        return self.count == 0

    def state(self):
        return self.count

    def flush(self):
        self.count = 0
        return self

    def pop(self):
        if self.count > 0:
            self.count -= 1
        else:
            print("Warning: Illegal pop, stack empty")
        return self

    def push(self):
        self.count += 1
        return self

    def __str__(self):
        return "MiniStack({}): {}".format(self.name, self.count)

class Timer(object):

    def __init__(self):
        self.timer = []
        self.start()

    def start(self):
        t = time.process_time()
        self.timer.append(t)
        return t

    def tick(self, msg=""):
        if len(self.timer) == 0:
            return None
        dur = time.process_time()-self.timer[-1]
        if len(msg):
            print("{} in {}".format(msg, dur))
        #self.timer.pop()
        return dur

    def end(self, msg=""):
        if len(self.timer) == 0:
            return None
        dur = time.process_time()-self.timer[-1]
        if len(msg):
            print("{} in {}".format(msg, dur))
        self.timer.pop()
        return dur
