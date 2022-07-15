""" Wrapper of MIDI package """

import sys

from melospy.basic_representations.metrical_annotator import *
from melospy.basic_representations.popsong_meta_data import *
from melospy.basic_representations.solo import *
from melospy.external.midi.MidiInFile import MidiInFile
from melospy.external.midi.MidiOutStream import MidiOutStream
from melospy.input_output.midi_params import MIDIReaderParams


class MidiIntermediateBeat(object):
    def __init__(self, note_event, bar, beat, beat_rest):
        self.note_event = note_event
        self.bar = bar
        self.beat = beat
        self.beat_rest = beat_rest

    def __str__(self):
        return "note:{}|bar:{}|beat:{}|rest:{}".format(self.note_event, self.bar, self.beat, self.beat_rest)


class MidiNote(object):
    def __init__(self, onset_ticks, pitch, duration, velocity=100):
        self.onset_ticks = onset_ticks
        self.pitch = pitch
        self.duration = duration

    def to_note_event(self, division, beat_dur):
        onset = float(self.onset_ticks)/division * beat_dur
        duration = float(self.duration)/division * beat_dur
        ne = NoteEvent(self.pitch, onset, duration)
        return ne

    def __str__(self):
        return "p:{}|on:{}|dur:{}".format(self.pitch, self.onset_ticks, self.duration)

class TempoMapEvent(object):
    def __init__(self, onset_ticks, event, event_type):
        self.onset_ticks = onset_ticks
        self.event = event
        self.event_type = event_type

    def __str__(self):
        return "{}|onset:{}|event:{}".format(self.event_type, self.onset_ticks, self.event)

    def __eq__(self, tme):
        if tme is None:
            return False
        return tme.event_type == self.event_type and tme.onset_ticks == self.onset_ticks and tme.event == self.event

    def __ne__(self, tme):
        return  not self.__eq__(tme)

class MidiStream(object):
    def __init__(self, n_track, channel):
        self.n_track = n_track
        self.channel = channel
        self.events = []

    def append(self, event):
        self.events.append(event)

    def __len__(self):
        return len(self.events)

    def __iter__(self):
        return iter(self.events)

    def __getitem__(self, i):
        return self.events[i]


class MidiStreamCollection(object):
    def __init__(self):
        self.streams = {}

    def add(self, event, n_track, channel):
        if n_track not in self.streams:
            self.streams[n_track] = {}
        if channel not in self.streams[n_track]:
            self.streams[n_track][channel] = []
        self.streams[n_track][channel].append(event)
        #print "Added event {} for track {} with channel {}".format(event, n_track, channel)

    def number_of_tracks(self):
        return len(list(self.streams.keys()))

    def get_track_numbers(self):
        return list(self.streams.keys())

    def number_of_channels(self, n_track):
        return len(self.get_channel_numbers(n_track))

    def get_channel_numbers(self, n_track):
        try:
            return list(self.streams[n_track].keys())
        except:
            raise ValueError("Invalid track number {}".format(n_track))

    def get_stream(self, n_track, channel=None):
        try:
            track = self.streams[n_track]
        except:
            raise ValueError("Invalid track number: {}, {}".format(n_track))
        if channel is None:
            return track
        try:
            return track[channel]
        except:
            raise ValueError("Invalid channel number: {}, {}".format(channel))

