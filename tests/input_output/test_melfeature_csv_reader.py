#!/usr/bin/env python

import os
import sys
import unittest

import numpy as np
import pytest

from melospy.input_output.melfeature_csv_reader import MelfeatureCSVReader

from tests.rootpath import *

class TestModuleMelFeatureCSVReader( unittest.TestCase ):
    """ Unit tests for melfeature_csv_reader.py """

    #@pytest.mark.skip(reason="Path mismatch")
    def testReadRawScalarFeatureValues(self):
        """ Test read_raw() functionality for scalar feature values """
        r = MelfeatureCSVReader()
        data = r.read_raw(add_data_path('test_melfeature_csv_reader_scalar_features.csv'))
        self.assertEqual(data["itemLabels"], ['A01', 'A02', 'A03', 'C01', 'C02'])
        self.assertEqual(data["featureLabels"], ['MAKE_UP_METADATA.collection', 'MAKE_UP_METADATA.year', 'FEATURE.feature1', 'FEATURE.feature2'])
        self.assertEqual(data["featureValues"], [['ALTDEUTSCH', 1950, 0.0, 0.05],
                                                ['ALTDEUTSCH', 1955, 0.0, 0.05],
                                                ['ALTDEUTSCH', 1955, 0.0, 0.0],
                                                ['CHINA', 1955, 0.0, 0.0],
                                                ['CHINA', 1930, 0.0, 0.09]])

    #@pytest.mark.skip(reason="Path mismatch")
    def testReadRawVectorFeatureValues(self):
        """ Test read_raw() functionality for vector feature values """
        r = MelfeatureCSVReader()
        data = r.read_raw(add_data_path('test_melfeature_csv_reader_vector_features.csv'))
        self.assertEqual(data["featureValues"], [['ALTDEUTSCH', 1950, [0.0, 0.1, 0.3], 0.05],
                                                ['ALTDEUTSCH', 1955, [0.0, 0.3, 0.6], 0.0],
                                                ['ALTDEUTSCH', 1955, [0.0, 0.5, 0.7], 0.0],
                                                ['CHINA', 1955, [0.0, 0.7, 0.2], 0.0],
                                                ['CHINA', 1930, [0.0, 0.3, 0.4], 0.09]])

    #@pytest.mark.skip(reason="Path mismatch")
    def testReadRawMatrixFeatureValues(self):
        """ Test read_raw() functionality for matrix feature values """
        r = MelfeatureCSVReader()
        data = r.read_raw(add_data_path('test_melfeature_csv_reader_matrix_features.csv'))
        self.assertEqual(data["featureValues"], [['ALTDEUTSCH', 1950, [[0.0, 0.1], [0.2, 0.3]], 0.05],
                                                ['ALTDEUTSCH', 1955, [[0.0, 0.3], [0.3, 0.2]], 0.0],
                                                ['ALTDEUTSCH', 1955, [[0.0, 0.5], [0.6, 0.3]], 0.0],
                                                ['CHINA', 1955, [[0.0, 0.7], [0.1, 0.0, 4.0]], 0.0],
                                                ['CHINA', 1930, [[0.0, 0.3], [0.6, 0.5]], 0.09]])

    #@pytest.mark.skip(reason="Path mismatch")
    def testFeatureSelection(self):
        """ Test feature selection """
        r = MelfeatureCSVReader()

        data = r.read_raw(add_data_path('test_melfeature_csv_reader_scalar_features.csv'))
        dataNew = r.group_items_and_select_features(data)
        self.assertEqual(data, dataNew)

        data = r.read_raw(add_data_path('test_melfeature_csv_reader_scalar_features.csv'))
        dataNew = r.group_items_and_select_features(data, selectFeatures=['FEATURE.feature1'])
        self.assertEqual(dataNew["featureLabels"], ['FEATURE.feature1'])

        # test that non-existing feature labels are ignored
        data = r.read_raw(add_data_path('test_melfeature_csv_reader_scalar_features.csv'))
        dataNew = r.group_items_and_select_features(data, selectFeatures=['FEATURE.feature1', 'SOME RANDOM NON-EXISTING FEATURE'])
        self.assertEqual(dataNew["featureLabels"], ['FEATURE.feature1'])

    #@pytest.mark.skip(reason="Path mismatch")
    def testFeatureRemoval(self):
        """ Test feature removal """
        r = MelfeatureCSVReader()

        data = r.read_raw(add_data_path('test_melfeature_csv_reader_scalar_features.csv'))
        dataNew = r.group_items_and_select_features(data, removeFeatures=[])
        self.assertEqual(dataNew["featureLabels"], ['MAKE_UP_METADATA.collection', 'MAKE_UP_METADATA.year', 'FEATURE.feature1', 'FEATURE.feature2'])

        data = r.read_raw(add_data_path('test_melfeature_csv_reader_scalar_features.csv'))
        dataNew = r.group_items_and_select_features(data, removeFeatures=['FEATURE.feature1'])
        self.assertEqual(dataNew["featureLabels"], ['MAKE_UP_METADATA.collection', 'MAKE_UP_METADATA.year', 'FEATURE.feature2'])

        data = r.read_raw(add_data_path('test_melfeature_csv_reader_scalar_features.csv'))
        dataNew = r.group_items_and_select_features(data, removeFeatures=['MAKE_UP_METADATA.collection', 'FEATURE.feature1'])
        self.assertEqual(dataNew["featureLabels"], ['MAKE_UP_METADATA.year', 'FEATURE.feature2'])

        # test that non-existing feature labels are ignored
        data = r.read_raw(add_data_path('test_melfeature_csv_reader_scalar_features.csv'))
        dataNew = r.group_items_and_select_features(data, removeFeatures=['MAKE_UP_METADATA.collection', 'FEATURE.feature1', 'SOME RANDOM NON-EXISTING FEATURE'])
        self.assertEqual(dataNew["featureLabels"], ['MAKE_UP_METADATA.year', 'FEATURE.feature2'])

    #@pytest.mark.skip(reason="Path mismatch")
    def testGroupAndSelectEasyGrouping(self):
        """ Test group_items_and_select_features() for easy grouping """
        r = MelfeatureCSVReader()
        data = r.read_raw(add_data_path('test_melfeature_csv_reader_scalar_features.csv'))

        # let's define two groups -> German & Chines songs
        groups = [{"groupLabel":"Altdeutsch","select":["MAKE_UP_METADATA.collection", "=", "ALTDEUTSCH"] },
                  {"groupLabel":"China","select":["MAKE_UP_METADATA.collection", "=", "CHINA"] }]
        selectFeatures = ['FEATURE.feature1']
        dataNew = r.group_items_and_select_features(data, groups, selectFeatures)

        self.assertEqual(dataNew["itemLabels"], ['A01', 'A02', 'A03', 'C01', 'C02'])
        self.assertEqual(dataNew["featureLabels"], ['FEATURE.feature1'])
        self.assertEqual(dataNew["featureValues"], [[0.0], [0.0], [0.0], [0.0], [0.0]])
        self.assertEqual(dataNew["groupLabels"], ['Altdeutsch', 'China'])
        self.assertEqual(dataNew["itemGroupID"], [0, 0, 0, 1, 1])

    #@pytest.mark.skip(reason="Path mismatch")
    def testGroupAndSelectAdvancedGrouping(self):
        """ Test group_items_and_select_features() for advanced grouping"""
        r = MelfeatureCSVReader()
        fn = add_data_path('test_melfeature_csv_reader_scalar_features.csv')
        # read raw data dict
        data = r.read_raw(fn)

        # Now some more advanced grouping
        #  Group 1: German songs from after 1952
        #  Group 2: Chines songs from before 1940
        groups = [{
                     "groupLabel":"Altdeutsch_After_1952",
                     "select":
                     {"op":"&",
                         "set1":["MAKE_UP_METADATA.collection", "=", "ALTDEUTSCH"],
                         "set2":["MAKE_UP_METADATA.year", ">", 1952]
                      }
                   },
                     {
                         "groupLabel":"China_Before_1940",
                         "select":
                          {"op":"&",
                           "set1":["MAKE_UP_METADATA.collection", "=", "CHINA"],
                           "set2":["MAKE_UP_METADATA.year", "<", 1940]
                     }
                   }]

        selectFeatures = ['FEATURE.feature2']
        dataNew = r.group_items_and_select_features(data, groups, selectFeatures)

        self.assertEqual(dataNew["itemLabels"], ['A02', 'A03', 'C02'])
        self.assertEqual(dataNew["featureLabels"], ['FEATURE.feature2'])
        self.assertEqual(dataNew["featureValues"], [[0.05], [0.0], [0.09]])
        self.assertEqual(dataNew["groupLabels"], ['Altdeutsch_After_1952', 'China_Before_1940'])
        self.assertEqual(dataNew["itemGroupID"], [0, 0, 1])

    #@pytest.mark.skip(reason="Path mismatch")
    def testGroupAndSelectComplexGroupingThreeSets(self):
        """ Test group_items_and_select_features() for complex grouping with three conditions"""
        r = MelfeatureCSVReader()
        fn = add_data_path('test_melfeature_csv_reader_scalar_features.csv')
        # read raw data dict
        data = r.read_raw(fn)

        # Now some more advanced grouping
        #  Group 1: German songs from after 1952 with Feature 2 > 0.03
        #  Group 2: Chines songs from before 1940
        groups = [{
                     "groupLabel":"Altdeutsch_After_1952_F2_geq_0_03",
                     "select":
                     {"op":"&",
                         "set1":["MAKE_UP_METADATA.collection", "=", "ALTDEUTSCH"],
                         "set2":["MAKE_UP_METADATA.year", ">", 1952],
                         "set3":["FEATURE.feature2", ">", .03]
                      }
                   },
                     {
                         "groupLabel":"China_Before_1940",
                         "select":
                          {"op":"&",
                           "set1":["MAKE_UP_METADATA.collection", "=", "CHINA"],
                           "set2":["MAKE_UP_METADATA.year", "<", 1940]
                     }
                   }]

        selectFeatures = ['FEATURE.feature2']
        dataNew = r.group_items_and_select_features(data, groups, selectFeatures)

        self.assertEqual(dataNew["itemLabels"], ['A02', 'C02'])
        self.assertEqual(dataNew["featureLabels"], ['FEATURE.feature2'])
        self.assertEqual(dataNew["featureValues"], [[0.05], [0.09]])
        self.assertEqual(dataNew["groupLabels"], ['Altdeutsch_After_1952_F2_geq_0_03', 'China_Before_1940'])
        self.assertEqual(dataNew["itemGroupID"], [0, 1])


if __name__ == "__main__":
    unittest.main()
