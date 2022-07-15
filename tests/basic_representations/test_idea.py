#!/usr/bin/env python

""" Unit test for Idea class """

import unittest

import pytest

from melospy.basic_representations.idea import *


class TestIdea( unittest.TestCase ):

    def testConstructor(self):
        """ test constructor """
        #idea = Idea("~##+line_w_asdl:moin")
        #idea = Idea("void->line_w_h")
        idea = Idea("rhythm-single/irregular")
        idea = Idea("line-wavy-horizontal")
        #idea = Idea("alternativ: die n?chsten vier Ideen als: quote:The Peanut Vendor")
        #idea = Idea("theme[:1]")
        #print idea._parseType("expressive_trill")
        self.assertEqual(idea.type_string(), "line-wavy-horizontal")
        self.assertEqual(idea.type_list(), ["line", "wavy", "horizontal"])
        #print idea.type_list()
        #idea = Idea("#mAsdlkjhasdkjhasdkjhasdeldy")
        #print idea.__str__()
        #print idea._parseLabel("mAsdlkjhasdkjhasdkjhasdeldy")
    def testParseConnector(self):
        idea = Idea()
        self.assertEqual(idea._parseConnector(""),  0)
        self.assertEqual(idea._parseConnector("ABC"), 0)
        self.assertEqual(idea._parseConnector("#"), 1)
        self.assertEqual(idea._parseConnector("####"),  4)
        self.assertEqual(idea._parseConnector("#20"), 20)
        self.assertRaises(ValueError, idea._parseConnector, "##20")
        self.assertRaises(ValueError, idea._parseConnector, "##20#")

    def testParseModifier(self):
        idea = Idea()

        self.assertEqual(idea._parseModifier("*"), "*")
        self.assertEqual(idea._parseModifier("+"), "+")
        self.assertEqual(idea._parseModifier("-"), "-")
        self.assertEqual(idea._parseModifier("="), "=")
        self.assertEqual(idea._parseModifier(""), "")
        self.assertRaises(ValueError, idea._parseModifier, "++")

    #@pytest.mark.skip(reason="Assertion mismatch")
    def testParseType(self):
        idea = Idea()

        self.assertEqual(idea._parseType("void"), ("void", "", "", "undefined"))
        self.assertEqual(idea._parseType("quote"), ("quote", "", "", "undefined"))
        self.assertEqual(idea._parseType("melody"), ("melody", "", "", "undefined"))
        self.assertEqual(idea._parseType("theme"), ("theme", "", "", "undefined"))
        self.assertEqual(idea._parseType("fragment"), ("fragment", "", "", "undefined"))
        self.assertEqual(idea._parseType("expressive"), ("expressive", "", "", "undefined"))
        self.assertEqual(idea._parseType("lick"), ("lick", "", "", "undefined"))
        self.assertEqual(idea._parseType("lick_blues"), ("lick", "blues", "", "undefined"))
        self.assertEqual(idea._parseType("lick_bebop"), ("lick", "bebop", "", "undefined"))
        self.assertEqual(idea._parseType("lick_motif"), ("lick", "motif", "", "undefined"))
        self.assertEqual(idea._parseType("line_a"), ("line", "ascending", "", "ascending"))
        self.assertEqual(idea._parseType("line_d"), ("line", "descending", "", "descending"))
        self.assertEqual(idea._parseType("line_cx"), ("line", "convex", "", "convex"))
        self.assertEqual(idea._parseType("line_cv"), ("line", "concave", "", "concave"))
        self.assertEqual(idea._parseType("line_w_a"), ("line", "wavy", "ascending", "ascending"))
        self.assertEqual(idea._parseType("line_w_d"), ("line", "wavy", "descending", "descending"))
        self.assertEqual(idea._parseType("line_w_a"), ("line", "wavy", "ascending", "ascending"))
        self.assertEqual(idea._parseType("line_w_d"), ("line", "wavy", "descending", "descending"))
        self.assertEqual(idea._parseType("line_w_h"), ("line", "wavy", "horizontal", "horizontal"))
        self.assertEqual(idea._parseType("line_w_cx"), ("line", "wavy", "convex", "convex"))
        self.assertEqual(idea._parseType("line_w_cv"), ("line", "wavy", "concave", "concave"))
        self.assertEqual(idea._parseType("line_t_asdl"), ("line", "tick", "slide", "descending"))
        self.assertEqual(idea._parseType("line_t_alds"), ("line", "tick", "rabble", "ascending"))
        self.assertEqual(idea._parseType("line_t_dsal"), ("line", "tick", "tickmark", "ascending"))
        self.assertEqual(idea._parseType("line_t_dlas"), ("line", "tick", "golfclub", "descending"))
        self.assertEqual(idea._parseType("line_w_asdl"), ("line", "wavy", "slide", "descending"))
        self.assertEqual(idea._parseType("line_w_alds"), ("line", "wavy", "rabble", "ascending"))
        self.assertEqual(idea._parseType("line_w_dsal"), ("line", "wavy", "tickmark", "ascending"))
        self.assertEqual(idea._parseType("line_w_dlas"), ("line", "wavy", "golfclub", "descending"))
        self.assertEqual(idea._parseType("line_i_ah"), ("line", "interwoven", "bellow lower ascending", "ascending"))
        self.assertEqual(idea._parseType("line_i_ah"), ("line", "interwoven", "bellow lower ascending", "ascending"))
        self.assertEqual(idea._parseType("line_i_aa"), ("line", "interwoven", "stairs up", "ascending"))
        self.assertEqual(idea._parseType("line_i_dd"), ("line", "interwoven", "stairs down", "descending"))
        self.assertEqual(idea._parseType("line_i_ah"), ("line", "interwoven", "bellow lower ascending", "ascending"))
        self.assertEqual(idea._parseType("line_i_dh"), ("line", "interwoven", "bellow lower descending", "descending"))
        self.assertEqual(idea._parseType("line_i_ha"), ("line", "interwoven", "bellow upper ascending", "ascending"))
        self.assertEqual(idea._parseType("line_i_hd"), ("line", "interwoven", "bellow upper descending", "descending"))
        self.assertEqual(idea._parseType("line_i_hcx"), ("line", "interwoven", "bellow roof", "convex"))
        self.assertEqual(idea._parseType("line_i_hcv"), ("line", "interwoven", "bellow eject", "concave"))
        self.assertEqual(idea._parseType("line_i_cxh"), ("line", "interwoven", "bellow lower convex", "convex"))
        self.assertEqual(idea._parseType("line_i_cvh"), ("line", "interwoven", "bellow lower concave", "concave"))
        self.assertEqual(idea._parseType("line_i_da"), ("line", "interwoven", "scissors close-open", "undefined"))
        self.assertEqual(idea._parseType("line_i_ad"), ("line", "interwoven", "scissors open-close", "undefined"))
        self.assertEqual(idea._parseType("LINE_I_AD"), ("line", "interwoven", "scissors open-close", "undefined"))
        self.assertEqual(idea._parseType("rhythm_sr"), ("rhythm", "single/regular", "", "horizontal"))
        self.assertEqual(idea._parseType("rhythm_mr"), ("rhythm", "multi/regular", "", "horizontal"))
        self.assertEqual(idea._parseType("rhythm_si"), ("rhythm", "single/irregular", "", "horizontal"))
        self.assertEqual(idea._parseType("rhythm_mi"), ("rhythm", "multi/irregular", "", "horizontal"))
        self.assertEqual(idea._parseType("rhythm"), ("rhythm", "single/irregular", "", "horizontal"))
        self.assertEqual(idea._parseType("oscillation"), ("rhythm", "multi/regular", "", "horizontal"))
        self.assertEqual(idea._parseType("tickmark"), ("line", "tick", "tickmark", "ascending"))
        self.assertEqual(idea._parseType("slide"), ("line", "tick", "slide", "descending"))
        self.assertEqual(idea._parseType("rabble"), ("line", "tick", "rabble", "ascending"))
        self.assertEqual(idea._parseType("golfclub"), ("line", "tick", "golfclub", "descending"))

        self.assertRaises(ValueError, idea._parseType, "line_i_hh")
        self.assertRaises(ValueError, idea._parseType, "line_ad")
        self.assertRaises(ValueError, idea._parseType, "line_w_z")
        self.assertRaises(ValueError, idea._parseType, "rhythm_ri")
        self.assertRaises(ValueError, idea._parseType, "rhythm_ri[]")

    def testParseLabel(self):
        idea = Idea()
        self.assertEqual(idea.parseLabel("line_a"), True)
        self.assertEqual(idea.parseLabel("#line_a"), True)
        self.assertEqual(idea.parseLabel("~line_a"), True)
        self.assertEqual(idea.parseLabel("+line_a"), True)
        self.assertEqual(idea.parseLabel("-line_a"), True)
        self.assertEqual(idea.parseLabel("=line_a"), True)
        self.assertEqual(idea.parseLabel("*line_a"), True)
        self.assertEqual(idea.parseLabel("~+line_a"), True)
        self.assertEqual(idea.parseLabel("~-line_a"), True)
        self.assertEqual(idea.parseLabel("~=line_a"), True)
        self.assertEqual(idea.parseLabel("~*line_a"), True)
        self.assertEqual(idea.parseLabel("##line_a"), True)
        self.assertEqual(idea.parseLabel("#2line_a"), True)
        self.assertEqual(idea.parseLabel("~#line_a"), True)
        self.assertEqual(idea.parseLabel("~#+line_a"), True)
        self.assertEqual(idea.parseLabel("~#-line_a"), True)
        self.assertEqual(idea.parseLabel("~#=line_a"), True)
        self.assertEqual(idea.parseLabel("~#*line_a"), True)
        self.assertEqual(idea.parseLabel("line-wavy-horizontal"), True)
        self.assertDictEqual(idea._parseLabel("~#*line_a"), idea._parseLabel("  ~#*line_a  "))
        idea.parseLabel("~#*line_a")
        self.assertEqual(idea.backref, 1)
        self.assertEqual(idea.glue, True)
        self.assertEqual(idea.modifier, "*")
        self.assertEqual(idea.main_direction, "ascending")
        self.assertEqual(idea.parseLabel("theme:t1"), True)
        idea.parseLabel("void->theme:t1")
        self.assertEqual(idea.label, "void->theme:t1")
        self.assertRaises(ValueError, idea._parseLabel, "~~line_a")
        self.assertRaises(ValueError, idea._parseLabel, "askjdhaskdjhaskjdh")
        self.assertRaises(ValueError, idea._parseLabel, "#~line_a")
        self.assertRaises(ValueError, idea._parseLabel, "#++line_a")
        self.assertRaises(ValueError, idea._parseLabel, "#+=line_a")
        self.assertRaises(ValueError, idea._parseLabel, "~##+line_i_hh")
        self.assertRaises(ValueError, idea._parseLabel, "")
        i1 = Idea("line-wavy-ascending")
        i2 = Idea("line_w_a")
        self.assertEqual(i1.mainly_equal(i2), True)

    def testMainDirection(self):
        testIdeas =  ["quote", "rhythm_mr", "line_w_asdl", "rabble", "line_cx", "line_i_da"]
        testDirections = ["undefined", "horizontal", "descending", "ascending", "convex", "undefined"]
        for i in range(len(testIdeas)):
            idea = Idea(testIdeas[i])
            self.assertEqual(idea.main_direction, testDirections[i])

if __name__ == "__main__":
    unittest.main()