class MidiToMelody(MidiOutStream):
    """ Event handler for MIDIReader2"""

    def __init__(self):
        self.note = None
        self.division = 0
        self.n_tracks = 0
        self.key = None
        self.format=0
        self.tempo_map = {}
        self.note_events = MidiStreamCollection()
        self.cur_track = -1
        self.event_stack = {'main': {}, 'twins': {}}

    def set_default_tempo_map(self):
        self.tempo_map = {}
        event = TempoMapEvent(0, Signature(4, 4), "signature")
        self.add_tempo_map_event("signature", event)
        event = TempoMapEvent(0, .5, "tempo")
        self.add_tempo_map_event("tempo", event)

    def number_of_note_tracks(self):
        return self.note_events.number_of_tracks()

    def number_of_channels(self, n_track):
        return self.note_events.number_of_channels(n_track)

    def has_tempo_map(self):
        return len(self.tempo_map) > 0

    def contains(self, tempo_map_event):
        if tempo_map_event.event_type not in self.tempo_map:
            return False
        for tme in self.tempo_map[tempo_map_event.event_type]:
            if tme == tempo_map_event:
                return True
        return False

    def add_tempo_map_event(self, event_type, event):
        if event_type not in self.tempo_map:
            self.tempo_map[event_type] = []
        #print "Contains", event, self.contains(event)
        if not self.contains(event):
            self.tempo_map[event_type].append(event)
            #print("Added tempo map event",  event)

    def get_notetrack_numbers(self):
        return self.note_events.get_track_numbers()

    #############################
    # channel events
    def push_event(self, n_track, channel, pitch, onset_ticks, which = 'main'):
        #print self.note_events.keys()

        if n_track not in self.event_stack[which]:
            self.event_stack[which][n_track] = {}
        if channel not in self.event_stack[which][n_track]:
            self.event_stack[which][n_track][channel] = []
        self.event_stack[which][n_track][channel] = (pitch, onset_ticks)
        #print("Pushed pitch {} for track: {} and channel {} with onset:{}".format(pitch, n_track, channel, onset_ticks))

    def pop_event(self, n_track, channel, which = 'main'):
        #print self.note_events.keys()
        #print(self.event_stack)
        #print("which: {}, n_track: {}, channel: {}".format(which, n_track, channel))
        if(self.stack_set(n_track, channel, which)):
            return self.event_stack[which][n_track][channel]
        #try:
        #    ret = self.event_stack[which][n_track][channel]
        #    print("ret: ", ret, self.stack_set(n_track, channel, which))
        #except:
        #    pass
        return (None, None)
        
    
    def clear_stack(self, n_track, channel, which = 'main'):
        try:
            self.event_stack[which][n_track][channel] = None
            #print("Cleared stack {} Track: {} Channel: {}".format(which, n_track, channel))
        except:
            pass

    def stack_set(self, n_track, channel, which = 'main'):
        try:
            return self.event_stack[which][n_track][channel] is not None
        except:
            pass

    def swap_stacks(self, n_track, channel):
        tmp = self.event_stack['main'][n_track][channel]
        self.event_stack['main'][n_track][channel] = self.event_stack['twins'][n_track][channel]
        self.event_stack['twins'][n_track][channel]  = tmp
        #print "Swapped stacks"

    def print_stacks(self, n_track, channel):
        try:
            main_stack = self.event_stack['main'][n_track][channel]
        except:
            main_stack  = None
        try:
            twin_stack = self.event_stack['twins'][n_track][channel]
        except:
            twin_stack   = None
        #print("Main: {}, Twins: {}".format(main_stack, twin_stack))

    def note_on(self, channel=0, note=0x40, velocity=0x40):
        #print("-"*60)
        #print('note_on  - ch:%02X,  note:%02d,  vel:%02X time:%s' % (channel, note, velocity, self.abs_time()))
        if velocity == 0:
            self.note_off(channel, note, velocity)
            return
        if self.stack_set(self.cur_track, channel, 'main'):
            #Sometimes a NoteOn and a NoteOff are erroneouly swapped
            #in monophponic MIDIs so we use a second stack to work around
            #this shit
            if self.stack_set(self.cur_track, channel, 'twins'):
                raise ValueError("Channel {} of track {} not monophonic".format(channel, self.cur_track))
            else:
                self.push_event(self.cur_track, channel, note, self.abs_time(), "twins")
        else:
            self.push_event(self.cur_track, channel, note, self.abs_time(), "main")
        #self.print_stacks(self.cur_track, channel)

    def note_off(self, channel=0, note=0x40, velocity=0x40):
        #print('note_off - ch:%02X,  note:%02d,  vel:%02X time:%s' % (channel, note, velocity, self.abs_time()))
        #self.print_stacks(self.cur_track, channel)
        cur_stack = 'main'
        duration = self.rel_time()
        pitch, onset = self.pop_event(self.cur_track, channel, "main")
        if onset is None or pitch is None:
            print("Warning: Invalid note off even in track {}/channel {}".format(self.cur_track, channel))
            return
            #raise ValueError("Invalid track and/or channel number: {}, {}".format(self.cur_track, channel))
        if pitch != note:
            pitch1, onset1 = self.pop_event(self.cur_track, channel, 'twins')
            if pitch1 != note:
                raise ValueError("Channel {} of track {} not monophonic".format(channel, self.cur_track))
            #cur_stack = "twins"
            #print "Channel {} of track {} not monophonic".format(channel, self.cur_track)
            #raise ValueError("Channel {} of track {} not monophonic".format(channel, self.cur_track))

        mn = MidiNote(onset, note, duration, velocity)
        self.note_events.add(mn, self.cur_track, channel)
        self.clear_stack(self.cur_track, channel, cur_stack)
        if self.stack_set(self.cur_track, channel, 'twins'):
            self.swap_stacks(self.cur_track, channel)

    #########################
    # header does not really belong here. But anyhoo!!!

    def header(self, format=0, nTracks=1, division=96):
        #print 'format: %s, nTracks: %s, division: %s' % (format, nTracks, division)
        #print '----------------------------------'
        #print ''
        self.format = format
        #if format == 0:
        #    raise RuntimeError("MIDI file with Format 0 currently not supported")

        self.division = division
        self.n_tracks = nTracks
        #if nTracks > 1 and format != 2:
        #    raise RuntimeError("Found more than one track")

    def eof(self):
        #print 'Done'
        pass

    def start_of_track(self, n_track=0):
        #print 'Start - track #%s' % n_track
        self.cur_track = n_track

    def end_of_track(self):
        #print 'End of track #', self.cur_track
        #print ''
        self.cur_track = -1

    #####################
    ## meta events


    def sequence_name(self, text):
        #print 'sequence_name:', text
        pass

    def instrument_name(self, text):
        #print 'instrument_name:', text
        pass

    def tempo(self, value):
        #print 'tempo:', value
        beat_dur = float(value)/1000000.
        #print "Cur tempo :{} ( {} bpm)".format(self.cur_beat_dur, 60./self.cur_beat_dur)
        event = TempoMapEvent(self.abs_time(), beat_dur, "tempo")
        self.add_tempo_map_event("tempo", event)

    def time_signature(self, nn, dd, cc, bb):
        print('time_signature:', nn, dd, cc, bb, 2**dd)
        sig  = Signature(nn, 2**dd)
        event = TempoMapEvent(self.abs_time(), sig, "signature")
        self.add_tempo_map_event("signature", event)

    def key_signature(self, sf, mi):
        if sf > 127:
            #sf is signed char, negative values are flats
            pc = -((256-sf)*5 % 12)
        else:
            pc = sf*7 % 12
        n = NoteName.fromMIDIPitch(abs(pc), useSharp=pc>=0,  generic=True)
        key = Key(n, ["maj", "min"][mi])
        if self.key is None:
            self.key = key
            #print "Key", key

