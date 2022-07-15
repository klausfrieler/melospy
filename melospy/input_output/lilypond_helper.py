""" Lilypond Helper functions (all those fractional math)"""

from fractions import Fraction
from math import log

import melospy.basic_representations.jm_util as jm_util


def distance_next_beat(qpos, wrap=True):
    val = (1-(qpos-int(qpos)))
    if wrap:
        val = val % 1
    return val

def distance_next_bar(qpos, qper):
    if qpos >= qper:
        raise RuntimeError("Invalid quarter position {} for period {}".format(qpos, qper))
    return int(qper) - qpos

def analyse_frac_duration(frac):
    #print "_analyse_frac_duration, frac=", frac
    num = frac.numerator
    denom = frac.denominator
    tuplet_factor = Fraction(1)
    closest_pot = jm_util.closest_power_of_two(denom)
    val = Fraction(num, closest_pot)

    if closest_pot != denom:
        tuplet_factor = Fraction(denom, closest_pot)
    return val, tuplet_factor

def find_optimal_duration(qpos, qdur, resolution=2, zero_sub=Fraction(1, 4)):
    if qpos == None:
        qpos = 0
    opt = (qpos + qdur).limit_denominator(resolution)-qpos
    if opt <= 0:
        opt = zero_sub
    #print "qpos:{}, qdur:{}, opt:{}, end:{}, diff:{}={}".format(qpos, qdur, opt, qpos+opt, opt-qdur, round(float(opt-qdur),2))
    return opt

def calc_dots(int_val):
    """
        Calculates the dots for dotted rhythms from
        an int val representing the number of quarter, eights etc.
        Returns the original value if it is a power of two
        Each dots mean a half; quarter, eighths etc. of the base value to add.
        E.g., 3 can be written as 2 + 1*dots, 7 as 4 + 1 * 4/2 + 1*4/4.
        On the other hand, 5 has no such represenntion, which only hold numbers
        of the form 2^n-1. In this case, base = 0 is returned.
    """
    int_val = int(abs(int_val))

    if jm_util.powTwoBit(int_val):
        return int_val, 0

    closest_pot = log(int_val+1, 2)

    num_dots = 0
    base = 0
    if closest_pot == int(closest_pot):
        num_dots = int(closest_pot)-1
        base = 2**int(log(int_val, 2))
    return base, num_dots

def render_atomic_duration(dur):
    """Transform atomic fraction duration (quarter-based), power of two denom
        into Liylpond duration token
        maximal duration is 4 (full bar rest)
        denominator must be of form 2^n
    """
    if dur > 4:
        raise ValueError("Max duration is 4, got {}".format(dur))
    if not jm_util.powTwoBit(dur.denominator):
        raise ValueError("Denominator must be a power of two, got {}".format(dur.denominator))

    int_val = dur.numerator
    base, num_dots = calc_dots(int_val)
    if base == 0:
        raise ValueError("Non-atomic duration {}".format(dur))

    tmp = Fraction(base, dur.denominator)
    #print "dur:{}, base: {}, num_dots:{}, tmp:{}".format(dur, base, num_dots,tmp)

    if tmp >= 1:
        tmp = Fraction(4, tmp.numerator)
        dur_token = str(tmp)
    else:
        dur_token = str(Fraction(base, dur.denominator).denominator * 4)

    dur_token += "."*num_dots
    return dur_token

def is_atomic_dur(dur):
    """Check if duration is of form 2^n or 2^n-1
    """
    if jm_util.powTwoBit(dur) or jm_util.powTwoBit(dur+1):
        return True
    return False

def flatten_nested_tuple(tuple_of_tuple):
    ret = []
    #print "="*60
    #print "tuple_of_tuple", tuple_of_tuple
    try:
        tmp = list(tuple_of_tuple)
    except:
        return [tuple_of_tuple]
    #print "tmp", tmp
    for i in tmp:
        #print "i", i
        ret.extend(flatten_nested_tuple(i))
        #print "ret", ret
    return ret

def split_non_atomic_dur(dur, pos=0):
    #dur = qdur.numerator
    #pos = qpos.numerator

    closest_pot = jm_util.closest_power_of_two(dur)
    if closest_pot > dur:
        closest_pot //= 2
    first = closest_pot
    second = dur - closest_pot
    if not is_atomic_dur(second):
        #print "is_atomic_dur(second)", second, is_atomic_dur(second)
        second = split_non_atomic_dur(second, pos + first)
    if pos % 2 == 1:
        first, second = second, first
    first = flatten_nested_tuple(first)
    second = flatten_nested_tuple(second)
    first.extend(second)

    return tuple(first)

