""" Unit test for class RecordInfo"""
import unittest

from melospy.basic_representations.esac_info import *


class TestEsacInfo( unittest.TestCase ):

    def testConstructor(self):

        esac_info = EsacInfo(collection = "IRISCHE VKL.",\
                      title = "Lough erne shore, S. 68",\
                      melid = 123,\
                      esacid = "I0518",\
                      key  = "D",\
                      unit = "16",\
                      signature = "3/4",\
                      region = "Irland",\
                      source = "O BOYLE, Sean: 25 Irish Folksongs, Dublin 1976",\
                      function = '"Reverdie", Liebeslied',\
                      comment = "Zeilen wegen Ueberlaenge geteilt",
                      tunefamily = "I0518",
                      )


        # test with valid initialization
        self.assertEqual(esac_info.collection, "IRISCHE VKL.")
        self.assertEqual(esac_info.title, "Lough erne shore, S. 68")
        self.assertEqual(esac_info.melid, 123)
        self.assertEqual(esac_info.esacid, "I0518")
        self.assertEqual(esac_info.key, "D")
        self.assertEqual(esac_info.unit, "16")
        self.assertEqual(esac_info.signature, "3/4")
        self.assertEqual(esac_info.region, "Irland")
        self.assertEqual(esac_info.source, "O BOYLE, Sean: 25 Irish Folksongs, Dublin 1976")
        self.assertEqual(esac_info.function, '"Reverdie", Liebeslied')
        self.assertEqual(esac_info.comment, "Zeilen wegen Ueberlaenge geteilt")
        self.assertEqual(esac_info.cnr, "")
        self.assertEqual(esac_info.tunefamily, "I0518")

        esac_info_dict = { "Collection":"IRISCHE VKL.",
                "Title":"Lough erne shore, S. 68",
                "Melid": "123",
                "Esacid": "I0518",
                "Key": "D"}
        esac_info = EsacInfo.fromDict(esac_info_dict)
        print(esac_info.__dict__)
        self.assertEqual(esac_info.collection, "IRISCHE VKL.")
        self.assertEqual(esac_info.title, "Lough erne shore, S. 68")
        self.assertEqual(esac_info.melid, "123")
        self.assertEqual(esac_info.esacid, "I0518")
        self.assertEqual(esac_info.key, "D")


if __name__ == "__main__":
    unittest.main()
