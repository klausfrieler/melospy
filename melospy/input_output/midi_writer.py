""" Wrapper of MIDI package """

from math import floor, log10, pow

from melospy.basic_representations.jm_util import bit_log2, lcm, min_max
from melospy.basic_representations.melody import Melody
from melospy.basic_representations.note_track import NoteTrack
from melospy.external.MIDIutil.MidiFile import MIDIFile
from melospy.input_output.midi_params import MIDIWriterParams


class MIDIWriter(object):
    """ Class for writing MIDI files """

    def __init__(self, params=None, verbose=False):
        if isinstance(params, dict):
            params = MIDIWriterParams.fromDict(params)

        if params == None:
            params = MIDIWriterParams()
        self.tempo = params.tempo
        #print self.tempo
        self.transpose = int(params.transpose)
        self.track = int(params.track)
        self.channel = int(params.channel)
        self.instrument = params.instrument
        self.loudness_map = "const"

        try:
            self.volume = min_max(int(params.volume), 1, 127)
        except:
            self.volume = "auto"
            self.loudness_map = params.volume.lower()
            if self.loudness_map not in ["const", "log_fixed", "linear", "log_range"]:
                raise ValueError("Invalid loudness mapping: {}".format(params.volume))
        self.quantize = params.quantize
        self.quantize_duration = params.quantize_duration
        self.verbose = verbose
        try:
            self.ticks_per_beat = min(int(params.ticks_per_beat), 20160)
        except:
            self.ticks_per_beat = 0

    def _getTimeSignatureInfo(self, mne):
        mc = mne.getMetricalContext()
        mi = mc.getMeterInfo()
        num = mi.getNumerator()
        denom = bit_log2(mi.getDenominator())
        if denom == None:
            raise ValueError("Invalid denominator: {}!".format(mi.getDenominator()))
        return num, denom

    def _loudnessToVelocity(self, solo_event, max_vel=127, min_vel=81, max_loud=85, min_loud=45, mode="const"):
        try:
            loudness = float(solo_event.getLoudnessField("median"))
        except:
            #print "No loudness values found"
            return max_loud
        #print "loudness:{}, max_vel:{}, min_vel:{}, max_loud:{}, min_loud:{}".format(loudness, max_vel, min_vel, max_loud, min_loud)
        if mode == "log_fixed":
            norm_loudness = min_max(loudness, min_loud, max_loud)
            norm_loudness = (loudness-max_loud)/40
            velocity = floor(127*pow(10, norm_loudness))
        elif mode == "log_range":
            norm_loudness = min_max(loudness, min_loud, max_loud)
            #print "norm_loudness", norm_loudness
            alpha = (min_loud-max_loud)/log10(min_vel/127.0)
            #print "alpha", alpha
            norm_loudness = (loudness-max_loud)/alpha
            #print "norm_loudness2", norm_loudness

            velocity = floor(127*pow(10, norm_loudness))
        elif mode == "linear":
            norm_loudness = (loudness-min_loud)/(max_loud-min_loud)
            norm_loudness = min_max(norm_loudness, 0, 1)
            velocity = norm_loudness*(max_vel-min_vel) + min_vel
        elif mode == "const":
            velocity = max_vel
        else:
            raise ValueError("Invalid loudness mapping: {}".format(mode))
        #print "loudness {} -> velocity {}".format(loudness, velocity)
        return velocity

    def createFromNoteTrack(self, noteTrack, name="NoteTrack"):
        """ Method to create a MIDIFile object for NoteTracks
            TODO: extend by velocity / loudness
        """
        #print "createFromNoteTrack"
        MyMIDI = MIDIFile(numTracks=1)

        tempo = 120
        #if self.tempo == "auto":
            #self.tempo, dummy = noteTrack.getMeanTempo(bpm=True)
            #self.tempo = int(round(self.tempo))

        # Tracks are numbered from zero. Times are measured in beats.
        time = 0

        # Add track name and tempo.
        MyMIDI.addTrackName(self.track, time, name)
        MyMIDI.addTempo(self.track, time, tempo)
        tempo_factor = tempo/60.

        if self.verbose:
            print("Creating MIDITrack from NoteTrack with: ")
            self.printInfo()

        if self.volume == "auto":
            try:
                max_l, min_l = noteTrack.getLoudnessRange()
            except:
                max_l, min_l = 80, 55
        for i, e in enumerate(noteTrack.events):
            # Add solo notes
            pi = e.pitch + self.transpose
            on = e.onsetSec * tempo_factor
            #print e.durationSec, tempo_factor
            du = e.durationSec * tempo_factor

            #print "Event #{}: ({}, {}, {})".format(i, pi, on, du)
            if self.volume == "auto":
                volume = self._loudnessToVelocity(solo_event=e, max_loud=max_l, min_loud=min_l, mode=self.loudness_map)
            else:
                volume = self.volume

            MyMIDI.addNote(self.track, self.channel, pi, on, du, volume)

        return MyMIDI

        # get score parameters from note track
        #pitch       = noteTrack.projection("pitch")
        #onsetSec    = noteTrack.projection("onset")
        #durationSec = noteTrack.projection("duration")
        #tempo_factor = tempo/60.
        # Add solo notes
        #for i in range(len(pitch)):
        #    pi = pitch[i] + self.transpose
        #    on = onsetSec[i] * factor
        #    du = durationSec[i] * factor
        #    MyMIDI.addNote(self.track, self.channel, pi, on, du, volume)

        #return MyMIDI


    def createFromMelody(self, melody, name="Melody", key=None):
        """ Method to create a MIDIFile object for Melody object
            TODO: extend by velocity / loudness
            """
        ticks_per_beat= melody.leastCommonTatum()
        #print "Least common Tatum", ticks_per_beat
        need_requant = self.ticks_per_beat > 0 and ticks_per_beat != self.ticks_per_beat
        requant_ticks = 64*9*5*7 if self.ticks_per_beat == 0 else self.ticks_per_beat
        #print "Requant: {}, need:{}".format(requant_ticks, need_requant)
        if not need_requant and ticks_per_beat > 65535:
            need_requant = True

        if need_requant:
            # print "Requantized from {} to {} ticks per beat".format(ticks_per_beat, requant_ticks)
            ticks_per_beat = requant_ticks
            mel = melody.setNewDivision(ticks_per_beat)
        else:
            mel = melody

        ticks_per_quarter = ticks_per_beat
        #if self.quantize and self.tempo == "auto":
        if self.tempo == "auto":
            try:
                self.tempo = mel.getMedianTempo(bpm=True)
                self.tempo = int(round(self.tempo))
            except:
                self.tempo =120
        #for MIDI there are only quarter notes for tempo, where we have beats that might be
        #dotted quarter also.
        #The reproduce the tempo we have to calculate a correction factir for this ternary
        #cases
        beat_factor = 1
        mp0 = mel[0].getMetricalPosition()

        primaryBeatDivision = mp0.getMeterInfo().getPrimaryBeatDivision()
        if primaryBeatDivision == "ternary":
            #print "Ternary"
            beat_factor = 3.0/2
            ticks_per_quarter = ticks_per_beat * 2.0/3
        elif primaryBeatDivision == "asymmetric":
            raise ValueError("Asymmetric beats not supported yet")

        #print "Beat factor:", primaryBeatDivision , beat_factor
        #print "Ticks per quarter:", ticks_per_quarter

        #some stupid calculation to get the right offset at the
        #beginning for correct upbeats

        bar_offset = 0
        beat_offset = 0
        if mel.hasUpbeat():
            #print "Melody has upbeat"
            mp0_dec = mp0.toDecimal()
            if self.quantize and mp0_dec<0:
                bar_offset = mp0.getBar()
            beat_offset = mp0_dec * mp0.getMeterInfo().period * beat_factor
            #print mp0, mp0.toDecimal(), mp0_dec, beat_offset
        tempo_factor = self.tempo/60.
        time = 0
        if self.verbose:
            print("Creating MIDITrack/NoteTrack with: ")
            self.printInfo()
        #print melody
        #mnay MIDI programs seem to have problems with to small ticks per beats
        #so ensure at least a value of 192 ticks per beat
        ticks_per_beat = max(ticks_per_beat, 192)

        MyMIDI = MIDIFile(numTracks=1, 
                          ticksPerBeat=ticks_per_beat, 
                          removeDuplicates=True, 
                          deinterleave=True)

        MyMIDI.addTrackName(self.track, time, name)
        MyMIDI.addTempo(self.track, time, self.tempo)
        if key != None and not key.empty():
            accidentals, maj_marker = key.getMIDIKeyEvent()
            if accidentals < 0:
                accidentals = 256 + accidentals
            MyMIDI.addKeySignature(self.track, time, accidentals, maj_marker)

        num, denom = 0, 0
        #metricalIOIs= []
        on = 0
        #duration quantization is useful to get rid of all the artificial rests
        #in real-time data
        if self.quantize:
            #metricalIOIs = melody.getMetricalIOIsDecimal()
            qpos = melody.getQuarterPositionsDecimal()

        if self.quantize_duration:
            qposIOIs = melody.getQuarterIOIsDecimal()
            du = mel.events[-1].durationSec * tempo_factor / beat_factor
            qposIOIs.append(du)

        if self.volume == "auto":
            try:
                max_l, min_l = melody.getLoudnessRange()
            except:
                self.volume = 100

        for i, e in enumerate(mel.events):
            # Add solo notes
            pi = e.pitch + self.transpose
            if self.quantize:
                on = qpos[i]
            else:
                on = e.onsetSec * tempo_factor + beat_offset
            if self.quantize_duration:
                du = qposIOIs[i]
                cmp_du = e.durationSec * tempo_factor
                #fix very long IOIs for better and good
                #use some heuristics.
                if (du-cmp_du)>1:
                    new_du = round(cmp_du*2)/2
                    if new_du<.5:
                        new_du = .5
                    du = new_du

            else:
                #print e.durationSec, tempo_factor
                du = e.durationSec * tempo_factor

            #add time signature at same time as triggering event
            if i == 0:
                time = 0
            else:
                time = on
            tmp_num, tmp_denom = self._getTimeSignatureInfo(e)
            if num != tmp_num or denom != tmp_denom:
                MyMIDI.addTimeSignature(self.track, time, tmp_num, tmp_denom)
                num, denom = tmp_num, tmp_denom
                #print "New Meter: ", num, denom
            #print "Event #{}: ({}, {}, {})".format(i, pi, on, du)
            if self.volume == "auto":
                volume = self._loudnessToVelocity(solo_event=e, max_loud=max_l, min_loud=min_l, mode=self.loudness_map)
            else:
                volume = self.volume

            MyMIDI.addNote(self.track, self.channel, pi, on, du, volume)
        return MyMIDI


    def writeMIDIFile(self, noteTrack, midiFileName, trackName = "", key=None):
        """ Methd to write note track to MIDI file
            TODO: extend by velocity / loudness
            """
        # Create the MIDIFile Object with 1 track

        if isinstance(noteTrack, Melody) and not self.tempo == "raw":
            MyMIDI = self.createFromMelody(noteTrack, key=key)
        else:
            MyMIDI = self.createFromNoteTrack(noteTrack)


        #print "Writing {} with tempo: {}, transpose:{}, track:{}, channel: {}, instr: {}".format(midiFileName, self.tempo, self.transpose, self.track, self.channel, self.instrument)
        # And write it to disk.
        binfile = open(midiFileName, 'wb')
        #print "="*60
        #print MyMIDI.printRawEventList(0)
        MyMIDI.writeFile(binfile)
        binfile.close()
        #print "="*60
        #MyMIDI.printTrack(0)

    def writeMIDIFileRaw(self, tempo, pitch, onsets, durations, midiFileName):
        """ Method to write raw list of pitch, onsets, durations to MIDI file
            ignores all other settings
            TODO: extend by velocity / loudness
            """
        # Create the MIDIFile Object with 1 track
        MyMIDI = MIDIFile(numTracks=1)

        # Tracks are numbered from zero. Times are measured in beats.
        track   = 0
        time    = 0

        # Add track name and tempo.
        MyMIDI.addTrackName(track, time, "Raw")
        #MyMIDI.addTempo(track, time, self.tempo)
        #print "Writing with ", tempo
        factor = float(tempo)/60.
        # get score parameters from note track
        # Add solo notes
        if self.volume == "auto":
            volume = 100

        for i in range(len(pitch)):
            track = 0
            channel = 0
            pi = pitch[i]
            on = onsets[i] * factor
            du = durations[i] * factor
            #volume = self.volume
            MyMIDI.addNote(track, channel, pi, on, du, volume)

        # And write it to disk.
        binfile = open(midiFileName, 'wb')
        MyMIDI.writeFile(binfile)
        binfile.close()


    def printInfo(self):
        print("Tempo: {}, transposition: {}, volume: {}".format(self.tempo, self.transpose, self.loudness_map))
        print("Instrument: {}, channel:{}, track: {}".format(self.instrument, self.channel, self.track))
        print("Quantization: {}, duration-quant: {}".format(self.quantize, self.quantize_duration))
