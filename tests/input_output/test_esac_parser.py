#!/usr/bin/env python

""" Class implementation of MCSV reader"""

import unittest

import pytest

from melospy.input_output.esac_parser import *
from melospy.input_output.esac_reader import *
from tests.rootpath import *
#import os
free_songs = ["W1330.esa", "W1331A.esa", "W1332B.esa", "W1340.esa", "W1341B.esa", "W1342A.esa", "W1342B.esa", "W1342C.esa", "W1342D.esa", "W1342E.esa", "W1342F.esa", "W1342G.esa", "W1342R.esa", "W1386A.esa", "W1387B.esa", "W1387C.esa", "W1388.esa", "W1389.esa", "W1390.esa", "W1391.esa", "W1392.esa", "W1393.esa", "W1394.esa", "W1395A.esa", "W1395B.esa", "W1395C.esa", "W1396A.esa", "W1396B.esa", "W1397.esa", "W1398.esa", "W1399.esa", "W1400A.esa", "W1400B.esa", "W1400C.esa", "W1423A.esa", "W1423B.esa", "W1423D.esa", "W1424.esa", "W1427.esa", "W1432.esa", "W1463.esa"]

class TestEsacParser( unittest.TestCase ):

    def testEsacNoteEvent(self):
        ene = EsacNoteEvent(60, 0, 0, 1)
        self.assertEqual(ene.value, 60)
        self.assertEqual(ene.duration, 1)
        self.assertEqual(ene.tuplet_factor, 1)
        ene = EsacNoteEvent(60, 2, 1, 5)
        self.assertEqual(ene.value, 60)
        self.assertEqual(ene.duration, 6)
        self.assertEqual(ene.tuplet_factor, 5)
        self.assertEqual(ene.tuplet_co_factor, 4)
        self.assertRaises(ValueError, ene.__init__, 60, 2, 3, 1)

    #@pytest.mark.skip(reason="Path mismatch")
    def testEsacParser(self):
        """ Initialize module """
        #esac_reader = EsacReader("c:\Users\klaus\Data\EsacDB\Irland\esa\complete\I0522.esa")
        #esac_reader = EsacReader("c:/Users/klaus/Data/EsacDB/WarmiaI/esa/complete/W1342C.esa")
        #esac_reader = EsacReader("c:/Users/klaus/Data/EsacDB/WarmiaI/esa/complete/W1332B.esa")
        #esac_reader = EsacReader("c:/Users/klaus/Data/EsacDB/WarmiaI/esa/complete/W1435.esa")
        #esac_reader = EsacReader("c:/Users/klaus/Data/EsacDB/WarmiaI/esa/complete/W1390.esa")
        #esac_reader = EsacReader("c:/Users/klaus/Data/EsacDB/Kinderlieder/esa/complete/K0025.esa")
        #esac_reader = EsacReader("c:/Users/klaus/Projects/science/jazzomat/software/melopy/input_output/jazz/ChetBaker_ThereWillNeverBeAnotherYou.esa")
        #esac_reader = EsacReader("c:/Users/klaus/Projects/science/jazzomat/software/melopy/input_output/jazz/ChetBaker_JustFriends.esa")
        #esac_reader = EsacReader("c:/Users/klaus/Projects/science/jazzomat/software/melopy/input_output/jazz/JohnColtrane_Slowtrane.esa")
        #esac_reader = EsacReader("c:/Users/klaus/Projects/science/jazzomat/software/melopy/input_output/jazz/ArtPepper_GroovinHigh.esa")
        #esac_reader = EsacReader("c:/Users/klaus/Projects/science/jazzomat/software/melopy/input_output/parser_test2.esa")
        #esac_reader = EsacReader("c:/Users/klaus/Projects/science/jazzomat/software/melopy/input_output/freemeter/W1463.esa")
        #esac_reader = EsacReader("c:/Users/klaus/Data/EsacDB/WarmiaI/esa/complete/W1462.esa")
        #esac_reader = EsacReader("c:/Users/klaus/Data/EsacDB/Balladen/esa/complete/Q0034.esa")
        #esac_reader = EsacReader("c:/Users/klaus/Data/EsacDB/WarmiaI/esa/complete/W1347C.esa")
        esac_reader = EsacReader(add_data_path("D0001.esa"))

        #free_path = "c:/Users/klaus/Projects/science/jazzomat/software/melopy/input_output/tmp/"
        #for i in range(len(free_songs)):
        #    print "Song: "+ free_songs[i]
        #    esac_reader = EsacReader(free_path+ free_songs[i])
        #esac_parser = EsacParser(esac_reader.esacmelody, esac_reader.unit, esac_reader.get_bar_lengths(), esac_reader.signatures, esac_reader.key, esac_reader.tempo)
        #print esac_reader.esacinfo
        #print K0001

""" Function calls all unit tests """
if __name__ == '__main__':
    alltests = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(TestEsacParser)])
    unittest.main()
