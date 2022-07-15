""" Unit test for class EsacMetaData"""
import unittest

from melospy.basic_representations.esac_meta_data import *


class TestEsacMetaData(unittest.TestCase):

    def testConstructor(self):
        esac_info = EsacInfo("ALTDEUTSCH",
                             123,
                             'A0001',
                             "G",
                             '4',
                             "4/4",
                             'Das Hildebrandslied',
                             'Europa, Mitteleuropa, Deutschland',
                             'Romanze, Ballade, Lied',
                             'no comment',
                             'sprach sich meister Hiltebrant;',
                             '1, S. 1 1545 gedruckt in Wittenberg',
                             'A0651',
                             '',
                             '1_  3b_3b_4_4_  5__5__\
0_5__5_  5_6_7b_5_  5__0_\
5_  5_6_7b_5_  6b__5__\
0_5_4_3b_  5_3b_3b__\
0_3b_3b_3b_  4_4_5__  5__0_\
5_  4_3b_3b_3b_  2__1__\
0_5_5_.4  3b__0_\
5_  6b_5_5_3b_  4__5__\
0_4_3b3b1_  1_-6_-7__  1__. //')

        esac_metadata = EsacMetaData(esac_info)
        self.assertEqual(esac_metadata.getEsacInfo(), esac_info)
        self.assertEqual(esac_metadata.getSubInfo("EsacInfo"), esac_info)
        self.assertEqual(esac_metadata.getField("collection"), "ALTDEUTSCH")
        self.assertEqual(esac_metadata.getField("melid"), 123)
        self.assertEqual(esac_metadata.getField("esacid"), "A0001")
        self.assertEqual(esac_metadata.getField("title"), "Das Hildebrandslied")
        self.assertEqual(esac_metadata.getField("region"), "Europa, Mitteleuropa, Deutschland")
        self.assertEqual(esac_metadata.getField("function"), "Romanze, Ballade, Lied")
        self.assertEqual(esac_metadata.getField("key"), "G")
        self.assertEqual(esac_metadata.getField("unit"), "4")
        self.assertEqual(esac_metadata.getField("signature"), "4/4")
        self.assertEqual(esac_metadata.getField("melstring"), "1_  3b_3b_4_4_  5__5__\
0_5__5_  5_6_7b_5_  5__0_\
5_  5_6_7b_5_  6b__5__\
0_5_4_3b_  5_3b_3b__\
0_3b_3b_3b_  4_4_5__  5__0_\
5_  4_3b_3b_3b_  2__1__\
0_5_5_.4  3b__0_\
5_  6b_5_5_3b_  4__5__\
0_4_3b3b1_  1_-6_-7__  1__. //")
        self.assertRaises(TypeError, esac_metadata.__init__, 0)

        esac_metadata = EsacMetaData(None)
        self.assertEqual(esac_metadata.getEsacInfo(), None)

if __name__ == "__main__":
    unittest.main()
