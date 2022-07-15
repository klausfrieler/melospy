""" Classes for chord-scale-theory"""
from melospy.basic_representations.chord import *
from melospy.basic_representations.jm_util import dict_from_keys_vals
from melospy.basic_representations.scale import *

most_likely = {'NC':None,
               'C':'maj',
               'Cmin':'min',
               'Caug':'wt',
               'Cdim':'htwt',
               'Csus':'mix',
               'C6':'maj',
               'C69':'maj',
               'C7':'mix',
               'Cmaj7':'maj',
               'Cmin7':'min',
               'Cminj7':'melmin',
               'Cmin6':'dor',
               'Cdim7':'htwt',
               'Cmin7b5':'hdim',
               'Caug7':'htwt',
               'C+j7':'lyd#5',
               'Csus7':'mix',
               'C7alt':'alt',
               'C79b':'htwt',
               'C9':'mix',
               'Cj79':'maj',
               'C+9':'wt',
               'C79#':'htwt',
               'Cmin9':'min',
               'Csus79b':'phr',
               'Csus79':'mix',
               'Csus9':'mix',
               'Csus13':'mix',
               'Cmin11':'min',
               'C11':'mix',
               'C9b11':'mix',
               'C11':'mix',
               'C13':'mix',
               'C+13b':'mixb6',
               'C79b11#13b':'alt',
               'C7911#':'mix#4',
               'C79#11#13b':'alt'
               }



class ChordScale(Chord):
    """
        Class for Chord Scale.
        Handles and calculates associations of scales to chords.
    """

    def __init__(self, chordLabel=None, scales=None, strategy='abs'):
        """intialize module"""
        Chord.__init__(self, chordLabel)
        if not scales:
            self._scales  = self.findBestScales(strategy = strategy)
        else:
            self._scales = scales

    def clone():
        cs = ChordLabel(self.getChordLabel())
        cs._scale = [s for s in self._scales]
        return cs

    def getScales(self):
        return self._scales

    def getBestScales(self, strategy="abs"):
        if not self._scales:
            return None
        scales_sorted = sorted(self._scales, key=self._scales.get, reverse=True)
        maxVal = 0
        ret = []
        for s in scales_sorted:
            if self._scales[s] < maxVal:
                break
            else:
                maxVal = self._scales[s]
                ret.append(s)
        return [(s, self._scales[s]) for s in ret]

    def getMostLikelyScale(self):
        c = Chord(self.getChordLabel())
        c.setRootNote(NoteName("C"))
        for s in most_likely:
            if Chord(s) == c:
                return most_likely[s]
        return None

    def findBestScales(self, strategy='abs'):
        if strategy == "most":
            return {self.getMostLikelyScale():1.0}
        scales  = {}
        compats = {}
        chord_pcset = self.getPitchClassSet()
        if chord_pcset == None:
            return None
        for k in scale_list:
            if not scale_list[k]:
                continue
            comp = theScaleManager.calcCompatibility(k, 0, chord_pcset)[0]
            compats[k] = comp
        sort_comp = sorted(compats, key=compats.get, reverse=True)
        values =  [(compats[s], len(scale_list[s])) for s in sort_comp]
        compats = dict_from_keys_vals(sort_comp, values)
        #print "compats", len(self)
        maxVal = len(chord_pcset)
        #print compats
        for s in sort_comp:
            if compats[s][0] < maxVal:
                break
            else:
                maxVal= compats[s][0]
            weight = 1-0.25*float(abs(len(scale_list[s])-7))
            scales[s] = round(float(compats[s][0])/compats[s][1], 3)*weight
        return scales

    def classifyPitch(self, pitch, scale=None):
        pcdiatonic = ['1', 'u', 'u', '3', '3', 'u', '5', '5', 'u', 'u', '7', '7' ]
        #print "classifyPitch type(self.rootnote)", type(self.rootnote)
        #print ".....", self.rootnote
        try:
            rel_pc = (int(round(pitch))-self.getRootNote().getMIDIPitch()) % 12
        except:
            return 'X'
        ctype = self.chordtype.getTriadType()

        pcset = set(self.getPitchClassSet())
        base_pcset= set(self.getPitchClassSet(includeBass=False, rootRelative=True, withTensions=False))
        upper_pcset = pcset.difference(base_pcset)
        #print(pcset)
        #print(base_pcset)
        #print(upper_pcset)
        if rel_pc not in pcset:
            label = 'c'
        else:
            if rel_pc in upper_pcset:
                label = 'u'
            else:
                label = pcdiatonic[rel_pc]
                if ctype == 'dim' and rel_pc == 9:
                    label = '7'
                if ctype == 'dim' and rel_pc == 6:
                    label = '5'
                if ctype == 'aug' and rel_pc == 8:
                    label = '5'
                if ctype == 'sus' and rel_pc == 5:
                    label = '3'
        # print "label: {}".format(label)
        # print "Pitch: {}, rel pc: {}, chord: {}, label={}".format(pitch, rel_pc, Chord.__str__(self), label)
        return label

    def __eq__(self, other):
        if not isinstance(other, ChordScale): return False
        return Chord.__eq__(self) == Chord.__eq__(other) and self._scales == other._scales

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        scales_sorted =sorted(self._scales, key=self._scales.get, reverse=True)
        scalestr = "|".join(["{}({})".format(s, self._scales[s]) for s in scales_sorted])
        chord = Chord.__str__(self)
        return chord + ":" + scalestr

    scales = property(getScales)
