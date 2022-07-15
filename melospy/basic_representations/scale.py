""" Class for scales """
from melospy.basic_representations.note_name import *

#from melospy.basic_representations.chord import Chord

class Scale(object):
    """ Class for scales """
    __scale_max = 12
    def __init__(self, description="", intervalStructure=None, label='', scaleMax=12):

        self.__scale_max = int(scaleMax)
        self.setDescription(description)
        self.setIntervalStructure(intervalStructure)
        #if label =="":
        #    label = description
        self.setLabel(label)

    def getDescription(self):
        return self.__desc

    def setDescription(self, desc):
        """ Set description of the scale """
        self.__desc = str(desc)
        return self

    def getIntervalStructure(self):
        return self.__intervalStructure

    def setIntervalStructure(self, val):
        """ Set interval structure as a tuple with sum==__scale_max """
        if isinstance(val, tuple):
            if sum(val) is self.__scale_max:
                self.__intervalStructure = val
            else:
                raise Exception("Sum over interval structure must be 12!")
        elif val == None:
            self.__intervalStructure = val
        else:
            raise Exception("Interval structure must be a tuple of integers")
        return self

    def getLabel(self):
        """Get label for scale"""
        return self.__label

    def setLabel(self, val):
        """
            Set label for a scale,
            mostly used as a mnemomic and as a key for ScaleManager,
            which defines a set of most well-known jazz scales.
        """
        self.__label = str(val)
        return self

    def getScaleMax(self):
        return self.__scale_max

    def getPitchClasses(self, start=0):
        p = self.getMIDIPitches(start, strict=False)
        for i in range(len(p)):
            p[i] = p[i] % self.__scale_max
        return list(set(p))

    def getMIDIPitches(self, start=0, count=0, strict=True):
        """
            Retrieves a set of 'count' MIDI pitches of the scale,
            beginning with 'start'. If 'strict' is True, no value
            greater than 127 will be generated.
        """
        if not isinstance(start, (float, int)) or start<0 or start>127:
            raise ValueError("Start value must be positive numeric less than 128")

        if not isinstance(count, (float, int)) or count<0:
            raise ValueError("Count must be a numeric >=0")

        pitch = start
        pitches = [pitch]
        ints = self.getIntervalStructure()
        if count <= 0:
            count = len(ints)
        i = 0
        for i in range(count-1):
            #print "{},{},{}".format(pitch, i % len(ints), ints[i % len(ints)])
            pitch += ints[i % len(ints)]
            if strict and pitch>127:
                break
            pitches.append(pitch)
        return pitches

    def getMIDIModifier(self):
        return theScaleManager.getMIDIModifier(self.__label.lower())


    def inside(self, vals):
        """
            Calculates the number or elements in the intersection of vals and the scale.
            Scales are represented as pitch class values between 0 and scale_max (12),
            values are likewise converted to a set of pitch class values
        """
        valset = vals if isinstance(vals, list) else [vals]
        for i in range(len(valset)):
            valset[i] = valset[i] % self.__scale_max

        pitches = set(self.getMIDIPitches())
        return len(pitches.intersection(valset))

    def __eq__(self, other):
        if not isinstance(other, Scale): return False
        return self.__intervalStructure == other. __intervalStructure

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return str(self.__label)

    def __len__(self):
        return len(self.getPitchClasses())

    desc                = property(getDescription, setDescription)
    intervalStructure   = property(getIntervalStructure, setIntervalStructure)
    label               = property(getLabel, setLabel)


