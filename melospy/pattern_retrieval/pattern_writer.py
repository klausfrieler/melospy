import os
import random
import subprocess

from melospy.input_output.audio_slicer import AudioSlicer
from melospy.input_output.lilypond_writer2 import *
from melospy.input_output.midi_writer import *
from melospy.input_output.pattern_search_helper import (increment_generated_files_counter,
                                                        set_generation_completed)
from melospy.pattern_retrieval.ngram_data_provider import *
from melospy.pattern_retrieval.ngram_database import *
from melospy.pattern_retrieval.pattern_mining import *


class PatternWriter(object):

    def __init__(self, outfilename, outdir, mel_rep=None, db_session=None, app_name=None, sep=";", convention="en", audio_slicer=None, crop_images=False, verbose = False, proc_hook=None):
        self.audio_slicer = audio_slicer
        self.base_file = outfilename
        self.crop_images = crop_images
        self.melrep = mel_rep
        self.db_session = db_session
        self.app_name = app_name
        self.sep = sep
        self.outdir = outdir
        self.midi_gap = 2
        self.dummy_label_count = {"search": {"list":1, "audio":1, "midi":1, "stats":1, "lilypond":1, "png":1, "pdf":1},
                                    "db": {"list":1, "midi":1, "stats":1}}
        self.prec = 7
        if convention.lower()[0:3]  in ['ger', 'de', 'deu', 'con', 'fre']:
            self.convention = 'de'
        else:
            self.convention = 'en'
        self.outfile_cache = []
        self.verbose = verbose
        if proc_hook == None:
            self.proc_hook = jm_util.void
        else:
           self.proc_hook  = proc_hook

    def _make_outfilename(self, pattern_request, display):
        if pattern_request.type == "partition":
            ofn = self._make_outfilename_partition(pattern_request, display)
        elif pattern_request.type == "database":
            ofn = self._make_outfilename_database(pattern_request, display)
        elif pattern_request.type == "search":
            ofn = self._make_outfilename_search(pattern_request, display)
        else:
            raise ValueError("Invalid pattern request of type {}".format(pattern_request.type))
        return ofn

    def _make_outfilename_search(self, pattern_search, display):
        if display not in ["list", "audio", "midi", "stats", "lilypond", "png", "pdf"]:
            raise ValueError("Unknown display type: {}".format(pattern_search.display))

        label = pattern_search.label
        if label == "":
            label = "{}_{}".format(os.path.splitext(self.base_file)[0], str(self.dummy_label_count["search"][display]))
            label = label.replace("_1", "")
            self.dummy_label_count["search"][display] += 1

        #allow dots in label with quick hack
        label = label.replace(".", "_####_")
        outfile = prepend_path(self.outdir, label)

        pre = os.path.splitext(outfile)[0]
        ext = os.path.splitext(outfile)[1]
        if len(ext) == 0:
            ext = ".csv"

        name = [pre]

        if display == "midi":
            ext = ".mid"
        elif display == "stats":
            name.append("stats")

        outfile = "_".join(name)+ext
        outfile = outfile.replace("_####_", ".")
        return outfile

    def _make_outfilename_database(self, pattern_db, display):
        if display not in ["list", "stats"]:
            raise ValueError("Unknown display type: {}".format(pattern_search.display))

        pp = pattern_db

        if pp.label:
            label = pp.label
        else:
            label = os.path.splitext(self.base_file)[0]
        name = [label, pp.transform, pp.minN, pp.maxN, pp.minOccur, pp.minSource]
        ext = os.path.splitext(self.base_file)[1]
        if len(ext) == 0:
            ext = ".csv"

        if display == "stats":
            name.append("stats")
        name.append("db")
        outfile = "_".join([str(v) for v in name])
        outfile = prepend_path(self.outdir, outfile) + ext
        return outfile

    def _make_outfilename_partition(self,  pattern_partition, display):
        if display not in ["list", "stats"]:
            raise ValueError("Unknown display type: {}".format(pattern_search.display))

        pp = pattern_partition
        ext = os.path.splitext(self.base_file)[1]
        if len(ext) == 0:
            ext = ".csv"

        if pattern_partition.label:
            label = pattern_partition.label
        else:
            label = os.path.splitext(self.base_file)[0]
        tmp = [label, pp.transform, pp.minN, pp.minOccur, pp.minSource]
        if pp.filter_scales == True:
            tmp.append("sf")
        if pp.filter_trills == True:
            tmp.append("tf")
        if pp.filter_arpeggios == True:
            tmp.append("af")
        if display == "stats":
           tmp.append(display)
        if bool(pp.simul):
            tmp.append("sim")
            if simul > 0:
                tmp.append(str(pp.simul))
        outfile = "_".join([str(v) for v in tmp])
        outfile = prepend_path(self.outdir, outfile) + ext
        return outfile


    def _get_header(self, prtype, display):
        if prtype == "partition":
            return self._get_header_partition(display)
        elif prtype == "database":
            return self._get_header_db(display)
        return self._get_header_search(display)

    def _get_header_partition(self, display):
        if display == "stats":
            header = ["id", "note_count", "min_N", "max_N", "min_occur", "min_source", "pattern_count", "coverage", "avg_N", "avg_overlap", "over_coverage", "log_excess_prob"]
        else:
            header = ["id", "start", "N", "onset", "dur", "metricalposition",  "value", "freq", "prob100", "tag"]

        return header

    def _get_header_db(self, display):
        if display == "stats":
            header = ["value", "N", "freq", "prob100", "noSources"]
        else:
            header = ["id", "start", "N", "onset", "dur", "metricalposition", "value", "freq", "prob100"]

        return header

    def _get_header_search(self, display):

        if display == "stats":
            header = ["value", "N", "freq", "prob100", "noSources"]
        else:
            header = ["id", "start", "N", "onset", "dur", "metricalposition", "value", "freq", "prob100"]

        return header

    def set_melody_rep(self, melrep):
        self.melrep = melrep

    def _make_partition_entry(self, transform, display, ngram_part):
        if display == "stats":
            return self._make_partition_entry_stats(ngram_part)
        return self._make_entry_list(transform, ngram_part, mode="partition")

    def _make_partition_entry_stats(self, ngram_part):
        ret = [ngram_part.getStats()]
        return ret

    def _format_row(self, row, NA_str="N/A"):
        for i in range(len(row)):
            if row[i] == None:
                row[i] = NA_str
            if isinstance(row[i], float):
                #print "Before ", row[i]
                row[i] = round(row[i], self.prec)
                #print "after ", row[i]
                if self.convention.lower() == "de":
                    row[i] = str(row[i]).replace(".", ",")
        return row

    def _make_ngram_entry(self, transform, display, ngram):
        if display.lower() == "stats":
            return self._make_ngram_entry_stats(ngram)
        #return self._make_ngram_entry_list(transform, ngram)
        return self._make_entry_list(transform, ngram, mode="ngram")

    def _make_ngram_entry_stats(self, ngram):
        ret =  [ngram.getStats()]
        return ret

    def _make_entry_list(self, transform, ngram_container, mode, prec=3):
        ret = []
        indexOffset, lengthOffset = NGramDataProvider.get_transform_offsets(transform)
        if mode == "partition":
            npos_list = ngram_container.getList()
        else:
            npos_list = ngram_container

        for n in npos_list:
            melody = self.melrep[n.seqid] if self.melrep else None
            name = ngram_container.getSeqRep().getNameFromId(n.seqid)

            if melody:
                mp = melody[n.startid + indexOffset].getMetricalPosition()
            else:
                mp = None

            real_start = n.startid + indexOffset
            real_end = n.endid + lengthOffset + indexOffset

            try:
                start_onset, dur = melody.getRegionFromIDs(real_start, real_end)
            except:
                start_onset, dur = None, None

            freq = n.freq
            prob = n.prob * 100
            if mode == "partition":
                value = n.getValue(ngram_container.getSeqRep())
                tag = n.tag
            else:
                value = ngram_container.getValue()
                tag = None
            row = [name, real_start, n.N, start_onset, dur, mp, value, freq, prob]
            if tag:
                row.append(tag)

            ret.append(row)
        return ret

    def _make_notetrack(self, ngram, transform, gap=2):
        if self.melrep == None:
            raise RuntimeError("Need melody repository for MIDI export")
        nt = NoteTrack()
        onset_offset = 0
        indexOffset, lengthOffset = NGramDataProvider.get_transform_offsets(transform)
        #print transform, indexOffset, lengthOffset
        for n in ngram:
            #print "_make_notetrack", n.seqid
            melody = self.melrep[n.seqid]
            real_start = n.startid + indexOffset
            real_end = n.endid + lengthOffset + indexOffset

            start       = melody[real_start].getOnset()
            end         = melody[real_end].getOffset()
            total_dur   = end - start + gap
            for i in range(n.startid, n.endid + lengthOffset + 1):
                pitch = melody[i].getPitch()
                onset = melody[i].getOnset() - start + onset_offset
                duration = melody[i].getDuration()
                ne =  NoteEvent(pitch, onset, duration)
                nt.append(ne)
                #print "Added ({}, {}, {})".format(onset, pitch, duration)
            onset_offset = onset_offset + total_dur
            #print "New offset:", onset_offset
        #print "Len Notetrack: ", len(nt)
        return nt

    def _patch_title(self, title, aux_data):
        mp = aux_data[5]
        start = aux_data[1]
        onset = round(aux_data[3], 3)
        patched_title = "{} [{}, {}, {}]".format(title, mp, start, onset)
        return patched_title

    def get_surrounding_phrase_ids(self, solo, startID, endID):
        new_start, new_end = startID, endID
        num_phrases = 0
        try:
            phrases = solo.getPhraseSections()
            sections = phrases.get_sections_by_ids(startID, endID)
            num_phrases = len(sections)
            #print "Pattern {}-{} is spanning {} phrases".format(startID, endID, num_phrases)
            if num_phrases == 1:
                sect = sections[0]
                new_start, new_end = sect.startID, sect.endID
            elif num_phrases > 1:
                new_start, new_end = sections[0].startID, sections[-1].endID
        except:
            print("Could not find phrase section for {}, {}".format(startID, endID))
            new_start, new_end = None, None
        return new_start, new_end, num_phrases

    def _parse_output_context(self, output_context, song, startID, endID):
        prefix = 0
        suffix = 0
        elements = output_context.split(",")
        try:
            prefix = int(chomp(elements[0]))
            if len(elements) > 1:
                suffix = int(chomp(elements[1]))
        except:
            return startID, endID
        start = max(startID - prefix, 0)
        end   = min(endID + suffix, len(song)-1)
        #print "OC: {}, {},{}->{},{}".format(output_context, startID, endID, start, end)
        return start, end

    def _melody_cuts(self, ngram, transform, pattern, output_context = "phrase-fit"):
        if self.melrep == None:
            raise RuntimeError("Need melody repository for Lilypond export")

        indexOffset, lengthOffset = NGramDataProvider.get_transform_offsets(transform)
        dummy = self._make_entry_list(transform, ngram, mode="search", prec=3)
        songs = []

        for i, n in enumerate(ngram):
            unique_pattern = ','.join(map(str, ngram.getValue()))
            if transform in ['cdpc', 'cdpcx', 'tdpc']:
                unique_pattern = unique_pattern.replace(',', '')
            real_start = n.startid + indexOffset
            real_end = n.endid + lengthOffset + indexOffset

            song = self.melrep[n.seqid].clone()
            title = song.getMetadata().getField("title")
            patched_title = self._patch_title(title, dummy[i])
            song.getMetadata().setField("title", patched_title)

            base_filename = "{}_{}_{}_{}_{}".format(transform, '[' + unique_pattern + ']', song.getMetadata().identifier(), real_start, n.N)
            song.getMetadata().setField("basefilename", base_filename)

            if output_context in ["phrase-fit", "phrase-all"]:
                d1, d2, num_phrases= self.get_surrounding_phrase_ids(song, real_start, real_end)
                #print "{}-{} -> {}-{} in {} phrases".format(real_start, real_end, d1, d2, num_phrases)
                if output_context  == "phrase-fit" and num_phrases > 1:
                    num_phrases = 0
            else:
                d1, d2 = self._parse_output_context(output_context, song, real_start, real_end)
                num_phrases = 1
            if num_phrases:
                song = song.slice(d1, d2)
                first_bar = song[0].getBar()
                song.shiftbar(-first_bar+1)
                songs.append(song)
            else:
                print("Excluded ", song.getMetadata().getField("title"))

        return songs

    def print_pattern_partition(self, partition_result):
        pr = partition_result.pattern_request
        try:
            display = pr.display[0]
        except:
            display = "list"
        header = self._get_header(pr.type, display)

        csvwriter = csv.writer(sys.stdout, delimiter=self.sep, lineterminator="\n", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(header)
        for part in partition_result.result:
            rows = self._make_partition_entry(pr.transform, pr.display, part)
            for row in rows:
                csvwriter.writerow(self._format_row(row))

    def print_search_result(self, search_result):
        pr = search_result.pattern_request
        try:
            display = pr.display[0]
        except:
            display = "list"
        header = self._get_header(pr.type, display)

        csvwriter = csv.writer(sys.stdout, delimiter=self.sep, lineterminator="\n", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(header)
        for ngram in search_result.result:
            rows = self._make_ngram_entry(pr.transform, display, ngram)
            for row in rows:
                csvwriter.writerow(self._format_row(row))

    def print_database(self, database_result):
        pr = database_result.pattern_request
        try:
            display = pr.display[0]
        except:
            display = "list"
        if display == "tree":
            print("Tree mode not implemented yet")
            return
        header = self._get_header(pr.type, display)

        csvwriter = csv.writer(sys.stdout, delimiter=self.sep, lineterminator="\n", quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerow(header)
        for ngram_list in database_result.result:
            print("="*20)
            print("N = {}".format(ngram_list.getN()))
            for ngram in ngram_list:
                rows = self._make_ngram_entry(pr.transform, display, ngram)
                for row in rows:
                    csvwriter.writerow(self._format_row(row))

    def write_pattern_partition(self, partition_result):
        pr = partition_result.pattern_request
        for d in pr.display:
            outfile = self._write_csv_header(pr, d)
            with open(outfile, 'a') as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=self.sep, lineterminator="\n", quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for i, part in enumerate(partition_result.result):
                    self.proc_hook(i, len(partition_result.result))
                    try:
                        rows = self._make_partition_entry(pr.transform, d, part)
                        for row in rows:
                            csvwriter.writerow(self._format_row(row))
                    except:
                        print("Skipped results for entry", i)
            self.outfile_cache.append(outfile)
            if self.verbose:
                print("Successfully written partitions to: \n    {}".format(outfile))

    def write_search_result_audio(self, search_result, display):
        start_time = time.time()
        pattern_request = search_result.pattern_request
        outfile = self._make_outfilename(pattern_request, "audio").replace("\\", "/")
        total_result_count = search_result.result.positionCount()
        result_count = 0

        for result_index, ngram in enumerate(search_result.result):
            self.audio_slicer['data'] = self._make_ngram_entry(pattern_request.transform, display, ngram)
            self.audio_slicer['pattern'] = ngram.value
            self.audio_slicer['transformation'] = pattern_request.transform
            self.audio_slicer['search'] = pattern_request.search
            self.audio_slicer['db_session'] = self.db_session
            self.audio_slicer['app_name'] = self.app_name

            AudioSlicer(self.audio_slicer).slice_files()
            self.outfile_cache.append(outfile)

        set_generation_completed('audio', pattern_request.search, self.db_session, self.app_name)
        print("Audio generation completed in {} seconds.\n".format(time.time() - start_time))

    def write_search_result_midi(self, search_result):
        pr = search_result.pattern_request
        outfile = self._make_outfilename(pr, "midi").replace("\\", "/")
        if outfile not in self.outfile_cache:
            notetrack = NoteTrack()
            num_pos = 0
            for ngram in search_result.result:
                nt = self._make_notetrack(ngram, transform=pr.transform, gap=self.midi_gap)
                notetrack.concat(nt, gap=self.midi_gap)
                num_pos += len(ngram)
            midi_writer = MIDIWriter()
            midi_writer.writeMIDIFile(notetrack, outfile)
            self.outfile_cache.append(outfile)

        if self.verbose:
            print("Successfully written {} with {} elements from {} ngrams with {} positions".format(outfile, len(notetrack), len(search_result.result), num_pos))

    def write_search_result_lily(self, search_result, display="lilypond"):
        start_time = time.time()
        pattern_request = search_result.pattern_request
        pattern = pattern_request.pattern.replace(" ", "")
        output_context = search_result.output_context
        lily_writer = LilypondWriter2()
        total = 0

        print("Starting lilypond conversion...")

        for ngram_id, ngram in enumerate(search_result.result):
            cuts = self._melody_cuts(ngram,
                                     transform=pattern_request.transform,
                                     pattern=pattern,
                                     output_context=output_context)
            total += len(cuts)

            for cut_id, song in enumerate(cuts):
                base_filename = prepend_path(self.outdir, song.getMetadata().getField('basefilename'))

                if base_filename not in self.outfile_cache:
                    lilypond_filename = base_filename + '.ly'
                    with_title_section = not self.crop_images
                    try:
                        lily_writer.write(lilypond_filename, song, with_title_section=with_title_section)
                    except RuntimeError as error:
                        print("Error writing lilypond file: {}".format(error))

                    if display in ["png", "pdf"]:
                        try:
                            base_filepath = os.path.splitext(lilypond_filename)[0]

                            if self.crop_images:
                                if self.should_crop_image(base_filepath + "_cropped." + display, output_context):
                                    if output_context == 'phrase-all':
                                        base_filepath += "_" + output_context
                                    self.convert_from_lilypond(display, base_filepath, lilypond_filename)
                                    filepath = base_filepath + "." + display
                                    self.trim_image(filepath)

                                    if os.path.isfile(filepath):
                                        os.remove(filepath)
                                if os.path.isfile(lilypond_filename):
                                    os.remove(lilypond_filename)
                            else:
                                self.convert_from_lilypond(display, base_filepath, lilypond_filename)
                        except:
                            pass
                    if base_filename not in self.outfile_cache:
                        self.outfile_cache.append(base_filename)

                increment_generated_files_counter(pattern_request.search, self.db_session, self.app_name)

        if self.verbose:
            print("Successfully written {} lilypond files from {} ngrams. base name:{}".format(total, len(search_result.result), base_filename))
        if output_context == 'phrase-all':
            set_generation_completed('score', pattern_request.search, self.db_session, self.app_name)
        print("Score generation completed in {} seconds.".format(time.time() - start_time))

    def convert_from_lilypond(self, display, base_filepath, lilypond_filename):
        subprocess.check_output(['lilypond', '-l', 'BASIC_PROGRESS', '-f', display, '-o', base_filepath, lilypond_filename])

    def should_crop_image(self, filepath, output_context):
        if output_context == 'phrase-all':
            return not os.path.isfile(filepath.replace('cropped.png', 'phrase-all_cropped.png'))
        else:
            return not os.path.isfile(filepath)

    def trim_image(self, filepath):
        trimmed_filepath = filepath.replace(".png", "_cropped.png")
        os.system("convert \"{}\" +profile \"icc\" -gravity north -crop 100x60% -trim +repage \"{}\"".format(filepath, trimmed_filepath))

    def _write_csv_header(self, pattern_request, display):
        outfile = self._make_outfilename(pattern_request, display).replace("\\", "/")
        header = self._get_header(pattern_request.type, display)
        if outfile not in self.outfile_cache:
            with open(outfile, "w") as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=self.sep, lineterminator="\n", quotechar='"', quoting=csv.QUOTE_MINIMAL)
                csvwriter.writerow(header)
            #self.outfile_cache.append(outfile)
            #prin3t "added {} to outfile cache".format(outfile)
        return outfile

    def write_search_result_list(self, search_result, display):
        pr = search_result.pattern_request
        outfile = self._write_csv_header(pr, display)
        if outfile not in self.outfile_cache:
            with open(outfile, 'a') as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=self.sep, lineterminator="\n", quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for ngram in search_result.result:
                    rows = self._make_ngram_entry(pr.transform, display, ngram)
                    for row in rows:
                        csvwriter.writerow(self._format_row(row))
                self.outfile_cache.append(outfile)
        if self.verbose:
            print("Successfully written search results to: \n   {}".format(outfile))

    def write_search_result(self, search_result):
        for display in search_result.pattern_request.display:
            display = display.lower()
            if display == "audio":
                self.write_search_result_audio(search_result, display)
            elif display == "midi":
                self.write_search_result_midi(search_result)
            elif display in ["lilypond", "pdf", "png"]:
                self.write_search_result_lily(search_result, display)
            else:
                self.write_search_result_list(search_result, display)

    def write_database(self, database_result):
        pr = database_result.pattern_request
        for d in pr.display:
            if d == "tree":
                print("Tree mode not implemented yet")
                return
            minN = pr.minN
            minOccur = pr.minOccur
            minSource = pr.minSource
            outfile = self._write_csv_header(pr, d)
            # print "Added {} to outfile cache".format(outfile)

            with open(outfile, 'a') as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=self.sep, lineterminator="\n", quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for i, ngram_list in enumerate(database_result.result):
                    self.proc_hook(i, database_result.result.maxN)
                    for ngram in ngram_list:
                        if ngram.N < minN or ngram.getFreq() < minOccur or ngram.sourceCount() < minSource:
                            continue
                        rows = self._make_ngram_entry(pr.transform, d, ngram)
                        for row in rows:
                            csvwriter.writerow(self._format_row(row))
            self.outfile_cache.append(outfile)
            if self.verbose:
                print("Successfully written N-gram database to {}".format(outfile))
