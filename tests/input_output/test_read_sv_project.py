#!/usr/bin/env python

""" Class implementation of SV project file reader"""

import unittest

import pytest

from melospy.basic_representations.idea_filter import *
from melospy.input_output.lilypond_writer import *
from melospy.input_output.mcsv_writer import *
from melospy.input_output.melody_importer import *
from melospy.input_output.read_sv_project import *
from tests.rootpath import *

class TestSVReader( unittest.TestCase ):
    def testExtractLayer(self):
        #s = SVReader("c:/Users/klaus/Projects/science/intonation_jukka/data/analysis/annotations/alto_take3_mic13.sv")
        #nt = s.extractLayer("notes")
        pass

    #@pytest.mark.skip(reason="Forever messy")
    def testReader(self):
        """ Initialize module """
        #return
   
        #print("Now we are talking.....")
        #test_file = "e:/projects/science/jazzomat/projects/weimar_bass_database/sv/RonCarter_E.S.P._FINAL.sv"
        #s = SVReader(test_file)
        s = SVReader(add_data_path("MilesDavis_SoWhat_FINAL.sv"))
        s = SVReader("e:/projects/science/jazzomat/support/robin/donnalee.sv")
        events = s.bundle(duration_threshold=.00)
        #print(len(events))
        self.assertEqual(len(s.solo), len(events))
        return
 
        #print solo.beattrack
        IF = IFAFilter(solo)
        gaps = IF.getIdeaGaps()
        notes = IF.getIdeaDurations(type="notes")
        print(solo.export("ideas", optParam={"events": False, "type":"backref", "include_voids":True}))
        #print solo.export("ideas", optParam={"events": False, "type":"id", "include_voids":True})
        id_durs = solo.export("idea_durs", optParam={"type":"IOI", "unit": "sec", "include_voids":True})
        id_glue = solo.export("ideas", optParam={"events": False, "type":"backref-bin", "include_voids":True})
        print(len(id_durs), len(id_glue), sum(id_glue)*1./len(id_glue))
        print(mean(id_durs), mean(notes), mean([notes/dur for notes, dur in zip(notes, id_durs)]))
        #print solo
        #self.assertEqual(s.getBasename(), "laweb.sv")
        self.assertRaises(Exception, SVReader.__init__, 3.4)
        self.assertRaises(Exception, s.XMLparse)
        s.unzip()
        #self.assertEqual(s.getLineCount(), 385)
        #print s.getLines()
        #self.assertEqual(s.getLine(0), "<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
        xmldoc = s.XMLparse()
        data = xmldoc.getElementsByTagName("model")
        #self.assertEqual(data.length, 4)
        #print "No of Models: " + str(data.length)
        models = []
        for i in range(data.length):
            models.append(SVModel(data[i]))
        datasets = {}
        types = {'beats':0, 'phrases':1, 'notes':2}
        for m in models:
            print(str(m.getSampleRate()) + " " + m.getMainType() + "/" + m.getSubtype()+ " " + str(m.getDataId()))
            d = SVDataSet(m)
            #self.assertEqual(d.getSampleRate(), 44100)
            if len(d.getId())>0:
                d.parse(xmldoc)
                datasets[d.getType()] = d
        #self.assertEqual(len(datasets), 3)
        #self.assertEqual(datasets[0].getRaw()[0], [179742.0/44100, 'A1-Fj7-4/4'])
        #self.assertEqual(datasets[1].getRaw()[0], [201728.0/44100, 109184.0/44100])
        #self.assertEqual(datasets[2].getRaw()[0], [201728.0/44100, 5688.0/44100, 72])
        #self.assertEqual(datasets[0].getDimensions(), 2)
        #self.assertEqual(datasets[1].getDimensions(), 2)
        #self.assertEqual(datasets[2].getDimensions(), 3)
        #self.assertEqual(datasets[0].getType(), "beats")
        #self.assertEqual(datasets[1].getType(), "phrases")
        #self.assertEqual(datasets[2].getType(), "notes")


        #bt = SVParseBeats(datasets[0].getRaw()).getBeatTrack()
        #print bt
        #bcf = SVBeatsFormChords(datasets[0].parse(xmldoc))
        #print bcf.getBeats().toString()

        #SVParseNotes tests
        svn = SVParseNotes(datasets['notes'].parse(xmldoc))
        nt = svn.getNoteTrack()

        ##sva = SVParseModulation(datasets['modulation'].parse(xmldoc), None)
        #r = sva.getModulation()
        #print r
        #SVParsePhrase tests
        #nt = svn.getNoteTrack()
        #print str(nt[33].getOnsetSec())
        #spp = SVParsePhrases(datasets[1].getRaw(), svn.getNoteTrack())
        #print spp.getPhraseSection()
        spf = SVParseChordForm(datasets['beats'].getRaw(), svn.getNoteTrack())
        #print spf.parseBeatChordFormString("2.1:I1")
        #print spf.parseBeatChordFormString("2.1:A1-Gmaj7-4/4a2")
        #print "After"

        #print spf.parseBeatChordFormString("10.2")
        #print spf.parseBeatChordFormString("A1-Cmj7-4/4")
        #print spf.parseBeatChordFormString("A1-4/4-Cmj7")
        #print spf.parseBeatChordFormString("A1-Cmj7")
        #print spf.parseBeatChordFormString("A1")
        #print spf.parseBeatChordFormString("Cmj7")
        #print spf.parseBeatChordFormString("Cmj7-4/4")
        #print spf.parseBeatChordFormString("A1-4/4")
        #print spf.parseBeatChordFormString("I1")
        #print spf.parseBeatChordFormString("4/4")
        spf.parseBeatChordFormString("A7-F7")
        spf.parseBeatChordFormString("F7-A7")
        spf.parseBeatChordFormString("B1 - A7 - 4/4")
        spf.parseBeatChordFormString("Fmaj7")
        beats, sf, sc = spf.parse()
        #print nt
        #ma = MetricalAnnotator(nt, beats, cma)
        #mg = ma.annotate()
        #onset_nt = nt.getOnsets()
        #onset_mg = mg.getOnsets()
        #print len(set(onset_nt))
        #print len(set(onset_mg))
        #print (set(onset_nt).difference(onset_mg))
        #print mg.getMeanTempo()
        #mean, std = mg.getMeanTempo(bpm = True)
        #print "Mean: {}, sd: {}".format(mean, std)
        print("Now we are talking.....")
        events = s.bundle(cma, normalize=True, diagnostic=False)
        solo = s.solo
        print(solo.getModulations())

        #solo.getChordalScaleCompatibility()
        #ticks = events[0]['division']
        #sig = s.getMelody().getEvents()[0].getMetricalContext().getMeterInfo()
        #mcsvw = MCSVWriter(events)
        #mcsvw.write("testMCSV.csv", mcsvw.level1Preamble(sig.getNumerator(), sig.getDenominator(), ticks))
        #print svn.getNoteTrack().toString()

""" Function calls all unit tests """
if __name__ == '__main__':
    alltests = unittest.TestSuite([unittest.TestLoader().loadTestsFromTestCase(TestSVReader)])
    unittest.main()
