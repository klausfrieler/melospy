#!/usr/bin/env python

""" Unit test for class Gaussfication """

import os
import unittest

import pytest

from melospy.basic_representations.accents import *
from melospy.basic_representations.gaussification import *
from melospy.basic_representations.rhythm import *
from melospy.input_output.melody_importer import *
from melospy.input_output.tony_csv_reader import *
from tests.rootpath import *

# from applications.commandline_tools import *

class TestGaussification( unittest.TestCase ):

    def prepareTestData(self):
        #test_file = os.path.join(root_path(), "input_output\\test\\bb_normal_nd.csv")
        test_file = add_data_path("bb_normal_nd.csv")
        tcsvr = TonyCSVReader(test_file)
        return tcsvr

    #@pytest.mark.skip(reason="Path mismatch")
    def testConstructor(self):
        #testing empty constructor and defaults
        g = Gaussification()
        self.assertEqual(len(g.times), 0)
        self.assertEqual(len(g), 0)
        self.assertEqual(g.weightrules["method"], "gauss-standard")
        self.assertEqual(g.weightrules["params"]["a_min"], 2)
        self.assertEqual(g.weightrules["params"]["a_maj"], 3)
        self.assertEqual(g.weightrules["params"]["sigma"], .04)
        self.assertEqual(g.getDeltaT(), 0.01)
        self.assertEqual(g.getSigma(), 0.04)

        del g

        #testing simple example
        r = Rhythm.isochronous(10, 0, 0.250)
        g = Gaussification(r)
        self.assertEqual(len(g.onsets), len(r))
        g.gaussify()
        l1 = len(g.timeseries)
        g.setDeltaT(0.005)
        g.gaussify()
        self.assertEqual(len(g.timeseries), 2*l1-1)
        filename = add_data_path("gauss_test.csv")
        g.writeCSV(filename)
        tcsvr = self.prepareTestData()
        # valid calls
        g = Gaussification(tcsvr.melody)
        filename = add_data_path("bb_normal_gauss.csv")
        ts = g.gaussify()
        g.writeCSV(filename)

    #@pytest.mark.skip(reason="Path mismatch")
    def testCorrelations(self):
        tcsvr = self.prepareTestData()
        r = Rhythm.isochronous(10, 0, 0.5)
        g = Gaussification(r)
        g.gaussify()
        g.writeCSV(add_data_path("ac_test_timeline.csv"))

        tw = g._getWeightTensor()
        dm = g._getOnsetDiffMatrix()
        tw1, dm1 = g._prepareAutocorrelation()
        self.assertEqual(tw1, tw)
        self.assertEqual(dm1, dm)


        tw2, dm2 = g._prepareCrossCorrelation(g)
        self.assertEqual(tw1, tw2)
        self.assertEqual(dm1, dm2)

        ac = g.autocorrelation(max_lag = 3)
        ac.writeCSV(add_data_path("ac_test.csv"))
        self.assertEqual(ac.argmax(), [0, 50, 100, 150, 200, 250, 300])
        self.assertEqual(ac.maxvals()[0], (0, 1.0))

        ac = g.autocorrelation(max_lag = 3)
        self.assertEqual(ac.argmax(), [0, 50, 100, 150, 200, 250, 300])
        self.assertEqual(ac.maxvals()[0], (0, 1.0))

        cc = g.crosscorrelation(g, start=0, end=3, deltaT=None)
        self.assertEqual(cc.argmax(), [0, 50, 100, 150, 200, 250, 300])
        self.assertEqual(cc.maxvals()[0], (0, 1.0))

        g = Gaussification(tcsvr.melody)
        #g.gaussify()
        #g.writeCSV(os.path.join(data_path, "ac_test_timeline.csv"))
        ac = g.autocorrelation(max_lag = 10)
        #ac.writeCSV(os.path.join(data_path, "bb_normal_ac.csv"))
        #print ac.extrema(mode="strict")
        ac_ts = ac.maxvals(as_ts=True)
        self.assertAlmostEqual(ac.maxvals()[1][0], (0.63))
        #print ac_ts
        #ac_ts.writeCSV(os.path.join(data_path, "bb_normal_ac_max.csv"))

    def testOnRealData(self):
        try:
            dbpath = pytest.wjazzd_db_filepath
        except:
            dbpath = add_data_path('wjazzd.db')

        dbinfo = DBInfo.fromDict({'path': dbpath, "use": True})
        #mi = MelodyImporter(tunes=tunes, path="", dbinfo=dbinfo)
        mi = MelodyImporter(tunes = "test-db", path=dbpath, dbinfo=dbinfo )
        mel = next(mi.fetcher())

        g = Gaussification(mel.slice(0, 50))
        g.gaussify()
        #g.writeCSV("miles_timeline.csv")
        ac = g.autocorrelation(max_lag = 3)
        #ac.writeCSV("miles_ac.csv")
        ac_ts = ac.maxvals(as_ts=True)
        #ac_ts.writeCSV("miles_ac_max.csv")


    def teardown_method(self, method):
        for filename in [
            'ac_test_timeline.csv',
            'ac_test.csv',
            'bb_normal_gauss.csv',
            'bb_normal_ac.csv',
            'bb_normal_ac_max.csv',
            "miles_ac.csv",
            "miles_ac_max.csv",
            'gauss_test.csv']:
                if os.path.exists(add_data_path(filename)):
                    os.remove(add_data_path(filename))


if __name__ == "__main__":
    unittest.main()
