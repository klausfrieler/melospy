""" Class implementation of Segmenter"""

#from melospy.basic_representations.jm_util import diff, break_ties_causal
from melospy.basic_representations.jm_stats import mean, median, sd, var
from melospy.basic_representations.rhythm import *
from melospy.basic_representations.segmenter_param import *


class Segmenter(object):

    def __init__(self, rhythm=None, params=None):

        self.rhythm = rhythm
        self.setParams(params)

    def setParams(self, params):

        if params is None:
            #use cool defaults, baby
            self.__params = SegmenterParams()
        elif isinstance(params, SegmenterParams):
            self.__params = params
        else:
            raise TypeError("Expected 'SegmenterParams' object or 'None'. Got:{}.".format(type(params)))
        return self

    def _simple_segment(self, rhythm):
        gap_seconds = self.__params["gap_seconds"]
        running_id = 1
        ev = rhythm[0].clone()
        ev.value = running_id
        markers = Rhythm(ev)
        iois = rhythm.getIOIs()
        #print iois
        for i, ioi in enumerate(iois):
            if ioi >= gap_seconds:
                running_id += 1
                ev = rhythm[i].clone()
                ev.value = running_id
                markers.append(ev)
        return markers

    def _relative_simple_segment(self, rhythm):
        gap_factor = self.__params["gap_factor"]
        running_id = 1
        ev = rhythm[0].clone()
        ev.value = running_id
        markers = Rhythm(ev)
        iois = rhythm.getIOIs()
        med_ioi = median(iois)
        gap = gap_factor* med_ioi
        #print "gap_factor: {} median IOI: {}, gap: {}".format(gap_factor, med_ioi, gap)
        for i, ioi in enumerate(iois):
            if i > 0 and ioi >= gap:
                running_id += 1
                ev = rhythm[i].clone()
                ev.value = running_id
                markers.append(ev)
        #print markers
        return markers

    def process(self, rhythm=None):
        if rhythm is None:
            rhythm = self.rhythm
        if rhythm is None or len(rhythm) == 0:
            raise ValueError("No rhythm given")
        if self.__params["method"] == "simple_segmenter":
            markers = self._simple_segment(rhythm)
        elif self.__params["method"] == "relative_simple_segmenter":
            markers = self._relative_simple_segment(rhythm)
        else:
            raise ValueError("Unkonw segmentation method: {}".format(self.__params["method"]))
        markers = self.post_process(markers, rhythm)
        return markers

    def post_process(self, markers, rhythm):
        if len(markers) == 0:
            return markers
        if self.__params["output_format"] == "rhythm":
            return markers
        if self.__params["output_format"] == "section_list":
            return rhythm.rhythmToSectionList(markers, sectType = "PHRASE")

    def getParams(self):
        return self.__params

    params    = property(getParams, setParams)
