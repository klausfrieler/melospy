import csv
import subprocess
import time
from os.path import expanduser

import pandas

from melospy.basic_representations.annotated_beat_track import AnnotatedBeatTrack
from melospy.basic_representations.f0_modulation import F0Modulation
from melospy.basic_representations.jm_util import get_safe_value_from_dict, void
from melospy.basic_representations.key import Key
from melospy.basic_representations.loudness import Loudness
from melospy.basic_representations.note_event import NoteEvent
from melospy.basic_representations.note_track import NoteTrack
from melospy.basic_representations.solo import Solo
from melospy.basic_representations.song import Song
from melospy.input_output.lilypond_writer2 import LilypondWriter2
from melospy.input_output.mcsv_writer import MCSVWriter
from melospy.input_output.mel_db_adapter_factory import MelDBAdapterFactory
from melospy.input_output.melody_importer import MelodyImporter
from melospy.input_output.metadata_provider import MetadataProvider
from melospy.input_output.midi_writer import MIDIWriter
from melospy.tools.commandline_tools.dbinfo import DBInfo
from melospy.tools.commandline_tools.util import *


class MelodyConverter(object):
    """Compact class for melody conversion"""
    def __init__(self, params, src_dbi, dir_paths_params):
        self.params          = params
        self.wdir            = dir_paths_params.get("wdir")
        self.outdir          = self._outdir(dir_paths_params.get("outdir"))
        self.bundles         = params.get("bundles")
        self.output_format   = params.get("output_format")
        self.input_format    = params.get("input_format")
        self.transpose       = params.get("transpose")
        self.output_params   = params.get("output_params")
        try:
            self.output_params.pop("format", None)
        except:
            pass
        self.sink_dbi        = DBInfo.fromDict(params.get("sink_dbi"))
        self.src_dbi         = DBInfo.fromDict(src_dbi.as_dict())
        self.db_adapter      = None
        if self.transpose == None and self.output_params != None:
            self.transpose= get_safe_value_from_dict(self.output_params, "transpose", 0)

        self.melody_importer_params = parse_melody_importer_params(params)
        svparams = self.melody_importer_params["sv_reader"]
        krnparams = self.melody_importer_params["krn_reader"]
        mcsvparams = self.melody_importer_params["mcsv_reader"]
        self.meta_data_file  = svparams["metadata_file"]
        if not self.meta_data_file:
            self.meta_data_file  = krnparams["metadata_file"]
        if not self.meta_data_file:
            self.meta_data_file  = mcsvparams["metadata_file"]

        self.loudness_dir    = svparams["loudness_dir"]
        self.walkingbass_dir = svparams["walkingbass_dir"]
        self.starttimes      = svparams["start_times_file"]
        self.starttimes_cache= {}
        self.loudness_data_frame = None
        self.walkingbass_df      = None
        self.melid_map           = None

        output_extensions = {"csv":"csv",
                             "database":"db",
                             "lilypond":"ly",
                             "mcsv":"csv",
                             "mcsv1":"csv",
                             "mcsv2":"csv",
                             "meter":"txt",
                             "mid":"mid",
                             "midi":"mid",
                             "notes":"txt"}

        try:
            self.output_ext = output_extensions[self.output_format.lower()]
        except:
            raise ValueError("Unknown or missing output format: {}".format(self.output_format))

        if self.output_format == "database":
            if not self.sink_dbi:
                raise RuntimeError("Output format is 'database', but no sink database is specified")

            if self.sink_dbi.type != "sqlite3":
                raise ValueError("Only SQLITE3 database supported, got: {}".format(self.sink_dbi.type))

            if self.outdir and os.path.dirname(self.sink_dbi.path) == "":
                self.sink_dbi.path = add_path_sep(self.outdir) + self.sink_dbi.path
            self.sink_dbi.use = True

            if self.src_dbi.use and self.sink_dbi.path == self.src_dbi.path:
                raise ValueError("Source and sink database must differ: {} ==  {}".format(self.src_dbi.path, self.sink_dbi.path))
        self.bucket = []

    def _outdir(self, outdir_param):
        if "%(home_dir)s" in outdir_param:
            return outdir_param % {"home_dir": expanduser("~")}
        return outdir_param

    def write_mcsv(self, mel, outfile, params):
        mel.transpose(self.transpose)
        try:
            style= params["style"]
        except:
            style  = "simile"
        mcsvw = MCSVWriter(mel, style=style)
        mcsvw.write(outfile)

    def write_mcsv2(self, mel, outfile, params):
        mel.transpose(self.transpose)
        
        try:
            annotations = params["annotations"]
        except:
            annotations = []
        try:
            metadata = params["metadata"]
        except:
            metadata  = []
        try:
            with_loudness = params["loudness"]
        except:
            with_loudness = False
        try:
            with_f0mod = params["f0mod"]
        except:
            with_f0mod = False
        try:
            decimal = params["decimal"]
        except:
            decimal = "."
        try:
            sep = params["sep"]
        except:
            sep = ";"
        try:
            exclude_empty= params["exclude_empty"]
        except:
            exclude_empty = True

        try:
            export_beat_track = str(params["export_beat_track"])
        except:
            export_beat_track = "False"

        if export_beat_track.lower() != "false":
            try:
                basename, ext = os.path.splitext(outfile)
                btf = basename + "_beattrack" + ext
                bt = mel.beattrack_as_dataframe(exclude_empty=exclude_empty)
                bt.to_csv(btf, sep=sep, decimal=decimal, index=False)
            except:
                raise RuntimeError("Could not export beat track for {}".format(os.path.basename(outfile)))
                pass
        if export_beat_track.lower() != "only":
            if isinstance(mel, Solo):
                df = mel.to_dataframe(annotations     = annotations,
                                      metadata        = metadata, 
                                      exclude_empty   = exclude_empty, 
                                      ignore_loudness = not with_loudness, 
                                      ignore_f0mod    = not with_f0mod)
            else:
                df = mel.to_dataframe(ignore_loudness = not with_loudness, 
                                      ignore_f0mod    = not with_f0mod)

            df.to_csv(outfile,
                      sep=sep,
                      decimal=decimal,
                      index=False)

    def write_meter(self, mel, outfile):
        with open(outfile, 'w') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',', lineterminator="\n", quotechar='|', quoting=csv.QUOTE_MINIMAL)
            onsets = mel.export("onset")
            meter  = mel.export("meter")
            for k in range(len(onsets)):
                row =[str(onsets[k]), str(meter[k])]
                csvwriter.writerow(row)

    def write_notes(self, mel, outfile):
        annotate_phrases = get_safe_value_from_dict(self.output_params, 'annotate-phrases', False)
        with_durations   = get_safe_value_from_dict(self.output_params, 'with-duration', False)
        with_offsets     = get_safe_value_from_dict(self.output_params, 'with-offset', False)
        pitch_first      = get_safe_value_from_dict(self.output_params, 'pitch-first', False)
        with open(outfile, 'w') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=',', lineterminator="\n", quotechar='|', quoting=csv.QUOTE_MINIMAL)
            onsets = mel.export("onset")
            notes  = mel.export("pitch")
            if with_offsets or with_durations:
                durations = mel.export("duration")
            if annotate_phrases:
                phrase_bounds = mel.export("phrase-boundaries")
            for k in range(len(onsets)):
                if pitch_first:
                    row =[str(notes[k]+self.transpose), str(onsets[k])]
                else:
                    row =[str(onsets[k]), str(notes[k]+self.transpose)]
                if with_offsets:
                    row.append(str(onsets[k] + durations[k]))
                if with_durations:
                    row.append(str(durations[k]))
                if annotate_phrases:
                    row.append(str(phrase_bounds[k]))
                csvwriter.writerow(row)

    def write_midi(self, mel, outfile, verbose=False, key=None):
        #midi_writer = MIDIWriter(tempo=tempo, transpose=transpose, quantize=quantize, quantize_duration=quantize_duration, channel=channel, instrument=instrument, track_no=track_no)
        midi_writer = MIDIWriter(self.output_params, verbose=verbose)
        midi_writer.writeMIDIFile(mel, outfile, key=key)

    def write_lilypond(self, mel, outfile, verbose=False):
        lily_writer = LilypondWriter2(melody=None, params=self.output_params)
        lily_writer.write(outfile, mel)
        try:
            post_process = self.output_params["post_process"].lower()
        except:
            post_process = ""

        if post_process in ["png", "pdf"]:
            try:
                print(subprocess.check_output(['lilypond', '-f', post_process, '-o', os.path.splitext(outfile)[0], outfile]))
            except:
                pass

    def read_loudness_data(self, filename="df_notes.csv"):
        if self.loudness_dir is None or not self.loudness_dir:
            return
        if self.loudness_data_frame is not None:
            return

        full_path  = os.path.join(self.loudness_dir, filename)
        #full_path = filename
        print("Reading loudness data from {}...".format(full_path))
        self.loudness_data_frame = pandas.read_csv(full_path)
        self.loudness_data_frame.f0_mod.fillna("", inplace=True)
        print("...read {} lines".format(len(self.loudness_data_frame)))
        if self.melid_map is None:
            self.melid_map = pandas.read_csv(os.path.join(self.loudness_dir, "filename_sv.csv"))
        return

    def get_melid_from_basename(self, base_name):
        #OUT OF TRY
        #melid = self.melid_map.query('filename_sv == "{}"'.format(base_name))["melid"]
        try:
            melid = int(self.melid_map.query('filename_sv == "{}"'.format(base_name))["melid"])
            # print "Found melid {} for {}".format(melid, base_name)
        except:
            melid = None
        return melid

    def get_loudness_and_f0mod_data(self, filename):
        if self.loudness_data_frame is None:
            self.read_loudness_data()

        base_name = os.path.basename(filename)
        melid = self.get_melid_from_basename(base_name)
        if melid is None:
            print("Could not find melid for {}".format(base_name))
            return []
        loudness = self.loudness_data_frame.query("melid == {}".format(melid))

        if len(loudness) == 0:
            print("No loudness data found for base_name {}".format(base_name))
            return []
        #onsets = list(loudness["onset"])
        note_ids = list(loudness["noteid"])
        tmp = loudness[["intensity_solo_max", "intensity_solo_median", "intensity_solo_std", "intensity_solo_rel_peak_pos", "intensity_solo_temp_centroid", "intensity_backing_median", "f0_mod", "f0_av_f0_dev_median", "f0_mod_freq_hz", "f0_mod_range_cent"]]
        tmp.columns = ["max", "median", "stddev", "rel_peak_pos", "temp_centroid", "backing_median", "annotated", "median_dev", "freq_hz", "range_cents"]
        loud_ret = []
        f0_ret = []
        for i in range(len(tmp)):
            values = tmp[i:(i+1)]
            try:
                s2b = float(values["median"])/float(values["backing_median"])
            except:
                s2b = None
            l = Loudness(float(values["max"]), float(values["median"]),
                         float(values["stddev"]), float(values["rel_peak_pos"]),
                         float(values["temp_centroid"]), s2b)

            f = F0Modulation("",
                             float(values["range_cents"]),
                             float(values["freq_hz"]),
                             float(values["median_dev"]))
            loud_ret.append(l)
            f0_ret.append(f)

        return loud_ret, f0_ret, note_ids

    def read_walkingbass_data(self, filename="df_beats.csv"):
        if self.walkingbass_dir == "":
            return
        if self.walkingbass_df is not None:
            return
        full_path  = os.path.join(self.walkingbass_dir, filename)
        #full_path = filename
        print("Reading walking bass data from {}...".format(full_path))
        self.walkingbass_df = pandas.read_csv(full_path)
        print("...read {} lines".format(len(self.walkingbass_df)))
        if self.melid_map  is None:
            self.melid_map = pandas.read_csv(os.path.join(self.loudness_dir, "filename_sv.csv"))
        return

    def get_walkingbass_data(self, filename):
        if self.walkingbass_df is None:
            self.read_walkingbass_data()

        base_name = os.path.basename(filename)
        melid = self.get_melid_from_basename(base_name)
        if melid is None:
            print("Could not find melid for {}".format(base_name))
            return []
        wb_data = self.walkingbass_df.query("melid == {}".format(melid))

        if len(wb_data) == 0:
            print("No walking bass data found for {}".format(base_name))
            return []
        ret = NoteTrack()
        onset   = list(wb_data["onset"])
        duration = list(wb_data["bass_confidence"])
        pitch = list(wb_data["bass_pitch"])
        for i, _ in enumerate(onset):
            wbne = NoteEvent(pitch[i], onset[i], duration[i])
            #old: wbne = NoteEvent(int(row[2]), float(row[0]), float(row[1])-float(row[0]))
            ret.append(wbne)
        print("Retrieved walking bass data of length {}".format(len(ret)))
        return ret

    def read_starttimes(self, tune, delimiter=";"):
        if self.starttimes == "":
            return None

        if len(self.starttimes_cache) == 0:
            #print "Reading data...", self.starttimes
            with open(self.starttimes) as csvfile:
                csvreader = csv.reader(csvfile, delimiter=delimiter)
                for row in csvreader:
                    sv_file = str(row[0])
                    start_time = float(row[1])
                    self.starttimes_cache[sv_file] = start_time
                    #print "Added {} with start time {}".format(sv_file, start_time)
                print("Read {} start times".format(len(self.starttimes_cache)))

        try:
            tune = os.path.basename(tune)
            st = self.starttimes_cache[tune]
        except:
            st = -1
        return st

    def add_to_bucket(self, mel, tune, melody_importer, idx, verbose=False):
        mel.transpose(self.transpose)
        if not self.src_dbi.use:
            input_format = melody_importer.guessInputFormat(tune)
            mp = MetadataProvider(self.meta_data_file, type=input_format)
            if input_format != "esa":
                smd = mp.get_solo_meta_data(tune)
                if smd != None and isinstance(mel, Solo):
                    avgTempoBPM = round(mel.getMeanTempo(bpm=True), 1)
                    smd.soloinfo.setAvgTempoBPM(avgTempoBPM, withTempoClass=True)
                    try:
                        smd.soloinfo.setChorusCount(mel.getChorusCount())
                        smd.soloinfo.chordchanges = mel.metadata.getField("chordchanges")
                    except:
                        pass
                    mel.setMetadata(smd)
                elif isinstance(mel, Song):
                    pmd = mp.get_pop_meta_data(tune, mel.getPopSongInfo())
                    mel.setMetadata(pmd)
                    pass
                else:
                    mel = Solo(melody=mel, metadata=smd)
                #melid = mdb.insertSolo(mel)
        else:
            input_format = melody_importer.tunetypes[melody_importer.melids[idx]]

        if self.loudness_dir !=  "":
            #OUT OF TRY
            #ld = self.get_loudness_data(tune)
            self.get_loudness_and_f0mod_data(tune)
            try:
                ld, f0d, note_ids = self.get_loudness_and_f0mod_data(tune)
            except:
                ld, f0d, note_ids = [], [], []
            if len(ld) > 0:
                #mel.addLoudnessDataByNoteId(ld, note_ids)
                #mel.addLoudnessAndModulationByNoteId(ld, f0d, note_ids)
                try:
                    #mel.addLoudnessDataByNoteId(ld, note_ids)
                    mel.addLoudnessAndModulationByNoteId(ld, f0d, note_ids)
                except Exception as e:
                    print(e)

        if self.walkingbass_dir !=  "" and mel.beattrack != None and isinstance(mel.beattrack, AnnotatedBeatTrack):
            #OUT OF TRY
            #wb = self.get_walkingbass_data(tune)
            try:
                wb = self.get_walkingbass_data(tune)
            except:
                print("WARNING: Could not find walking bass data.")
                wb = []
            #out of try
            #print "Found bass data of len {} for melody with beat track of of len {}".format(len(wb), len(mel.getBeatTrack()))
            try:
                mel.addBassData(wb, quick_fix=False)
            except Exception as e:
                print(e)
        if self.starttimes !=  None:
            try:
                st = self.read_starttimes(tune)
                #print "Found {} for {}".format(st, tune)
            except:
                st = None
            if st != None:
                try:
                    mel.patchStartTime(st)
                except Exception as e:
                    print(e)

        self.bucket.append((mel, input_format))
        if verbose:
            print("Added {} with format '{}' to bucket.".format(os.path.basename(tune), input_format))

    def _create_database_adapter(self, verbose=False):
        if self.db_adapter is not None:
            return
        self.db_adapter  = MelDBAdapterFactory(self.sink_dbi).create(verbose=verbose)
        self.db_adapter.open()

        if self.sink_dbi.rebuild:
            self.db_adapter.createDatabase()
            if verbose:
                print("Successfully created {}".format(self.sink_dbi.path))

    def bulkInsert(self, finalize=False, verbose=False):
        if not self.sink_dbi.use:
            return
        if self.db_adapter is None:
            self._create_database_adapter(verbose=verbose)
        #self.db_adapter.bulkInsert(self.bucket)
        if len(self.bucket):
            try:
                self.db_adapter.bulkInsert(self.bucket)
                print("Inserted {} items".format(len(self.bucket)))
                del self.bucket
                self.bucket = []
            except Exception as e:
                raise RuntimeError("Bulk insert failed! Reason: {}".format(str(e)))

        if finalize:
            self.db_adapter.rebuildIndices()
            self.db_adapter.insertDBInfo(content_type=self.sink_dbi.content_type, version=self.sink_dbi.version, release=self.sink_dbi.release)
            self.db_adapter.close()
            del self.db_adapter
            self.db_adapter = None
            if verbose:
                print("Successfully finalized {}".format(self.sink_dbi.path))

    def process(self, proc_func=None, verbose=False):
        start = time.process_time()
        if verbose == None:
            try:
                verbose = self.params.get("verbose")
            except:
                verbose = False
        if self.outdir != ".":
            ensure_dir(self.outdir)
        try:
            import_hook = proc_func["import"]
        except:
            import_hook = void
        try:
            write_hook = proc_func["melconv"]
        except:
            write_hook= void

        mi = MelodyImporter(self.bundles,
                            self.wdir,
                            self.src_dbi,
                            params=self.melody_importer_params,
                            input_format=self.input_format,
                            proc_hook=import_hook)

        if self.outdir != None:
            outfiles= [substitute_dir(substitute_file_extension(f, self.output_ext, add_if_missing=True), self.outdir) for f in mi.tunes]

        offending_files = []
        mel = None
        fetcher = mi.fetcher(verbose)
        i = -1
        nSucc = 0
        num_items = mi.getNumberItems()
        if verbose:
            print("="*60)

        for mel in fetcher:
            i += 1
            if mel == None:
                offending_files.append((mi.tunes[i], "Invalid melody object"))
                if verbose:
                    print("Error reading  file: Empty melody object")
                continue
            try:
                filename = mi.tunes[i]
                if verbose:
                    print("Reading {}...".format(filename))
            except Exception as e:
                if verbose:
                    print("Error reading file: " + str(e.args[0]))
                #filename = mel.getMetadata().getTranscriptionInfo().filenamesv
                offending_files.append((mi.tunes[i], str(e.args[0])))
                continue

            #OUT OF TRY
            #self.write_lilypond(mel, outfiles[i], verbose)
            #self.write_mcsv2(mel, outfiles[i], self.output_params)
            #self.write_midi(mel, outfiles[i], key=None)
            #self.add_to_bucket(mel, filename, mi, i, verbose)
            #sus = mel.detect_suspicious_chord_changes()
            #if sus > 0 :
            #    ifn = open("chord_diagnostics.txt", "a")
            #    ifn.write("{}: Detected {} suspicious chord changes\n".format(filename, sus))
            #    print "{}: Detected {} suspicious chord changes".format(filename, sus)
            #    ifn.write(str(mel.beattrack.toMeterGrid())+"\n\n")
            #continue
            try:
                if self.output_format[0:5] == "mcsv2":
                    self.write_mcsv2(mel, outfiles[i], self.output_params)
                elif self.output_format[0:4] == "mcsv":
                    self.write_mcsv(mel, outfiles[i], self.output_params)
                elif self.output_format == "meter":
                    self.write_meter(mel, outfiles[i])
                elif self.output_format == "midi":
                    try:
                        key = mel.getMetadata().getField("key")
                    except:
                        key = None
                    if not isinstance(key, Key):
                        try:
                            key = Key.fromString(key)
                        except:
                            key = None
                    self.write_midi(mel, outfiles[i], verbose, key=key)
                elif self.output_format == "notes":
                    self.write_notes(mel, outfiles[i])
                elif self.output_format == "lilypond":
                    self.write_lilypond(mel, outfiles[i], verbose)
                elif self.output_format == "database":
                    self.add_to_bucket(mel, filename, mi, i, verbose)
                    if i > 0 and i % 100 == 0:
                        self.bulkInsert()
                else:
                    msg = "Unknown output format: '{}'".format(self.output_format)
                    if verbose:
                        print(msg)
                    raise RuntimeError(msg)
                if self.output_format != "database":
                    if verbose:
                        print("Successfully written " + outfiles[i])
                nSucc += 1
            except Exception as e:
                if verbose:
                    print("Error writing {} file. Reason: {} ".format(self.output_format, str(e.args[0])))
                offending_files.append((mi.tunes[i], str(e.args[0])))

            if verbose:
                print("="*60)
            if write_hook:
                write_hook(i, num_items, filename, outfiles[i], verbose)

        if self.sink_dbi.use:
            self.bulkInsert(finalize=True, verbose=verbose)

        if verbose:
            nSucc = i + 1
            noun = "file" if nSucc == 1 else "files"
            print("Converted {} {} in {} s".format(nSucc, noun, round(time.process_time()-start, 3)))

        if len(offending_files) > 0:
            if verbose:
                verb = "was" if len(offending_files) == 1 else "were"
                noun = "file" if len(offending_files) == 1 else "files"
                print("There {} {} offending {}".format(verb, len(offending_files), noun))
                print("\n".join([" -  {}".format(of[0]) for of in offending_files]))

        return i, nSucc, time.process_time()-start, offending_files
