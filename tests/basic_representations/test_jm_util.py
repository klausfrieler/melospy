#!/usr/bin/env python

""" Unit test for functions from jm_util.py"""

import os
import random
import unittest
from datetime import date
from fractions import Fraction

from melospy.basic_representations.jm_util import *


class TestJmUtil( unittest.TestCase ):
    def getRandomSimMat(self, n = 5, min_sim = 0.5):
        zerov = [0.0 for _ in range(n)]
        mat = [[0.0 for _ in range(n)] for _ in range(n)]
        random.seed()
        for i in range(n-1):
            mat[i][i] = 1.0
            for j in range(i+1, n):
                while True:
                    sim = random.random()
                    if sim>=min_sim:
                        break
                mat[i][j] = round(sim, 2)
                mat[j][i] = round(sim, 2)
        mat[n-1][n-1] = 1.0
        return mat

    def testHelper(self):
        """ Test helper functions, might go somewhere else (jm_util.py)"""
        idz = [1, 5, 8]
        periods = [2, 3, 2]
        self.assertEqual(purify_period_track(list(zip(idz, periods))), list(zip(idz, periods)))

        idz = [1, 4, 8]
        periods = [2, 3, 2]
        self.assertEqual(purify_period_track(list(zip(idz, periods))), [(1, 2)])

        onsets = [i*.5 for i in range(10)]
        g = gaussification(onsets)

        simmat = [[1.0, 0.2, 1.0, 0.2, 0.7, 0.0],
                  [0.2, 1.0, 0.2, 0.7, 0.2, 0.0],
                  [1.0, 0.2, 1.0, 0.2, 1.0, 0.0],
                  [0.2, 0.7, 0.2, 1.0, 0.2, 0.0],
                  [0.2, 0.7, 0.2, 1.0, 0.2, 0.0],
                  [0.0, 0.0, 0.0, 0.0, 0.0, 1.0]]
        simmat = self.getRandomSimMat(n=5, min_sim = 0.0)
        #print simmat
        f = simmat2form(simmat)
        #print "Form: {}".format(f)

        freq = 440
        midi = 69.0
        self.assertEqual(hz_to_midi(freq), midi)
        self.assertEqual(midi_to_hz(midi), freq)
        l = [1, 1, 2, 3, 3, 4, 4]
        self.assertEqual(unique(l), [1, 2, 3, 4])
        l = [[1, 2], [1, 2], [3, 4], [3, 4]]
        self.assertEqual(hash_list(l), "[1, 2]+[1, 2]+[3, 4]+[3, 4]")
        self.assertEqual(unique(l, hash_list), [[1, 2], [3, 4]])

        self.assertEqual(multi_convert(1.2, int, default=0 ), 1)
        self.assertEqual(multi_convert(1.2, float, default=0 ), 1.2)
        self.assertEqual(multi_convert(1.2, str, default=0 ), "1.2")
        self.assertEqual(multi_convert("1.2", int, default=0 ), 0)
        self.assertEqual(multi_convert("1.2", [int, float], default=0 ), 1.2)
        self.assertEqual(multi_convert("1.2", float, default=0 ), 1.2)
        self.assertEqual(multi_convert("1.2", str, default=0 ), "1.2")
        self.assertEqual(multi_convert("auto", [int, str], default=0 ), "auto")
        self.assertEqual(multi_convert("", [int, float], default=None ), None)

        d = {"k1": "k1", "k2":"k2"}
        self.assertEqual(get_safe_value_from_dict(d, "k1"), "k1")
        self.assertEqual(get_safe_value_from_dict(d, "k0", "Not found"), "Not found")
        self.assertRaises(KeyError, get_safe_value_from_dict, d, "k0")

        vec = [{1:2}, {3:4}]
        self.assertRaises(Exception, repeater, vec, [2])
        self.assertEqual(repeater(vec, [1, 2]), [{1:2}, {3:4}, {3:4}])

        vec =  [3, 4, 5, 8, 9, 10, 17]
        self.assertEqual(remove_runs(vec), [3, 5, 8, 10, 17])
        vec =  [3, 4, 5, 8, 9, 10, 11, 12, 13, 17]
        self.assertEqual(remove_runs(vec), [3, 5, 8, 10, 12, 17])
        self.assertEqual(remove_from_list(vec, [1, 2, 3]), [3, 9, 10, 11, 12, 13, 17])
        self.assertEqual(remove_from_list(vec, [1]), [3, 5, 8, 9, 10, 11, 12, 13, 17])
        self.assertEqual(simplify_list([1, 1, 1, 2, 2, 3]), [1, "", "", 2, "", 3])
        self.assertEqual(simplify_list([]), [])
        self.assertEqual(simplify_list(None), None)
        self.assertEqual(simplify_list([1]), [1])
        self.assertEqual(simplify_list([1, 2, 3]), [1, 2, 3])
        self.assertEqual(ensure_first_element(["", 2, 3]), [2, 2, 3])
        self.assertEqual(ensure_first_element(["", "", ""]), ["", "", ""])

        vec = [3, 1, 3, 1, 3, 1]
        self.assertEqual(nPVI(vec), 1)
        vec = [3, 3, 3, 3, 3, 3]
        self.assertEqual(nPVI(vec), 0)
        vec = [100, 0, 100, 0, 100, 0 ]
        self.assertEqual(nPVI(vec, True), 200)
        #vec = [1, 1,1,1]
        vec =[1.1, 0.1]
        self.assertAlmostEqual(nPVI(vec), 5.0/3)

        keys = ['k1', 'k2', 'k3']
        vals1 = ['v1', 'v2', 'v3']
        vals2 = ['v1', 'v2']
        self.assertEqual(dict_from_keys_vals(keys, vals1), {'k3': 'v3', 'k2': 'v2', 'k1': 'v1'})
        self.assertEqual(dict_from_keys_vals(keys, vals2), {'k3': None, 'k2': 'v2', 'k1': 'v1'})

        tmp = "     TEST      "
        self.assertEqual(chomp(tmp), "TEST")

        tmp = ["a1", "a2", "", None, "a3"]
        self.assertEqual(remove_empty(tmp), ["a1", "a2", "a3"])
        self.assertEqual(find_empty(tmp), [2, 3])

        a, b = 51, 34
        self.assertEqual(lcm(a, b), 102)
        #self.assertRaises(Exception, lcm, 1,"e")
        #self.assertRaises(Exception, lcm, "e",1)
        #self.assertRaises(Exception, lcm, 1.0,1)
        #self.assertRaises(Exception, lcm, 1, 1.0)
        vec = [2, 3, 4, 6, 12]
        self.assertEqual(lcm_vec(vec), 12)
        #print_vector(vec)
        #self.assertRaises(Exception, lcm_vec, 1)
        #self.assertRaises(Exception, lcm_vec, [1.0, 1])
        #self.assertRaises(Exception, lcm_vec, [1, 2,3,4, "r"])
        val = 2*2*2*2*3*3*5*5*7
        self.assertEqual(prime_exponent(val, 2), 4)
        self.assertEqual(prime_exponent(val, 3), 2)
        self.assertEqual(prime_exponent(val, 5), 2)
        self.assertEqual(prime_exponent(val, 7), 1)
        self.assertEqual(prime_exponent(val, 16), 1)
        self.assertEqual(prime_exponent(val, 32), 0)

        self.assertEqual(best_divider(13, 480), 15)
        self.assertEqual(best_divider(13, 487), 487)
        self.assertEqual(best_divider(487, 13), 13)
        self.assertEqual(farey_proportion(43, 48, 12, 48 // 12), (42, 48))
        x = [ 1, 2, 3, 4]
        #y = pad_list(x, 0, 5, False)
        #print pad_list(x, 0, 5, True)
        #print pad_list(x, 0, 5, False)
        self.assertEqual(pad_list(x, 0, 5, True), [1, 2, 3, 4, 0])
        self.assertEqual(pad_list(x, 0, 5, False), [0, 1, 2, 3, 4])
        self.assertEqual(pad_list(x, 0, 4, False), [1, 2, 3, 4])
        self.assertEqual(pad_list(1, 0, 4, True), [1, 0, 0, 0,])
        self.assertEqual(pad_list(1, None, 2, True), [1, None])

        x = [1, 4, 5, 8, 9]
        positions = [0, 2]
        items = [[2, 3,], [6, 7]]
        self.assertEqual(multiple_insert(x, positions, items), [1, 2, 3, 4, 5, 6, 7, 8, 9])

        #print farey_proportion(112, 192, 6, 192 // 12)
        #for i in range(1, 48):
        #    n, m = farey_proportion(i, 48, 24, 48 // 12)
        #    abs_diff = abs(float(Fraction(i, 48)-Fraction(n,m)))
        #    print "i: {}, n:{}, m:{}, diff:{}".format(i,n, m, round(abs_diff,3))
        self.assertEqual(gcd(a, b), 17)
        a, b = 51, 34
        self.assertEqual(gcd(a, b), 17)
        #self.assertRaises(Exception, gcd, 1,"e")
        #self.assertRaises(Exception, gcd, "e",1)
        #self.assertRaises(Exception, gcd, 1.0,1)
        #self.assertRaises(Exception, gcd, 1, 1.0)
        vec = [2*3*5, 3*5, 3*5*7]
        self.assertEqual(gcd_vec(vec), 15)
        self.assertEqual(powTwoBit(441), False)
        self.assertEqual(powTwoBit(128), True)
        self.assertEqual(powTwoBit(1), True)
        self.assertEqual(powTwoBit(0), False)
        self.assertEqual(powTwoBit(441.0), False)
        self.assertEqual(powTwoBit(128.0), True)
        self.assertEqual(powTwoBit(1.0), True)
        self.assertEqual(powTwoBit(0.0), False)
        self.assertEqual(closest_power_of_two(1), 1)
        self.assertEqual(closest_power_of_two(2), 2)
        self.assertEqual(closest_power_of_two(3), 2)
        self.assertEqual(closest_power_of_two(4), 4)
        self.assertEqual(closest_power_of_two(5), 4)
        self.assertEqual(closest_power_of_two(6), 4)
        self.assertEqual(closest_power_of_two(7), 8)
        self.assertEqual(closest_power_of_two(8), 8)
        self.assertEqual(closest_power_of_two(12), 8)
        self.assertEqual(closest_power_of_two(13), 16)

        self.assertEqual(index_list_to_binary_str([2, 3, 9], max_N=10, offset=1, as_string=True), "0110000010")
        self.assertEqual(index_list_to_binary_str([2, 3, 9], max_N=10, offset=0, as_string=True), "0011000001")
        self.assertEqual(index_list_to_binary_str([2, 3, 9], max_N=10, offset=0, as_string=False), [0, 0, 1, 1, 0, 0, 0, 0, 0, 1])

        #self.assertRaises(Exception, gcd_vec, 1)
        #self.assertRaises(Exception, gcd_vec, [1.0, 1])
        #self.assertRaises(Exception, gcd_vec, [1, 2,3,4, "r"])

        #self.assertRaises(Exception, find_position, [1, 2,3,4, "r"], "r")
        #self.assertRaises(Exception, find_position, [1, 2,3,4], "r")
        self.assertEqual(find_position([0, 0.375, 0.75, 1], 15), (None, None))
        self.assertEqual(find_position([0, 0.375, 0.75, 1], .15), (0, .375))
        #self.assertAlmostEqual(find_position([0,0.2, 0.4, 0.6, 0.8, 1], .4), (2, .2))
        self.assertEqual(in_int_interval(0, 2, 1), True)
        self.assertEqual(in_int_interval(2, 0, 1), True)
        self.assertEqual(in_int_interval(0, 2, 0), True)
        self.assertEqual(in_int_interval(0, 2, 2), True)

        self.assertEqual(in_int_interval(0, 2, 3), False)
        self.assertEqual(in_int_interval(0, 2, -1), False)

        self.assertEqual(int_interval_overlap(0, 0, 0, 0), 1)
        self.assertEqual(int_interval_overlap(0, 2, 0, 2), 3)
        self.assertEqual(int_interval_overlap(0, 2, 1, 2), 2)
        self.assertEqual(int_interval_overlap(0, 2, 2, 2), 1)
        self.assertEqual(int_interval_overlap(0, 2, 3, 4), 0)
        self.assertEqual(int_interval_overlap(0, 4, 2, 3), 2)
        self.assertEqual(int_interval_overlap(0, 4, 2, 4), 3)
        self.assertEqual(int_interval_overlap(0, 4, 0, 2), 3)

        self.assertEqual(int_interval_overlap(0, 2, 1, 2), 2)
        self.assertEqual(int_interval_overlap(2, 2, 0, 2), 1)
        self.assertEqual(int_interval_overlap(3, 4, 2, 2), 0)
        self.assertEqual(int_interval_overlap(1, 3, 2, 5), 2)

        self.assertRaises(ValueError, int_interval_overlap, 4, 3, 2, 2)
        self.assertRaises(ValueError, int_interval_overlap, 3, 4, 3, 2)

        self.assertEqual(int_interval_contains(3, 4, 3, 4), True)
        self.assertEqual(int_interval_contains(3, 4, 3, 3), True)
        self.assertEqual(int_interval_contains(3, 4, 4, 4), True)
        self.assertEqual(int_interval_contains(3, 6, 4, 5), True)
        self.assertEqual(int_interval_contains(4, 5, 3, 6), False)
        self.assertEqual(int_interval_contains(1, 3, 2, 5), False)

        self.assertRaises(ValueError, int_interval_contains, 3, 4, 3, 2)

        self.assertEqual(float_equal(0.999999999999999999, 1), True)
        self.assertEqual(float_equal(0.99999999999, 1, 10), True)
        self.assertEqual(float_equal(0.99999999999, 1, 11), False)


        self.assertEqual(get_NA_str(None), "N/A")
        self.assertEqual(get_NA_str(date(2013, 2, 1)), "2013-02-01")
        self.assertEqual(get_NA_str(""), "N/A")
        self.assertEqual(get_NA_str("moin"), "moin")
        self.assertEqual(get_NA_str(1), "1")
        self.assertEqual(get_NA_str(1e3), "1000.0")

        #self.assertRaises(TypeError, type_check, 1., int)
        #self.assertRaises(TypeError, type_check, "r", (int, float))
        self.assertEqual(reformat_typename((int, float)), "int, float")

        x = [0, 1, 2, 3.4]
        self.assertRaises(TypeError, type_check_vec, x, int)
        self.assertRaises(TypeError, x, str)
        self.assertRaises(TypeError, type_check_vec, [0.1, None, 0.2], (int, float), True, False)

        class TestDummy(object):
            def __init__(self):
                pass
        tmp = TestDummy()
        safe_set(tmp, "test", "test", str)
        self.assertEqual(tmp.test, "test")

        safe_set(tmp, "test2", 2, int)
        self.assertEqual(tmp.test2, 2)

        safe_set(tmp, "test3", None, (int, float), True)
        self.assertEqual(tmp.test3, None)

        self.assertEqual(constant_grid(4), [0, 0.25, 0.5, 0.75])
        self.assertEqual(constant_grid(4, True), [0, 0.25, 0.5, 0.75, 1])
        self.assertEqual(constant_grid(4, False, 2), [0, 0.5, 1.0, 1.5])

        self.assertEqual(min_max(2, 1, 4), 2)
        self.assertEqual(min_max(-1, 1, 4), 1)
        self.assertEqual(min_max(5, 1, 4), 4)

        self.assertEqual(scale_vec([0, 1, 2, 3, 4, 5]), [0, 0.2, 0.4, 0.6, 0.8, 1])
        self.assertEqual(scale_vec([1, 2, 3, 4, 5, 6]), [0, 0.2, 0.4, 0.6, 0.8, 1])
        #type_check_vec([-1,2,3,4,5], (int, float))
        #print start,end
        self.assertEqual(diff([1, 2, 3, 4, 5]), [1, 1, 1, 1])
        self.assertEqual(diff_vec([1, 2, 3, 4, 5], [2, 3, 4, 5, 6]), [-1, -1, -1, -1, -1])

        self.assertEqual(cumsum([1, 2, 3, 4, 5]), [1, 3, 6, 10, 15])
        self.assertEqual(cumsum([1, 3, 2, 2]), [1, 4, 6, 8])
        pattern = [1, 0, 1, 1]
        positions = [1, 3, 4]
        self.assertEqual(grid_match(positions, pattern), True)
        self.assertEqual(grid_match(positions, ["X", "X", 0, "x"]), False)
        #for i in range(2, 20):
        #    print "{} -> {}".format(i, two_three_partition(i, twoleads = True))
        #    print "{} -> {}".format(i, two_three_partition(i, twoleads = False))

        self.assertEqual(two_three_partition(7, twoleads = True), (3, 2, 2))
        self.assertEqual(two_three_partition(7, twoleads = False), (3, 2, 2))

        self.assertEqual(two_three_partition(10, twoleads = True), (2, 2, 2, 2, 2))
        self.assertEqual(two_three_partition(10, twoleads = False), (3, 2, 3, 2))

        self.assertEqual(all_the_same(two_three_partition(10, twoleads = True)), True)
        self.assertEqual(all_the_same(two_three_partition(10, twoleads = False)), False)

        #test find_first_gt
        vec = list(range(400))
        self.assertEqual(find_first_gt(vec, 400), -1)
        self.assertEqual(find_first_gt(vec, -1), 0)
        self.assertEqual(find_first_gt(vec, 46), 46)
        self.assertEqual(find_first_gt(vec, 46, False), 47)
        self.assertEqual(find_first_gt(vec, 46.1), 47)
        vec = list(range(2))
        self.assertEqual(find_first_gt(vec, 46.1), -1)
        self.assertEqual(find_first_gt(vec, .5), 1)
        self.assertEqual(find_first_gt(vec, 0), 0)
        self.assertEqual(find_first_gt(vec, -0.5), 0)

        #test find_last_gt
        vec = list(range(400))
        self.assertEqual(find_last_gt(vec, 400), None)
        self.assertEqual(find_last_gt(vec, -1), 0)
        self.assertEqual(find_last_gt(vec, 46), 46)
        self.assertEqual(find_last_gt(vec, 46, False), 47)
        self.assertEqual(find_last_gt(vec, 46.1), 47)
        vec = list(range(2))
        self.assertEqual(find_last_gt(vec, 46.1), None)
        self.assertEqual(find_last_gt(vec, .5), 1)
        self.assertEqual(find_last_gt(vec, 0), 0)
        self.assertEqual(find_last_gt(vec, -0.5), 0)

        #test find_last_lt
        vec = list(range(400))
        self.assertEqual(find_last_lt(vec, 500), 399)
        self.assertEqual(find_last_lt(vec, -1), -1)
        self.assertEqual(find_last_lt(vec, 46, False), 45)
        self.assertEqual(find_last_lt(vec, 46.1), 46)
        vec = list(range(2))
        self.assertEqual(find_last_lt(vec, 46.1), 1)
        self.assertEqual(find_last_lt(vec, .5), 0)
        self.assertEqual(find_last_lt(vec, 0), 0)
        self.assertEqual(find_last_lt(vec, -0.5), -1)

        self.assertEqual(find_closest(vec, -0.5), 0)
        self.assertEqual(find_closest(vec, -0.5, max_diff=.01), -1)
        self.assertEqual(find_closest(vec, 1.5), 1)
        self.assertEqual(find_closest(vec, 1.5, max_diff=.01), -1)
        self.assertEqual(find_closest(vec, 0.5), 0)
        self.assertEqual(find_closest(vec, 0.5, max_diff=.01), -1)
        self.assertEqual(find_closest(vec, -0.01, max_diff=.01), 0)
        self.assertEqual(find_closest(vec, 1.01, max_diff=.01), 1)
        self.assertEqual(find_closest(vec, 0.01, max_diff=.01), 0)

        #test find_first_lt
#        vec = range(400)
#        self.assertEqual(find_first_lt(vec, 400), None)
#        self.assertEqual(find_first_lt(vec, -1), None)
#        self.assertEqual(find_first_lt(vec, 46), 46)
#        self.assertEqual(find_first_lt(vec, 46, False), 45)
#        self.assertEqual(find_first_lt(vec, 46.1), 46)
#        vec = range(2)
#        self.assertEqual(find_first_lt(vec, 46.1), None)
#        self.assertEqual(find_first_lt(vec, .5), 0)
#        self.assertEqual(find_first_lt(vec, 0), 0)
#        self.assertEqual(find_first_lt(vec, -0.5), 0)


        #test proportions()
        vec = [0.5, 0.5, 2./3, 1]
        self.assertEqual(proportions(vec, from_points = False), [1.0, 1.0, 1.333, 2.0])
        vec = [0.5, 0.5, 2./3, 1]
        self.assertEqual(proportions(vec, from_points = False, digits=1), [1.0, 1.0, 1.3, 2.0])
        vec = [0, 0.5, 2./3, 1]
        self.assertEqual(proportions(vec, from_points = True), [1.0, 0.333, 0.667])
        vec = [0., 0.0, 2./3, 1]
        self.assertRaises(ValueError, proportions, vec, from_points = True)
        vec = [0., 0.0, 2./3, 1]
        self.assertRaises(ValueError, proportions, vec, from_points = False)
        self.assertRaises(ValueError, proportions, [], from_points = False)
        self.assertRaises(ValueError, proportions, [0], from_points = True)

        #test durations_to_points()
        vec = [1, 1, 1, 1]
        self.assertEqual(durations_to_points(vec, 10), [10, 11, 12, 13, 14])

        #test gaps
        #print gaps([1, 2, 4, 6])

        #test fill_vector()
        N = 4
        vec = [0., .5, .75]
        positions = [0, 2, 3]
        self.assertEqual(fill_vector(vec, N, positions), [0.0, 0.25, 0.5, 0.75])

        vec = [.5, .75]
        positions = [2, 3]
        self.assertEqual(fill_vector(vec, N, positions), [0.0, 0.25, 0.5, 0.75])

        vec = [.5, 1.75]
        positions = [2, 3]
        self.assertRaises(ValueError, fill_vector, vec, N, positions)

        N = 3
        vec = [0.03421189042625798, 0.3302364528091238]
        positions = [0, 1]

        vec = [0, 1.5, 0.75]
        positions = [0, 2, 4]
        self.assertRaises(ValueError, fill_vector, vec, N, positions)

        N = 8
        vec = [0.014655915614381497, 0.13149754044322992, 0.397636796997815, 0.5923728383792396, 0.8195648866575524]
        #vec = [0.0, 1*0.125, 3*0.125, 4*0.125, 6*0.125]
        positions = [0, 1, 3, 4, 6]
        self.assertEqual(len(fill_vector(vec, N, positions)), N+1)

        chords = ['', "C7", "", "", "", "F7", "", None, None, None]
        fv = fill_up_vector(chords, default = "NC")

        self.assertEqual(s_to_ms(1.234567, digit=3), 1234.567)
        self.assertEqual(ms_to_s(1234.56, digit=3), 1.235)
        self.assertEqual(s_to_hms(60.11234556), "0:01:00.112346")

        s = "abcde"
        self.assertEqual(snippet(s, 0, 2), ">>a<< bc")
        self.assertEqual(snippet(s, 4, 2), "bcd >>e<<")
        self.assertEqual(snippet(s, 2, 0), "c")
        self.assertEqual(snippet(s, 2, -1), "c")
        self.assertRaises(ValueError, snippet, s, -1, 0)
        self.assertRaises(ValueError, snippet, s, 5, 0)

        ms = MiniStack("test")
        self.assertEqual(ms.push().push().pop().pop().empty(), True)
        self.assertEqual(ms.push().push().flush().empty(), True)
        self.assertEqual(ms.push().push().state(), 2)
        ms = BeatEnumerator(4)
        ms.inc().inc().inc().inc()
        self.assertEqual(str(ms), "4.1.0")
        self.assertEqual(ms.as_int(), 4)
        self.assertEqual(ms.get_values(zero_offset=True), (1, 0))
        self.assertEqual(ms.get_values(zero_offset=False), (1, 1))
        ms.dec()
        self.assertEqual(str(ms), "4.0.3")
        self.assertEqual(ms.as_int(), 3)
        self.assertEqual(ms.get_values(zero_offset=True), (0, 3))
        self.assertEqual(ms.get_values(zero_offset=False), (0, 4))
        ms2 = BeatEnumerator(4, 3, 2)
        self.assertEqual(ms.add(ms2).as_int(), 17)
        d = ['b5', '', 'sus', '#5', 'm']
        self.assertEqual(find_after_sort("Cm7b5", d), 'b5')
        self.assertEqual(find_after_sort("F##5", d), '#5')
        self.assertEqual(find_after_sort("Cm9", d), 'm')
        self.assertEqual(find_after_sort("G7", d), '')
        self.assertEqual(find_after_sort("G7sus", d), 'sus')

        self.assertEqual(huron_contour([0, 1, 1, 1, 0]), "convex")
        self.assertEqual(huron_contour([1, 1, -2, 1, 1]), "concave")
        self.assertEqual(huron_contour([0, 1, 1, 1, 2]), "asc")
        self.assertEqual(huron_contour([2, 1, 1, 1, 0]), "desc")
        self.assertEqual(huron_contour([0, 1, -2, 1, 0]), "hor")
        self.assertEqual(huron_contour([0, -1, 2, -1, 1]), "hor-asc")
        self.assertEqual(huron_contour([0, -1, 2, -1, -1]), "hor-desc")
        self.assertEqual(huron_contour([1, -1, 2, -1, 0]), "desc-hor")
        self.assertEqual(huron_contour([0, 1, 1, 1, 1]), "asc-hor")
        self.assertEqual(huron_contour([0, -1, 2, -1, 1], format="redcode"), "asc")
        self.assertEqual(huron_contour([0, -1, 2, -1, -1], format="redcode"), "desc")
        self.assertEqual(huron_contour([1, -1, 2, -1, 0], format="redcode"), "desc")
        self.assertEqual(huron_contour([0, 1, 1, 1, 1],   format="redcode"), "asc")
        self.assertEqual(huron_contour([1]), "hor")
        self.assertEqual(huron_contour([1, 2]), "asc")
        self.assertEqual(huron_contour([2, 1]), "desc")
        self.assertEqual(huron_contour([1, 1]), "hor")

        self.assertEqual(abesser_contour([0, 1, 1, 1, 0]), "convex")
        self.assertEqual(abesser_contour([1, 1, -2, 1, 1]), "hor")
        self.assertEqual(abesser_contour([0, 1, 1, 1, 2]), "asc")
        self.assertEqual(abesser_contour([2, 1, 1, 1, 0]), "desc")
        self.assertEqual(abesser_contour([0, 1, -2, 1, 0]), "convex")
        self.assertEqual(abesser_contour([0, -1, 2, -1, 1]), "concave")
        self.assertEqual(abesser_contour([0, -1, 2, -1, -1]), "desc-hor")
        self.assertEqual(abesser_contour([1, -1, 2, -1, 0]), "concave")
        self.assertEqual(abesser_contour([0, 1, 1, 1, 1]), "asc-hor")
        self.assertEqual(abesser_contour([0, -1, 2, -1, 1], format="redcode"), "concave")
        self.assertEqual(abesser_contour([0, -1, 2, -1, -1], format="redcode"), "desc")
        self.assertEqual(abesser_contour([1, -1, 2, -1, 0], format="redcode"), "concave")
        self.assertEqual(abesser_contour([0, 1, 1, 1, 1],   format="redcode"), "asc")
        self.assertEqual(abesser_contour([1]), "hor")
        self.assertEqual(abesser_contour([1, 2]), "asc")
        self.assertEqual(abesser_contour([2, 1]), "desc")
        self.assertEqual(abesser_contour([1, 1]), "hor")

        self.assertRaises(ValueError, huron_contour, None)
        self.assertRaises(ValueError, huron_contour, [])
        self.assertRaises(ValueError, huron_contour, [1, "2", "3"])
        self.assertEqual(symbolic_autocorrelation([0, 1, 2]*100, maxlag = 5, norm = False), [300, 0.0, 0.0, 297.0, 0.0, 0.0])
        self.assertEqual(symbolic_period_detection([0, 1, 2] * 100), 3)
        self.assertEqual(symbolic_period_detection([1, -1]*200), 2)
        self.assertEqual(symbolic_period_detection(['X']*200), 1)
        self.assertEqual(symbolic_period_detection([0, 1, 2, 3, 4, 5]*100), 0)
        self.assertEqual(symbolic_period_detection([0, 1, 2, 3, 4, 5]*100, max_period = 10), 6)
        self.assertEqual(symbolic_period_detection("2212221"*10, tolerance =.9), 0)
        self.assertEqual(symbolic_period_detection("2212221"*10, max_period = 7, tolerance =.9), 7)
        self.assertEqual(symbolic_period_detection("2212221"*10, tolerance =.7), 3)
        self.assertEqual(symbolic_period_detection("2212221"*10, tolerance =.5), 3)
        self.assertEqual(symbolic_period_detection("2212221"*10, tolerance =.3), 1)
        self.assertEqual(symbolic_period_detection([-1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1], max_period=2), 2)
        self.assertEqual(symbolic_period_detection([-1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1, -1, 1], max_period=1), 0)
        self.assertEqual(symbolic_period_detection([-2, 0, 0, 0], max_period=1), 0)
        vec = [-2, 0, 0, 0]
        self.assertEqual(is_trill(vec, min_period=1, max_period=2, tolerance=1./(len(vec)-2)), True)
        vec = [1, -1, 0, -1]*2
        self.assertEqual(is_trill(vec, min_period=1, max_period=4, transform="interval", tolerance=1./(len(vec)-2)), True)

        vec = [1, -1]*2
        self.assertEqual(is_trill(vec, min_period=1, max_period=4, transform="interval", tolerance=1./(len(vec)-2)), True)
        vec = [1, 2,]*2
        self.assertEqual(is_trill(vec, min_period=1, max_period=4, transform="interval", tolerance=1./(len(vec)-2)), False)
        vec = [0, 0]*2
        self.assertEqual(is_trill(vec, min_period=1, max_period=4, transform="interval", tolerance=1./(len(vec)-2)), True)
        vec = [0, 0]*2
        self.assertEqual(is_trill(vec, min_period=2, max_period=4, transform="interval", tolerance=1./(len(vec)-2)), False)
        vec = [-2, 0, 0, 0]
        self.assertEqual(is_scale_like(vec, transform="interval"), False)
        vec = [-2, -2, -1, -2]
        self.assertEqual(is_scale_like(vec, transform="interval"), True)
        vec = [-2, -2, 1, -2]
        self.assertEqual(is_scale_like(vec, transform="interval"), True)
        vec = [-2, -2, 1, -2]
        self.assertEqual(is_scale_like(vec, transform="interval", directed=True), False)
        vec = [-2, -2, -2, -2]
        self.assertEqual(is_scale_like(vec, transform="interval", directed=True), False)

        vec = [-4, 0, 0, 0]
        self.assertEqual(is_scale_like(vec, transform="interval", mode="arpeggio"), False)
        vec = [-4, -4, -3, -4]
        self.assertEqual(is_scale_like(vec, transform="interval", mode="arpeggio"), True)
        vec = [-4, -4, 3, -4]
        self.assertEqual(is_scale_like(vec, transform="interval", mode="arpeggio"), True)
        vec = [-4, -4, 3, -4]
        self.assertEqual(is_scale_like(vec, transform="interval", mode="arpeggio", directed=True), False)
        vec = [-4, -4, -4, -4]
        self.assertEqual(is_scale_like(vec, transform="interval", mode="arpeggio", directed=True), False)
        vec = [0, 0]
        self.assertEqual(break_ties_causal(vec), [0, 1])

        vec = [0, 0, 0, 0, 0, 1, 1, 2, 2, 10, 11, 12]
        self.assertEqual(cycle_list(vec, 5), [1, 1, 2, 2, 10, 11, 12, 0, 0, 0, 0, 0])
        self.assertEqual(break_ties_causal(vec), [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12])
        vec = []
        count = 100
        elements = 4
        for i in range(count):
            vec.append(''.join(random.choice(['a', 'b', 'c', 'd']) for _ in range(elements)))
        self.assertEqual(symbolic_period_detection(vec), 0)
        a1 = ["1", "2", "3"]
        a2 = [1, 2]
        self.assertEqual(sorted(intersection(a1, a2)), sorted(['1', '2']))
        self.assertDictEqual(string_to_dict("test: test")[0], {'test': 'test'})
        self.assertDictEqual(string_to_dict({"test": "test"})[0], {'test': 'test'})
        self.assertDictEqual(string_to_dict("test: test", as_list=False), {'test': 'test'})
        self.assertDictEqual(string_to_dict({"test": "test"}, as_list=False), {'test': 'test'})
        self.assertEqual(string_to_dict("test", as_list=False), 'test')
        self.assertEqual(is_list_of_int(["1", 2, 3]), True)
        self.assertEqual(is_list_of_int(["1", 2, "Moin"]), False)
        self.assertEqual(math_mod(2, 3), 2)
        self.assertEqual(math_mod(-2, 3), 1)
        self.assertEqual(math_mod(3, 3), 0)
        self.assertEqual(math_mod(0, 3), 0)
        durations = list(range(1, 10))
        test_durations = [Fraction(1, 4), Fraction(1, 2), Fraction(1, 3), Fraction(3, 4), Fraction(2, 3), Fraction(1, 1)]
        for i in range(len(test_durations)):
            cd = classify_duration(test_durations[i], ref_dur=1)
            # print "{}: {}".format(test_durations[i], cd )
            cd = classify_duration(Fraction(1, test_durations[i]), ref_dur=1)
            # print "{}: {}".format(Fraction(1, test_durations[i]), cd )
        timer = Timer()
        for i in range(10000):
            pass
        timer.start()
        for i in range(10000):
            pass
        timer.end("Finished test 2")
        timer.end("Finished test 1")
        timer.end("Finished test 1")
if __name__ == "__main__":
    unittest.main()
