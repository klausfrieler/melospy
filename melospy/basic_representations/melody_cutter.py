import re

from melospy.pattern_retrieval.intspan import *

from . import jm_util as util
from .solo import *


class MelodyCutter(object):
    """
        Helper class for cutting a melody or a solo object into
        a list of melody or solo objects according to a list
        of segmentation definitions.
    """

    def __init__(self, melody=None, segmentations=[], verbose=False):
        self.melody = melody
        self.segmentations = segmentations
        self.verbose = verbose
        self.reason = ""

    def cut(self):
        ret = []
        if len(self.segmentations)==0:
            return [(self.melody, "")]
        for segmentation in self.segmentations:
            #print segmentation, type(segmentation)
            #values = self.get_segmentation_values(segmentation)
            try:
                values = self.get_segmentation_values(segmentation)
            except Exception:
                if self.verbose:
                    print("Segmentation '{}' not supported by this melody object. Skipping".format(segmentation))
                continue
            #print "cut:", values
            seg_type = self._get_segmentation_name(segmentation)

            #if self.verbose:
            #    print "Segments: {}\n========================================\n".format(segmentation)
            for aux_id, seg_id in enumerate(values):
                if seg_type == "ideas":
                    #print aux_id, seg_id
                    mel = self._split_melody(seg_type, seg_id[0], seg_id[1])
                    for sub_id in range(len(mel)):
                        label = mel[sub_id][1]
                        m = mel[sub_id][0]
                        seg_name = "{}.{}".format(label.type_string(), seg_id[1])
                        #print "label:{} sub_id:{}, seg_name: {}".format(label, sub_id, seg_name)
                        if m != None:
                            ret.append((m, seg_name))

                else:
                    seg_name = self._get_seg_display_name(segmentation, seg_id, aux_id)
                    if isinstance(segmentation, dict):
                        aux_id = None

                    mel = self._split_melody(seg_type, seg_id, aux_id)
                    if mel != None:
                        ret.append((mel, seg_name))
                #print segmentation, seg_id, aux_id, seg_name, len(mel)
        return ret

    def _get_seg_display_name(self, segmentation, seg_id, aux_id):
        seg_name = ""
        if isinstance(seg_id, list) or isinstance(seg_id, set):
            seg_name = "{}.[{}-{}]".format(self._get_segmentation_name(segmentation), seg_id[0], seg_id[1])
        else:
            if segmentation == "form" and not  isinstance(segmentation, dict):
                chorus_id = self._get_chorus_id_for_form_part(aux_id)
                if chorus_id == -1:
                    chorus_id = "I"
                seg_name = "{}.{}".format(seg_id, chorus_id)
            elif (segmentation == "chords" and not isinstance(segmentation, dict)):
                seg_name = "{}.{}".format( seg_id, aux_id+1)
            else:
                seg_name = "{}.{}".format(self._get_segmentation_name(segmentation), seg_id)
        return seg_name
        #
    def _split_melody(self, seg_type, seg_id, aux_id=None):
        """The actual splitting method"""
        if seg_type== None:
            return None

        slices  = None
        if seg_type == 'phrases':
            slices= self.melody.getPhrase(seg_id)
        elif seg_type == 'bars':
            if isinstance(seg_id, list):
                if len(seg_id)>1:
                    slices = self.melody.getBarSequence(seg_id[0], seg_id[1])
                else:
                    slices = self.melody.getBarSequence(seg_id[0])
            else:
                slices = self.melody.getBarSequence(seg_id)
        elif seg_type == 'chorus':
            slices = self.melody.getChorus(seg_id)
        elif seg_type == 'form':
            chorus_id = self._get_chorus_id_for_form_part(aux_id)
            slices = self.melody.getFormPart(seg_id, chorus_id)
        elif seg_type == 'ideas':
            slices = self.melody.getIdeaSlices(seg_id, aux_id, with_labels=True)
            #print "Got {} slices for id={} and aux_id={}".format(len(slices), seg_id, aux_id)
        elif seg_type == 'chords':
            slices = self.melody.getEventsByChord(seg_id, aux_id)
        elif seg_type == 'chunk':
            #print fid
            slices = self.melody.slice(seg_id[0], seg_id[1])
        else:
            raise ValueError("Unkown segmentation type: {}".format(seg_type))
        return slices

    def _get_chorus_id_for_form_part(self, form_id):

        if form_id == None:
            return None

        form_chorus_ids = self.melody._formPartsChorusIDs()
        if len(form_chorus_ids) == 0:
            return None
        #print "FCI:", form_chorus_ids
        chorus_id = form_chorus_ids[form_id]
        #print "CI:", chorus_id
        return chorus_id

    def parse_directive(self, segmentation):
        """Check for well-formedness of segmentation directive"""

        seg_types = ['phrases', 'bars', 'chorus', 'form', 'chunk', 'chords', 'ideas']

        parameters = []
        segmentation = util.string_to_dict(segmentation, as_list=False)

        if isinstance(segmentation, dict):
            if len(list(segmentation.keys()))>1:
                raise ValueError("Too many elements in dictionary")

            seg_type = list(segmentation.keys())[0].lower()
            parameters = [util.chomp(v) for v in str(segmentation[seg_type]).split(" ") if not v == ""]
            #print seg_type, values
        else:
            seg_type = segmentation.lower()

        if seg_type not in seg_types:
            raise ValueError("Unknown segmentation: {}".format(seg_type))

        if seg_type != "chunk" and len(parameters) == 0:
            return seg_type, parameters

        if seg_type == "chunk" and len(parameters) < 1:
            raise ValueError("Chunk segmentation needs at least one value")

        bars_flag = False
        if seg_type=="bars" and parameters[0].lower() == "chunks":
            bars_flag = True
            parameters = parameters[1:]

        if seg_type == "phrases":
            try:
                for _ in parameters:
                    IS = IntSpan(chomp(_))
            #if not util.is_list_of_int(parameters):
            except:
                raise ValueError("Expected list of integers. Got: {}".format(parameters))
        elif seg_type == "chorus":
            if not util.is_list_of_int(parameters):
                raise ValueError("Expected list of integers. Got: {}".format(parameters))
        elif seg_type == "bars":
            bn = self.parse_barnumbers(parameters, max_len = None, list_mode=False)
            if len(bn) == 0:
                raise ValueError("Empty bar number specification: {}".format(parameters))

            parameters = [str(k) for k in bn]
            if not util.is_list_of_int(parameters):
                raise ValueError("Expected list of integers. Got: {}".format(parameters))
            if bars_flag:
                tmp = ["chunks"]
                tmp.extend(parameters)
                parameters = tmp
        elif seg_type == "chunk":
            if len(parameters) != 2:
                raise ValueError("Too less parameters for chunk. Need window and hop size")
            if not util.is_list_of_int(parameters):
                raise ValueError("Expected list of integers. Got: {}".format(parameters))
        elif seg_type == "chords":
            if parameters == ["set"]:
                pass
            else:
                try:
                    dummy = [Chord(v) for v in parameters]
                except:
                    raise ValueError("Found invalid chord symbol: {}".format(parameters))
        elif seg_type == "form":
            try:
                dummy = [FormName(v) for v in parameters]
            except:
                raise ValueError("Found invalid form name: {}".format(parameters))
        elif seg_type == "ideas":
            #print "parse_directive", parameters
            pass

        return seg_type, parameters


    def parse_barnumbers(self, barnumbers, max_len=None, list_mode=True):
        """
        Retrieves a list of numbers from a string of the form
        <n1>-<m1> <n2>-<m2> ...
        Hyphen separated pairs <n>-<m> are ranges of numbers including borders
        """
        ret = []
        if not barnumbers:
            return ret
        if barnumbers[0] == "chunks" and len(barnumbers)>1:
            if max_len == None:
                raise ValueError("Expected max_len parameter")
            chunk_size = int(barnumbers[1])
            hop_size = chunk_size
            if len(barnumbers)>2:
                hop_size = int(barnumbers[2])
            ret= [[i*hop_size, i*hop_size+chunk_size-1] for i in range(max_len/hop_size)]
            return ret
        for bn in barnumbers:
            try:
                tmp = bn.split("-")
                if list_mode:
                    ret.append([int(tmp[0]), int(tmp[1])])
                else:
                    ret.extend(list(range(int(tmp[0]), int(tmp[1])+1)))
            except:
                if list_mode:
                    ret.append([int(bn)])
                else:
                    ret.append(int(bn))
        #print ret
        return ret

    def get_segmentation_values(self, segmentation_type):
        """ Prepare a list of values for iteration in split function
            for solo events.
            If no parameter is given in 'segmentation_type', all possible
            values will used, otherwise a set depending on the parameters
            is retrieved.
        """
        #seg_type, values = self.parse_directive(segmentation_type)
        try:
            seg_type, values = self.parse_directive(segmentation_type)
        except Exception as e:
            raise e
        #print "get_segmentation_values:", seg_type, values
        all_values = None
        has_parameter = len(values)>0
        #print seg_type, segmentation_type
        if seg_type == 'phrases':
            ps = self.melody.getPhraseSections()
            if ps == None:
                raise RuntimeError("Found invalid value in phrase section")
            all_values = ps.getValues()
            all_values = IntSpan(all_values)
            if has_parameter:
                for _ in values:
                    vals = all_values.intersection(IntSpan(chomp(_)))
                #values = util.intersection(values, all_values)
                #values = [int(v) for v in values]
                values = list(vals)
            else:
                all_values = list(all_values)
        elif seg_type == 'bars':
            all_values = self.melody.getBarNumbers()
            if has_parameter:
                values = self.parse_barnumbers(values, max_len=all_values[-1], list_mode=False)
        elif seg_type == 'chorus':
            #negative values indicate dummy chorusses of intros and outros
            all_values = [v for v in self.melody.getChorusSections().getValues() if v > 0]
            if has_parameter:
                values = util.intersection(values, all_values)
                values = [int(v) for v in values]
        elif seg_type == 'form':
            all_values = self.melody.getFormSections().getValues()
            if has_parameter:
                values = util.intersection(values, all_values)
                values = [FormName(v) for v in values]
        elif seg_type == 'ideas':
            #all_values = set([Idea(v).type_string() for v in self.melody.getIFASections().getValues()])
            all_values = {(Idea(v).type_string(), k) for k, v in enumerate(self.melody.getIFASections().getValues())}
            #print len(all_values), all_values
            #if not has_parameter:
        elif seg_type == 'chords':
            all_values = self.melody.getChordSections().getValues()
            #print " ".join([str(v) for v in all_values]), values
            if has_parameter:
                if values[0] == "set":
                    values = util.intersection(all_values, all_values)
                    #print values
                else:
                    values = [Chord(v) for v in values]
                    values = util.intersection(values, all_values)
                    values = [Chord(v) for v in values]
                    #print str(values)
        elif seg_type == 'chunk':
            chunk_size  = int(values[0])
            if len(values)>1:
                hop_size = int(values[1])
                if hop_size>chunk_size:
                    raise ValueError("Overlap {} must be less or smaller than chunk size {}".format(overlap, chunk_size))
            else:
                hop_size = chunk_size
            if has_parameter and chunk_size>0:
                values = [[i*hop_size, i*hop_size+chunk_size-1] for i in range(len(self.melody)/hop_size)]
                if values[-1][1]>(len(self.melody)-1):
                    values[-1][1]= len(self.melody)-1
                    #print   len(solo)
        else:
            raise ValueError("Unkown segmentation type: {}".format(segmentation_type))

        if not has_parameter:
            values = all_values

        return values

    def _get_segmentation_name(self, segmentation_type):
        """ A segmentation type can be either a single string or
            a dict with parameter values.
            Returns the name of the segmentation.
        """
        if isinstance(segmentation_type, dict):
            seg_type = list(segmentation_type.keys())[0]
        else:
            seg_type = segmentation_type
        return seg_type