def split_duration_on_beat(dur, beat0, max_dur, debug=False):
    #dist_to_beat = 1- pos
    if beat0 >= max_dur:
        raise ValueError("Beat0 {} must be smaller than max dur {}".format(beat0, max_dur))

    dist_to_bar = max_dur - beat0
    #if dist_to_bar > 4:
    #    return dist_to_bar
    if dur <= 1:
        if debug: print("ON exit = 1")
        return dur

    if not jm_util.powTwoBit(dur.denominator):
        diff_dur = int(dur)
        if diff_dur >= dist_to_bar:
            diff_dur = dist_to_bar

        if is_atomic_dur(diff_dur.numerator):
            if debug: print("ON exit = 2")
            return diff_dur
        else:
            f = split_non_atomic_dur(diff_dur.numerator, 0)[0]
            if debug: print("ON exit = 3")
            return Fraction(f, diff_dur.denominator)

    if dur >= dist_to_bar:
        if is_atomic_dur(dist_to_bar.numerator):
            if debug: print("ON exit = 4")

            while dist_to_bar > 4:
                dist_to_bar -= 4
            return dist_to_bar
        else:
            f = split_non_atomic_dur(dist_to_bar.numerator, 0)[0]
            if debug: print("ON exit = 7")
            return Fraction(f, dist_to_bar.denominator)

    if is_atomic_dur(dur.numerator):
        if debug: print("ON exit = 5")
        return dur
    else:
        #print dur.numerator, split_non_atomic_dur(dur.numerator, 0)
        f = split_non_atomic_dur(dur.numerator, 0)[0]
        if debug: print("ON exit = 6")
        return Fraction(f, dur.denominator)

    raise RuntimeError("Invalid control branch in split_duration_on_beat")

def split_duration_off_beat(dur, pos, beat0, max_dur, debug=False):
    dist_to_beat = 1 - pos
    dist_to_bar = max_dur - (beat0 + pos)

    if debug:
        print("dist_to_beat:{}, dist_to_bar:{}".format(dist_to_beat, dist_to_bar))

    if not jm_util.powTwoBit(dist_to_bar.denominator):
        if dur <= dist_to_beat:
            if dur * pos.denominator > 2:
                if debug: print("OFF exit = 10")
                return Fraction(1, pos.denominator)
            if debug: print("OFF exit = 9")
            return dur
        else:
            if debug: print("OFF exit = 1")
            return dist_to_beat

    if dist_to_bar < 1 and dur >= dist_to_bar:
        if debug: print("OFF exit = 2")
        return dist_to_bar

    if dur <= 1:
        if dist_to_beat >= dur:
            if debug: print("OFF exit = 3")
            return dur
        else:
            if debug: print("OFF exit = 4")
            return dist_to_beat

    if dur >= dist_to_bar:
        if is_atomic_dur(dist_to_bar.numerator):
            if debug: print("OFF exit = 5")
            return dist_to_bar
        else:
            f = split_non_atomic_dur(dist_to_bar.numerator, pos.numerator)[0]
            if debug: print("OFF exit = 6")
            return Fraction(f, dist_to_bar.denominator)

    if dur < dist_to_bar:
        #if debug: print "OFF exit = BRUTAL"
        #return dist_to_beat
        if not jm_util.powTwoBit(dur.denominator) or dur.denominator != 2:
            if debug: print("OFF exit = 9")
            return dist_to_beat
        if is_atomic_dur(dur.numerator):
            if debug: print("OFF exit = 7")
            return dur
        else:
            f = split_non_atomic_dur(dur.numerator, pos.numerator)[0]
            if debug: print("OFF exit = 8")
            return Fraction(f, dur.denominator)

    raise RuntimeError("Invalid control branch in split_duration_off_beat")

def split_duration(dur, pos, beat, max_dur, only_durations=True, debug=False):
    if debug:
        print("-"*60)
        print("enter lh.split_duration")
    if beat is None:
        raise ValueError("Beat given is None")
    beat0 = beat - 1
    if beat0 < 0 or beat0 >= max_dur:
        raise ValueError("Invalid beat given :{}".format(beat))
    splits = []
    rest_dur = dur
    cur_beat0 = beat0
    cur_pos   = pos
    cur_dur   = 0
    diff_bar  = 0
    positions = []
    while rest_dur > 0:
        if debug:
            print("Loop start with rest_dur: {}, pos: {}, beat0: {}, max_dur: {}".format(rest_dur, cur_pos, cur_beat0, max_dur))
        if cur_pos == 0:
           cur_dur = split_duration_on_beat(rest_dur, cur_beat0, max_dur, debug=debug)
        else:
           cur_dur = split_duration_off_beat(rest_dur, cur_pos, cur_beat0, max_dur, debug=debug)
        if debug:
            print("Received duration: {}".format(cur_dur))
        if cur_dur > 4:
            sub_splits = split_duration(cur_dur, cur_pos, beat0 % 4 + 1, 4, False, False)
            s = sub_splits[0]
            cur_dur = s["dur"]
            #print "sub_splits", sub_splits
            #print "cur_dur", cur_dur
        if cur_dur <= 0:
            raise RuntimeError("Zero duration or negative duration")
        splits.append(cur_dur)
        positions.append({"diff_bar":diff_bar, "beat0":cur_beat0, "pos":cur_pos, "dur":cur_dur})
        rest_dur -= cur_dur
        cur_pos = cur_pos + cur_dur
        cur_beat0 = int(cur_beat0 + cur_pos)
        if cur_beat0 >= max_dur:
            diff_bar += 1
        cur_beat0 =  cur_beat0 % max_dur
        cur_pos = cur_pos  % 1

        if debug:
            print("Loop end with rest_dur:{}, pos:{}, beat0:{}".format(rest_dur, cur_pos, cur_beat0))

    tot_dur = sum(splits)
    if tot_dur != dur:
        raise RuntimeError("Split dur {} does sum to dur {}".format(tot_dur, dur))
    if  only_durations:
        return splits
    return positions

def get_partial_duration(qpos, qper):
    dur = qper - qpos
    denom = dur.denominator
    #print "_get_partial_duration", dur, denom, closest_power_of_two(denom)
    if denom != closest_power_of_two(denom):
        raise ValueError("No tuplets allowed for partial")
    return 4*denom, dur.numerator
