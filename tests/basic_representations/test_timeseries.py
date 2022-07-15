#!/usr/bin/env python

""" Unit test for class Gaussfication """

import os
import unittest

import pytest

from melospy.basic_representations.jm_util import rayleigh1, rayleigh2
from melospy.basic_representations.timeseries import *
from melospy.input_output.tony_csv_reader import *
from tests.rootpath import *


class TestTimeSeries( unittest.TestCase ):

    #@pytest.mark.skip(reason="Path mismatch")
    def testConstructor(self):
        #testing empty constructor and defaults
        ts = TimeSeries()
        self.assertEqual(len(ts), 0)
        self.assertEqual(ts.getDeltaT(), None)
        del ts

        #testing simple example
        r = Rhythm.isochronous(10, 0, 0.250)
        ts = TimeSeries(r)
        self.assertEqual(len(ts.times), len(r))
        self.assertEqual(len(ts.values), len(r))
        filename = "timeseries_test.csv"
        ts.writeCSV(add_data_path(filename))
        # valid calls
        test_file = add_data_path("bb_normal_nd.csv")
        #test_file = os.path.join(root_path(), "input_output\\test\\bb_normal_nd.csv")
        tcsvr = TonyCSVReader(test_file)
        del ts
        ts = TimeSeries(tcsvr.melody)
        self.assertEqual(len(ts), len(tcsvr.melody))

        r = Rhythm.isochronous(10, 0, 0.250)
        ts = TimeSeries.fromValues(list(range(10)), start=0, deltaT=0.25)
        self.assertEqual(ts.times, r.onsets)
        self.assertEqual(ts.toRhythm(), r)
        self.assertEqual(ts.__eq__(None), False)
        self.assertEqual(ts.__eq__(r), False)
        self.assertDictEqual(ts.toDict(), {0: 0, 0.25: 1, 2.0: 8, 1.25: 5, 1.0: 4, 1.75: 7, 0.75: 3, 1.5: 6, 2.25: 9, 0.5: 2})
        del ts

        ts1 = TimeSeries.fromValues(list(range(10)), start=0, deltaT=0.25)
        self.assertEqual(ts1._get_fuse_weights(fuse="linear"), (0.5, 0.5))
        self.assertEqual(ts1._get_fuse_weights(fuse="left"), (1.0, 0.0))
        self.assertEqual(ts1._get_fuse_weights(fuse="right"), (0.0, 1.0))
        x, y = (0, 1), (1, 2)
        wt = ts1._get_fuse_weights(fuse="linear")
        wv = ts1._get_fuse_weights(fuse="linear")
        self.assertEqual(ts1._fuse_func(x, y, wt, wv), (.5, 1.5))
        self.assertEqual(ts1.fuse(min_dt=.1).timeseries, ts1.timeseries)
        self.assertEqual(ts1.fuse(min_dt=.25)[0], (0.125, 0.5))

        self.assertEqual(ts1.fuse(min_dt=.25, fuse_t="left", fuse_v="left")[0], (0.0, 0.0))
        self.assertEqual(ts1.fuse(min_dt=.25, fuse_t="left", fuse_v="right")[0], (0.0, 1.0))
        self.assertEqual(ts1.fuse(min_dt=.25, fuse_t="left", fuse_v="linear")[0], (0.0, 0.5))

        self.assertEqual(ts1.fuse(min_dt=.25, fuse_t="right", fuse_v="left")[0], (0.25, 0.0))
        self.assertEqual(ts1.fuse(min_dt=.25, fuse_t="right", fuse_v="right")[0], (0.25, 1.0))
        self.assertEqual(ts1.fuse(min_dt=.25, fuse_t="right", fuse_v="linear")[0], (0.25, 0.5))
        tmp = ts1.clone().merge(ts1).fuse(min_dt=.1, fuse_t="left", fuse_v="left")
        self.assertEqual(tmp.timeseries, ts1.timeseries)
        del ts1


        values = [1]
        ts = TimeSeries.fromValues(values, start=0, deltaT=0.25)
        self.assertRaises(ValueError, ts.extrema, mode="blub")
        self.assertEqual(ts.extrema(mode="strict"), [(0, 1, 'min')])
        self.assertEqual(ts.extrema(mode="relaxed"), [(0, 1, 'min')])
        self.assertEqual(ts.argmin(), [0])
        del ts

        values = [1, 1]
        ts = TimeSeries.fromValues(values, start=0, deltaT=0.25)
        self.assertEqual(ts.extrema(mode="strict"), [])
        self.assertEqual(ts.extrema(mode="relaxed"), [(0, 1, 'min'), (1, 1, 'min')])
        self.assertEqual(ts.argmin(mode="strict"), [])
        self.assertEqual(ts.argmin(mode="relaxed"), [0, 1])
        del ts

        values = [1, 2]
        ts = TimeSeries.fromValues(values, start=0, deltaT=0.25)
        self.assertEqual(ts.extrema(mode="strict"), [(0, 1, 'min'), (1, 2, 'max')])
        self.assertEqual(ts.extrema(mode="relaxed"), [(0, 1, 'min'), (1, 2, 'max')])
        self.assertEqual(ts.argmin(mode="strict"), [0])
        self.assertEqual(ts.argmin(mode="relaxed"), [0])
        self.assertEqual(ts.argmax(mode="strict"), [1])
        self.assertEqual(ts.argmax(mode="relaxed"), [1])
        self.assertEqual(ts._argext(mode="strict"), [0, 1])
        self.assertEqual(ts._argext(mode="relaxed"), [0, 1])
        del ts

        values = [2, 1]
        ts = TimeSeries.fromValues(values, start=0, deltaT=0.25)
        self.assertEqual(ts.extrema(mode="strict"), [(0, 2, 'max'), (1, 1, 'min')])
        self.assertEqual(ts.extrema(mode="relaxed"), [(0, 2, 'max'), (1, 1, 'min')])
        self.assertEqual(ts.argmin(), [1])
        self.assertEqual(ts.argmax(), [0])
        del ts

        values = [1, 2, 1, 2, 1]
        ts = TimeSeries.fromValues(values, start=0, deltaT=0.25)
        self.assertEqual(ts.extrema(mode="strict"), [(0, 1, 'min'), (1, 2, 'max'), (2, 1, 'min'), (3, 2, 'max'), (4, 1, 'min')])
        self.assertEqual(ts.extrema(mode="relaxed"), [(0, 1, 'min'), (1, 2, 'max'), (2, 1, 'min'), (3, 2, 'max'), (4, 1, 'min')])
        self.assertEqual(ts.argmin(), [0, 2, 4])
        self.assertEqual(ts.argmax(), [1, 3])
        del ts

        values = [1, 2, 3, 2, 1]
        ts = TimeSeries.fromValues(values, start=0, deltaT=0.25)
        self.assertEqual(ts.extrema(mode="strict"), [(0, 1, 'min'), (2, 3, 'max'), (4, 1, 'min')])
        self.assertEqual(ts.extrema(mode="relaxed"), [(0, 1, 'min'), (2, 3, 'max'), (4, 1, 'min')])
        self.assertEqual(ts.argmin(), [0,  4])
        self.assertEqual(ts.argmax(), [2])
        pos = list(range(4))
        grads = [4, 4, -4, -4, None]
        for i in pos:
            self.assertEqual(ts.approxGradient(pos[i]), grads[i] )
        self.assertEqual(ts.peakSaliences()[0], (0.5, 4.0))
        self.assertEqual(ts.maxsals()[0], (0.5, 12.0))
        del ts

        values = [3, 2, 1, 2, 3]
        ts = TimeSeries.fromValues(values, start=0, deltaT=0.25)
        self.assertEqual(ts.extrema(mode="strict"), [(0, 3, 'max'), (2, 1, 'min'), (4, 3, 'max')])
        self.assertEqual(ts.extrema(mode="relaxed"), [(0, 3, 'max'), (2, 1, 'min'), (4, 3, 'max')])
        self.assertEqual(ts.argmin(), [2])
        self.assertEqual(ts.argmax(), [0, 4])
        del ts

        values = [3, 2, 2, 2, 3]
        ts = TimeSeries.fromValues(values, start=0, deltaT=0.25)
        self.assertEqual(ts.extrema(mode="strict"), [(0, 3, 'max'), (4, 3, 'max')])
        self.assertEqual(ts.extrema(mode="relaxed"), [(0, 3, 'max'), (1, 2, 'min'), (3, 2, 'min'), (4, 3, 'max')])
        self.assertEqual(ts.argmin(mode="strict"), [])
        self.assertEqual(ts.argmax(mode="strict"), [0, 4])
        self.assertEqual(ts.argmin(mode="relaxed"), [1, 3])
        self.assertEqual(ts.argmax(mode="relaxed"), [0, 4])
        self.assertEqual(ts.maxvals(mode="strict", as_ts=False), [(0, 3), (4*.25, 3)])
        self.assertEqual(ts.minvals(mode="relaxed", as_ts=False), [(1*.25, 2), (3*.25, 2)])
        self.assertEqual(ts.minvals(mode="relaxed").timeseries, [(1*.25, 2), (3*.25, 2)])
        del ts

        values = [3, 2, 2, 2, 3]
        ts = TimeSeries.fromValues(values, start=.5, deltaT=0.25)

        self.assertEqual(ts.apply(rayleigh1)[0], (0.5, 1.0))
        self.assertEqual(ts.apply(rayleigh2)[0], (0.5, 3.0))
        self.assertEqual(ts.scale(2).values, [6, 4, 4, 4, 6])
        self.assertEqual(ts.mult(ts).values, [9, 4, 4, 4, 9])
        ts1 = TimeSeries.fromValues(values, start=0, deltaT=0.25)
        ts2 = TimeSeries.fromValues(values, start=.5, deltaT=0.5)
        ts3 = TimeSeries.fromValues([3, 2, 2, 2], start=.5, deltaT=0.25)
        self.assertRaises(ValueError, ts.mult, ts1)
        self.assertRaises(ValueError, ts.mult, ts2)
        self.assertRaises(ValueError, ts.mult, ts3)
        self.assertEqual(ts.sortByVal(reverse=True).values, [3, 3, 2, 2, 2])
        self.assertEqual(ts.sortByVal().values, [2, 2, 2, 3, 3])
        #print(ts.sortByTime(reverse=False))
        self.assertEqual(ts.sortByVal().sortByTime(reverse=True).values, [3, 2, 2, 2, 3])
        ts.sortByTime()
        self.assertEqual(ts.findClosest(-1), 0)
        self.assertEqual(ts.findClosest(2), 4)
        self.assertEqual(ts.findClosest(.75), 1)
        self.assertEqual(ts.findClosest(.625), 0)
        self.assertEqual(ts.findClosest([-1, 2, .75, .625]), [0, 4, 1, 0])
        test_ts = TimeSeries()
        test_ts.timeseries = list(zip([-1, 2, .75, .625], list(range(4))))
        test_ts.sortByTime()
        self.assertEqual(ts.findClosest(test_ts), [0, 0, 1, 4])
        self.assertEqual(ts.magneticMove(test_ts, max_dist=.1).times, [0.5, .75, 1., 1.25, 1.5])
        self.assertEqual(ts.magneticMove(test_ts).times, [0.625, .75, 1., 1.25, 2.0])

        values = [1, 2]
        ts = TimeSeries.fromValues(values, start=0, deltaT=0.5)
        self.assertEqual(ts.gradientList(), [2.0])

        values = [1, 2, 3, 2, 1]
        ts = TimeSeries.fromValues(values, start=0, deltaT=0.5)
        self.assertEqual(ts.gradientList(), [2.0, -2.0])

        values = [1, 2, 3, 3, 3, 2, 1]
        ts = TimeSeries.fromValues(values, start=0, deltaT=0.5)
        self.assertEqual(ts.gradientList(), [2.0, 0.0, -2.0])

        values = [3, 2, 1, 1, 1, 2, 3]
        ts = TimeSeries.fromValues(values, start=0, deltaT=0.5)
        self.assertEqual(ts.gradientList(), [-2.0, 0.0, 2.0])
        self.assertEqual(ts.gradientList(mode="relaxed"), [-2.0, 0.0, 2.0])

    def teardown_method(self, method):
        filenames = ["timeseries_test.csv"]
        for filename in filenames:
            if os.path.exists(add_data_path(filename)):
                os.remove(add_data_path(filename))


if __name__ == "__main__":
    unittest.main()