class MIDIReader2(object):
    """ Class for reading MIDI files """

    def __init__(self, filename=None, params=None):
        self.filename = filename
        if isinstance(params, dict):
            params = MIDIReaderParams.fromDict(params)
        if params == None:
            params = MIDIReaderParams()
        self.params = params
        self.__melody   =  None
        if filename:
            self.__melody  = self.readMIDIFile(filename)

    def getMelody(self):
        return self.__melody

    def analyseMIDIFile(self, filename):
        """ Method to analyse a MIDI file
            """
        pass

    def _add_dummy_phrase(self, mel, dummy_phrase_id=0):
        sl = SectionList("PHRASE")
        sl.append(Section("PHRASE", dummy_phrase_id, 0, len(mel)-1))
        if isinstance(mel, Solo):
            if mel.getPhraseSections() is None:
                s = mel.setPhraseSections(sl)
        else:
            s = Solo(melody=mel, phrases=sl)
        return s

    def quantize(self, event_buffer):
        if len(event_buffer) == 0:
            return []
        params = FlexQParams(oddDivisionPenalty = 0.,
                             mismatchPenalty = 0.,
                             spreadPenalty = 0.)
        ma = MetricalAnnotator(NoteTrack(), params=params)
        events = [ev.beat_rest for ev in event_buffer]
        debug = False
        #if len(event_buffer) == 3:
        #    debug = True
        try:
            ret = ma.quantize(events,
                              rhythmThreshold = 0.0,
                              debug = debug,
                              max_division = 100)
        except Exception as e:
            #print "Event buffer:\n", "\n  - ".join([str(_) for _ in event_buffer])
            raise e
        #print "Ret: ", ret
        return ret

    def getMetricalNoteEvents(self, event_buffer, beat_dur, mi):
        #print("getMetricalNoteEvents called buffer len {}".format(len(event_buffer)))
        if len(event_buffer) == 0:
            return []
        tatum, pos = self.quantize(event_buffer)
        if len(pos) != len(event_buffer):
            tatum = len(event_buffer)
            pos = list(range(0, len(event_buffer)))
            print("Could not find optimal quantization: quantizing hard.")
        bi = BeatInfo(tatum, beat_dur)
        mc = MetricalContext(bi, mi)
        mnes = []
        for i in range(len(event_buffer)):
            ev = event_buffer[i]
            onset = ev.note_event.getOnset()
            pitch = ev.note_event.getPitch()
            duration = ev.note_event.getDuration()
            bar   = ev.bar
            beat  = ev.beat
            mp  = MetricalPosition(bar, beat, pos[i]+1, 0, mc)
            mne = MetricalNoteEvent(onset, pitch, mp, duration)
            #if onset <5:
            #    print("mne", mne)
            #print("ev", ev.note_event)
                    
            mnes.append(mne)
        return mnes

    def parse_streams(self, midi_to_melody, track_no):
        mtm = midi_to_melody
        tempo_map = mtm.tempo_map
        print(tempo_map)
        div = mtm.division
        ret = Solo()
        try:
            track = mtm.note_events.get_stream(track_no)
        except:
            raise ValueError("Invalid track number: {}".format(track_no))
        channels = list(track.keys())
        if len(channels) > 1:
            print(ValueError("Found more than one channel in note track. Using first #{}".format(channels[0])))

        nt = track[channels[0]]
        #print("\n".join([str(_) for _ in nt]))
        signatures = tempo_map["signature"]

        sig_changes = [sig.onset_ticks for sig in signatures]
        sig_pointer = 0
        cur_sig = signatures[sig_pointer]

        beat_factor = cur_sig.event.getBeatFactor(music21Mode=True, as_fraction=True)
        cur_mi = MeterInfo.fromSignature(cur_sig.event)

        tempos = tempo_map["tempo"]
        #print(tempos)
        tempo_changes = [t.onset_ticks for t in tempos]
        tempo_pointer = 0
        qbeat_dur = tempo_map["tempo"][tempo_pointer].event
        #qbeat_dur = .5
        #print(qbeat_dur)
        beat_dur = qbeat_dur * beat_factor
        #print("Cur sig:{}\nBeat factor:{}\nqbeat_dur:{}\nbeat_dur:{}".format(cur_sig, beat_factor, qbeat_dur, beat_dur))
        event_buffer = []
        qper = cur_mi.getQuarterLength()
        if qper != int(qper) and beat_factor != Fraction(3, 2):
            raise RuntimeError("Aksak meter currently not supported {}".format(qper))
        qper = int(qper)

        bar_offset = 1 if nt[0].onset_ticks == 0 else 0
        old_beat_int = None
        old_bar = None
        sig_change_offset = 0
        for e in nt:
            if len(sig_changes) > 1 and sig_pointer < len(sig_changes)-1:
                if e.onset_ticks >= sig_changes[sig_pointer +1]:
                    sig_pointer += 1
                    #print("New signatures:", signatures[sig_pointer])
                    cur_sig = signatures[sig_pointer]
                    beat_factor = cur_sig.event.getBeatFactor(music21Mode=False, as_fraction=True)
                    cur_mi = MeterInfo.fromSignature(cur_sig.event)
                    beat_dur = qbeat_dur * beat_factor
                    qper = cur_mi.getQuarterLength()
                    if qper != int(qper) and beat_factor != Fraction(3, 2):
                        raise RuntimeError("Aksak meter currently not supported {}".format(qper))
                    qper = int(qper)
                    sig_change_offset = sig_changes[sig_pointer]
            if len(tempo_changes) > 1 and tempo_pointer < len(tempo_changes)-1:
                if e.onset_ticks >= tempo_changes[tempo_pointer +1]:
                    tempo_pointer += 1
                    #print("New tempo:", tempos[tempo_pointer])
                    qbeat_dur = tempo_map["tempo"][tempo_pointer].event
                    qbeat_dur = .5
                    beat_dur = qbeat_dur * beat_factor
                    
            abs_qbeat = Fraction(e.onset_ticks - sig_change_offset, div)
            rel_qbeat = abs_qbeat % qper
            bar = int(abs_qbeat / qper)

            beat = rel_qbeat/beat_factor
            beat_rest = beat - int(beat)
            beat_int = int(beat)
            if old_beat_int is None:
                old_beat_int  = beat_int
            if old_bar is None:
                old_bar = bar
            #print("="*60)
            #print("Onset: {}, bar: {}, old_bar:{}".format(e.onset_ticks, bar, old_bar))
            #print("Abs_qbeat:{}, Abs_qbeat_int:{}".format(abs_qbeat, abs_qbeat_int))
            #print("Beat:{},  Beat_int:{}, Old_Beat:{}, beat_rest:{}".format(beat, beat_int, old_beat_int, beat_rest))
            beat_change = beat_int != old_beat_int or bar != old_bar
            if beat_change and event_buffer:
                mnes = self.getMetricalNoteEvents(event_buffer, beat_dur, cur_mi)
                ret.extend(mnes)
                event_buffer = []

            ne = e.to_note_event(div, qbeat_dur)
            mib = MidiIntermediateBeat(ne, bar + bar_offset, beat_int + 1, beat_rest)
            event_buffer.append(mib)
            #print("->Appended event {}, new len:{}".format(mib, len(event_buffer)))

            old_beat_int = beat_int
            old_bar = bar

        #print  beat_change, len(event_buffer)
        if event_buffer:
            mnes = self.getMetricalNoteEvents(event_buffer, beat_dur, cur_mi)
            ret.extend(mnes)
        return ret

    def readMIDIFile(self, filename, track_no=None, dummy_phrases=False):
        """
        Method to read a MIDI file.

        Args:
            filename: Name of file to read
            track_no: If MIDI file is not monophonic track number to use
            dummy_phrases: if set, a single phrase spanning the whole MIDI is

        Return:
            One of these objects:
            - NoteTrack (if no meter information was found in the MIDI)
            - Solo (if meter information was present and dummy_phrases was set to True)
        """
        psi = PopSongInfo()
        mel = None
        mtm = MidiToMelody()
        midiIn = MidiInFile(mtm, filename)
        midiIn.read()
        #print "Read MIDI stream", filename
        #print "\n".join([str(_) for _ in mtm.tempo_map])
        #print "Number of tracks", mtm.n_tracks
        #print "Number of note tracks", mtm.number_of_note_tracks()
        #print "Note track ids", mtm.get_notetrack_numbers()
        #print "Has tempo map", mtm.has_tempo_map()
        if mtm.number_of_note_tracks() > 1:
            raise RuntimeError("Midi file has more than one note track: #Tracks: {}".format(mtm.number_of_note_tracks() ))
        if not mtm.has_tempo_map():
            print("Midi file has no tempo map, assuming 120 bpm and 4/4")
            mtm.set_default_tempo_map()
        track_no = mtm.get_notetrack_numbers()[0]

        mel = self.parse_streams(mtm, track_no)
        if self.params != None and self.params.add_dummy_phrases:
            try:
                mel = self._add_dummy_phrase(mel)
            except:
                pass

        psi.filename = filename
        beat_durs = [_.event for _ in mtm.tempo_map["tempo"]]
        if len(beat_durs) > 0:
            psi.setAvgTempoBPM(60./mean(beat_durs))

        try:
            psi.signature = mtm.tempo_map["signature"][0].event
        except:
            psi.signature = Signature(4, 4)
        psi.key = mtm.key
        if not psi.key:
            psi.key = mel.estimateKey()
        md = PopSongMetaData(psi)
        #print "PopSongMetaData", md
        mel.setMetadata(md)
        return mel

    melody = property(getMelody)
