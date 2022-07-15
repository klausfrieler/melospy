import os
import subprocess
import sys
import unicodedata

from pydub import AudioSegment

from melospy.input_output.pattern_search_helper import increment_generated_files_counter


class AudioSlicer(object):
    """ The audio slicer cuts out parts from audio solo files based on the results of
    a pattern search. Files can be saved in different formats like mp3, ogg, etc. External
    dependencies are either ffmpeg (https://www.ffmpeg.org) or libav (https://www.libav.org).
    """

    def __init__(self, args):
        self.concatenate = True if args.get('concatenate') == 'True' else False
        self.data = args.get('data')
        self.destination_dir = args.get('destination_dir')
        self.export_format = args.get('export_format')
        self.pattern = args.get('pattern')
        self.silence_duration = int(args.get('silence_duration')) if args.get(
            'silence_duration') else 1000
        self.source_dir = args.get('source_dir')
        self.transformation = args.get('transformation')
        self.search = args.get('search')
        self.db_session = args.get('db_session')
        self.app_name = args.get('app_name')

    def slice_files(self):
        audio_segments = []
        concatenate = self.concatenate
        export_filenames = []
        self.verify_source_dir()
        self.ensure_destination_dir()

        print("Generating audio files for pattern instances of {} {}".format(self.transformation, self.pattern))

        for result_index, row in enumerate(self.data):
            # TODO use hash
            filename = row[0]
            start = row[1]
            ngram_size = row[2]
            onset = row[3]
            duration = row[4]
            pattern = self.pattern
            file_base_name = rename_file_base_name(filename)
            wav_filepath = self.source_dir + '/' + file_base_name + '.wav'

            if not os.path.isfile(wav_filepath):
                print("WARNING: Could not find {}".format(wav_filepath))
                continue

            if concatenate:
                audio_segment = slice_file(wav_filepath, onset, duration)
                silence = AudioSegment.silent(
                    duration=self.silence_duration)
                audio_segments.append(audio_segment + silence)
            else:
                base_name_parts = [self.transformation, pattern_value(
                    pattern, self.transformation), file_base_name.replace('_Solo', ''), str(start), str(ngram_size)]
                export_filepath = self.build_export_filepath(
                    '_'.join(base_name_parts))
                export_filenames.append(os.path.basename(export_filepath))

                if self.should_export_file(export_filepath):
                    self.export_file(wav_filepath, export_filepath, onset, duration)

            increment_generated_files_counter(self.search, self.db_session, self.app_name)

        if concatenate:
            self.export_concatenated_audio_file(audio_segments)
        else:
            self.write_m3u_file(export_filenames)

        print(" Done.")

    def build_export_filepath(self, file_base_name):
        return self.destination_dir + '/' + file_base_name + '.' + self.export_format

    def ensure_destination_dir(self):
        if not os.path.exists(self.destination_dir):
            os.makedirs(self.destination_dir)

    def export_file(self, wav_filepath, export_filepath, onset, duration):
        try:
            print(("Processing '{}'.").format(export_filepath))
            export_filepath = unicodedata.normalize('NFKD', export_filepath).encode('ascii', 'ignore')
            subprocess.check_output(['ffmpeg', '-y', '-loglevel', 'warning', '-i', wav_filepath, '-codec:a', 'libmp3lame', '-qscale:a', '2', '-ss', str(onset), '-t', str(duration), export_filepath])
        except IOError as io_error:
            error_string = "ERROR: Could not export '{}'. Exception was: {}"
            print(error_string.format(export_filepath, io_error))
        except OSError as os_error:
            error_string = "ERROR: Could not export '{}'. Exception was: {}. Please check FFmpeg is installed and in your PATH!"
            print(error_string.format(export_filepath, os_error))

    def export_concatenated_audio_file(self, audio_segments):
        concatenated_audio_segments = sum(audio_segments)
        export_filepath = self.build_export_filepath("pattern_" + str(self.pattern))
        self.export_file(concatenated_audio_segments, export_filepath)

    def should_export_file(self, export_filepath):
        return not os.path.isfile(export_filepath)

    def verify_source_dir(self):
        if not os.path.exists(self.source_dir):
            print("Error in AudioSlicer: Source dir '{}' does not exist!".format(self.source_dir))

    def write_m3u_file(self, filenames):
        m3u_file = open(self.destination_dir + '/playlist.m3u', 'w')
        for filename in filenames:
            m3u_file.write(filename + '\n')


def pattern_value(pattern, transformation):
    pattern = str(pattern).replace(' ', '')
    if transformation in ['cdpc', 'cdpcx', 'tdpc']:
        pattern = '[' + pattern + ']'
    return pattern


def read_file(filepath):
    audio_segment = None

    try:
        audio_segment = AudioSegment.from_wav(filepath)
    except IOError as io_error:
        print("ERROR: Could not read file '{}'. Exception was: {}".format(filepath, io_error))

    return audio_segment


def slice_file(wav_filepath, onset, duration):
    audio_segment = read_file(wav_filepath)
    start_time = seconds_to_milliseconds(onset)
    end_time = seconds_to_milliseconds(onset) + seconds_to_milliseconds(duration)

    return audio_segment[start_time:end_time]


def rename_file_base_name(filename):
    return (
        remove_filename_extension(filename)
        .replace('FINAL', 'Solo')
        .replace('=', '-')
        .replace(' ', '')
    )


def remove_filename_extension(filename):
    return os.path.splitext(filename)[0]


def seconds_to_milliseconds(time):
    return int(float(time) * 1000)