class ScaleManager(object):

    def __init__(self):
        self.initScales()

    def __call__(self, id):
        """ Syntactic sugar, make the class callable (eg. ScaleManager("min")) """
        return self.getScale(id)

    def getScale(self, id):
        if not str(id).lower() in list(self.__scales.keys()):
            raise ValueError("Unknown scale: ", id)
        return self.__scales[id.lower()]

    def getScales(self):
          return self.__scales

    def getScalePreferences(self):
          return self.__scale_preferences

    def getMIDIModifier(self, id):
        if not str(id).lower() in list(self.__scales.keys()):
            raise ValueError("Unknown scale: ", id)
        return self.__scale_MIDI_modifier[id.lower()]


    def initScales(self):
        self.__scales = {
            'none':    None, \
            'maj':     Scale("Major",      (2, 2, 1, 2, 2, 2, 1), 'maj'), \
            'ion':     Scale("Ionian",     (2, 2, 1, 2, 2, 2, 1), 'maj'), \
            'min':     Scale("Minor",      (2, 1, 2, 2, 1, 2, 2), 'min'), \
            'dor':     Scale("Dorian",     (2, 1, 2, 2, 2, 1, 2)), \
            'phr':     Scale("Phrygian",   (1, 2, 2, 2, 1, 2, 2)), \
            'lyd':     Scale("Lydian",     (2, 2, 2, 1, 2, 2, 1)), \
            'mix':     Scale("Mixolydian", (2, 2, 1, 2, 2, 1, 2)), \
            'mixo':     Scale("Mixolydian", (2, 2, 1, 2, 2, 1, 2)), \
            'aeol':    Scale("Aeolian",    (2, 1, 2, 2, 1, 2, 2)), \
            'lok':     Scale("Lokrian",    (1, 2, 2, 1, 2, 2, 2)), \
            'htwt':    Scale("Half-tone Whole-tone",              (1, 2, 1, 2, 1, 2, 1, 2)), \
            'wtht':    Scale("Whole-tone Half-tone",              (2, 1, 2, 1, 2, 1, 2, 1)), \
            'dombebu': Scale("Dominant Bebop Scale (ascending)",  (2, 2, 1, 2, 2, 1, 1, 1)), \
            'dombebd': Scale("Dominant Bebop Scale (descending)", (2, 2, 1, 2, 1, 1, 1, 2)), \
            'majbeb':  Scale("Major Bebop Scale",                 (2, 2, 1, 1, 1, 2, 2, 1)), \
            'harmmin': Scale("Harmonic Minor",                    (2, 1, 2, 2, 1, 3, 1), 'min'),\
            'melmin':  Scale("Melodic Minor (ascending)",         (2, 1, 2, 2, 2, 2, 1), 'min'), \
            'dorb2':   Scale("Dorian b2",                         (1, 2, 2, 2, 2, 1, 2)), \
            'lyd#5':   Scale("Lydian augmented",      (2, 2, 2, 2, 1, 2, 1)), \
            'mix#4':   Scale("Mixolydian #4",         (2, 2, 2, 1, 2, 1, 2)), \
            'mixb6':   Scale("Mixolydian b6",         (2, 2, 1, 2, 1, 2, 2)), \
            'hdim':    Scale("Half-diminished Scale", (2, 1, 2, 1, 2, 2, 2)), \
            'alt':     Scale("Altered Scale",         (1, 2, 1, 2, 2, 2, 2)), \
            'wt':      Scale("Whole Tone Scale",      (2, 2, 2, 2, 2, 2)), \
            'majpent': Scale("Major Pentatonic",      (2, 2, 3, 2, 3)), \
            'minpent': Scale("Minor  Pentatonic",     (3, 2, 2, 3, 2)), \
            'mixpent': Scale("Mixolydian Pentatonic", (2, 2, 3, 2, 3)), \
            'bluesmin': Scale("Blues Scale",           (3, 2, 1, 1, 3, 2)), \
            'blues':    Scale("Major Blues Scale",     (2, 1, 1, 1, 2, 2, 1, 1, 1)),\
            'chrom':   Scale("Chromatic Scale",     (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1))
          }
        for s in self.__scales:
            if self.__scales[s] and self.__scales[s].getLabel() == "":
                self.__scales[s].setLabel(s)
        self.__scale_preferences = {
            'maj': 3.5,
            'ion': 0,
            'min': 3,
            'dor': 2.5,
            'phr': 2,
            'lyd': 2.5,
            'mix': 2.5,
            'mixo': 2.5,
            'aeol': 0,
            'lok':  1,
            'htwt': 2,
            'wtht': 2,
            'dombebu': 2,
            'dombebd': 2,
            'majbeb': 2,
            'harmmin': 2,
            'melmin': 2,
            'dorb2':  1,
            'lyd#5':  2,
            'mix#4':  2,
            'mixb6':  2,
            'hdim': 2,
            'alt': 2.5,
            'wt': 3,
            'majpent': 3,
            'minpent': 3,
            'mixpent': 2,
            'bluesmin': 3,
            'blues': 2,
            'chrom': 0
          }
        self.__scale_MIDI_modifier= {
            #need for getting MIDI keys right
            #first value is offset in the circle of fifths
            #second value is maj/min indicator (0=maj, 1=min)
            'maj': (0, 0),
            'ion': (0, 0),
            'min': (-3, 0),
            'dor': (-2, 0),
            'phr': (-4, 0),
            'lyd': (+1, 0),
            'mix':(-1, 0),
            'mixo':(-1, 0),
            'aeol':(0, 1),
            'lok':(-5, 0),
            'htwt': (0, 0),
            'wtht': (0, 0),
            'dombebu': (-1, 0),
            'dombebd': (-1, 0),
            'majbeb': (-1, 0),
            'harmmin':(0, 1),
            'melmin': (0, 1),
            'dorb2':  (-2, 0),
            'lyd#5':  (+1, 0),
            'mix#4':  (-1, 0),
            'mixb6':  (-1, 0),
            'hdim': (0, 0),
            'alt': (0, 0),
            'wt': (0, 0),
            'majpent': (0, 0),
            'minpent': (0, 1),
            'mixpent': (-1, 0),
            'blues': (0, 0),
            'bluesmin': (0, 1),
            'chrom': (0, 0)
          }


        self.most_likely = {'NC':None,
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

    def calcCompatibility(self, label, root, pcset, weighted=False, normed=False):

        if label == None:
            return None

        s = self.__scales[label]
        #print label, root, pcset
        try:
            rpc = root.getPitchClass()
            rn = root
        except:
            try:
                rn = NoteName(root)
                rpc = rn.getPitchClass()
            except:
                rpc = root % 12
                rn = NoteName(root)
        rn.setOctave(None)
        pc1 = {(p + rpc) % 12 for p in s.getPitchClasses()}
        pc2 = [p % 12 for p in pcset]
        if not weighted:
            pc2 = set(pc2)
        comp = 0
        l = len(pc1)
        for p in pc2:
            if p in pc1:
                comp += 1
        #print pc1, pc2, comp
        if normed:
            return float(comp)/l
        return (comp, l)

    def calcScaleCompatibility(self, label1, label2, root1=0, root2=0):
        s1 = self.__scales[label1]
        s2 = self.__scales[label2]
        try:
            rpc1 = root1.getPitchClass()
            rn1 = root1
        except:
            rpc1 = root1 % 12
            rn1 = NoteName(root1)
        try:
            rpc2 = root2.getPitchClass()
            rn2 = root2
        except:
            rpc2 = root2 % 12
            rn2 = NoteName(root2)

        rn1.setOctave(None)
        rn2.setOctave(None)

        pc1 = {(p + rpc1) % 12 for p in s1.getPitchClasses()}
        pc2 = {(p + rpc2) % 12 for p in s2.getPitchClasses()}
        l1 = len(pc1)
        l2 = len(pc2)
        comp = len(pc1.intersection(pc2))
        #round(float(comp)/l1,3)
        print("{} {} <->{} {}: {} of ({},{})".format(rn1, label1, rn2, label2, comp, l1, l2))
        return comp

    def calcScaleCompatibilities(self):
        for k1 in self.scales:
            if k1 == 'none':
                continue
            for k2 in self.scales:
                if k2 == 'none' or k2 == k1:
                    continue
                self.calcScaleCompatibility(k1, k2)

    scales = property(getScales)
    scale_preferences = property(getScalePreferences)

theScaleManager = ScaleManager()
scale_list = theScaleManager.getScales()
