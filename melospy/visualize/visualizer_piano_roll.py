
import math
import random

#import applications.melvis_tools as mtools
import matplotlib.pyplot as pl
import numpy as np
from matplotlib.collections import LineCollection, PatchCollection
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle, Wedge

import melospy.visualize.visualizer_tools as vtools


class VisualizerPianoRoll(object):
    '''
    Main class for bar plot visualization
    '''

    def get_default_param_values(self):
        """ Returns default parameter values
        Returns:
            Dict with default parameter values
        """
        dv = dict()
        dv["onsetFeatureName"] = "onset"
        dv["durationFeatureName"] = "duration"
        dv["pitchFeatureName"] = "pitch"
        dv["patternBorderFeatureName"] = ""
        dv["noteGroupingFeatureName"] = None
        dv["noteGroupingLabel"] = None
        dv["noteGroupingSelect"] = None
        dv["showGroupIndex"] = False
        dv["showPatterns"] = False
        dv["showGroupBackground"] = False
        dv["showConnectLines"] = False
        dv["showSelfSimilarity"] = False
        dv["similarityThreshold"] = .3
        dv["selfSimFeatureName"] = ""
        dv["noteConnectorLineWidth"] = .5
        dv["title"] = "Piano Roll"
        dv["fontSize"] = 8
        dv["barWidth"] = 2
        dv["groupColoring"] = False
        dv["layout"] = "Linear"
        dv["backgroundColor"] = [[.9, .2, .3], [.6, .5, .5]]
        dv["foregroundColor"] = [[.6, .5, .5], [.9, .2, .3]]
        dv["minPitchRangeToPlot"] = 24
        dv["minPitchMargin"] = 5
        dv["minDurationToPlot"] = 20
        dv["minTimeMargin"] = 1
        return dv

    def process_simple(self, fn_image, onset, duration, pitch):
        """ Simple wrapper for simple input data, quick hack
            TODO: merge this with general function
        """
        fig, ax = pl.subplots()
        pl.cla()
        patches = []
        num_notes = len(onset)
        for k in range(num_notes):
            patches.append(Rectangle((onset[k], pitch[k]-.5), duration[k], 1))
        p = PatchCollection(patches, facecolors=[.6, .5, .5], edgecolors=[.6, .5, .5], antialiased=False)
        ax.add_collection(p)

        y_max = max(pitch)+5
        y_min = min(pitch)-5
        params = {}
        params["dpi"] = 30
        params["fontSize"] = 8
        params["showGrid"] = True
        # params["heightPx"] = params["dpi"]*5
        params["yLabel"] = "MIDI pitch"
        params["xLabel"] = "Time [s]"
        params["yLimMax"] = max(pitch)+5
        params["yLimMin"] = min(pitch)-5

        params["xLimMax"] = max([onset[_]+duration[_] for _ in range(num_notes)])+1
        params["xLimMin"] = min(onset)-1

        # # Pitch axis -> ticks for all C's (multiples of pitch 12) within the pitch range
        # params["yTickMajor"] = np.array(range(int(12*math.floor(float(params["yLimMin"])/12.)),
        #                                       int(12*math.ceil(float(params["yLimMax"])/12.)),
        #                                       12))
        #
        # # Octave note labels ('C1','C2' ...)
        # tick_octaves = params["yTickMajor"]/12 - 1
        # params["yTickLabels"] = ['C' + str(_) for _ in tick_octaves]

        # time axis ticks every 10 s
        params["xTickMajor"] = np.array(list(range(int(10*math.floor(float(params["xLimMin"])/10.)),
                                              int(10*math.ceil(float(params["xLimMax"])/10.)),
                                              10)))

        vtools.set_figure_properties(pl, params)

        fig.tight_layout()
        pl.savefig(fn_image, format=fn_image.split(".")[-1], dpi=params["dpi"], bbox_inches='tight', pad_inches=0)






    def process(self, params, data, proc_func = None):
        """ Main process function for bar plot visualization
        Args:
            params: Dictionary with visualization parameters
            data: Dictionary with dataset (see input_output/melfeature_csv_reader.py for details)
        Returns:
            params: Dictionary with visualization parameters
            data: Dictionary with dataset (see input_output/melfeature_csv_reader.py for details)
        """
        params = vtools.add_missing_params_by_default_values(params, self.get_default_param_values())

        nItems = len(data["itemLabels"])
        layout = params["layout"]

        # create empty figure
        fig, ax = pl.subplots()

        for i in range(nItems):

            if proc_func:
                proc_func(i, nItems, data["itemLabels"][i])

            pl.cla()

            data = self.prepare_data(data, i, params)

            # (3) group backgrounds / wedges
            if params["showGroupBackground"]:
                if layout == "Linear":
                    ax = self.plot_group_linear(ax, data, params)
                else:
                    ax = self.plot_group_circular(ax, data, params)

            # (5) pattern half-circles
            if params["showPatterns"]:
                ax = self.plot_patterns(ax, data, params, i)

            # PLOT NOTES
            if layout == "Linear":
                ax = self.plot_notes_linear(ax, data, params)
            else:
                ax = self.plot_notes_circular(ax, data, params)

            # GROUP INDEX
            if params["showGroupIndex"]:
                ax = self.show_group_index(ax, data, params)

            # PLOT NOTE CONNECTORS
            if params["showConnectLines"]:
                ax = self.plot_note_connectors(ax, data, params)

            # (4) similarity half-circles
            if params["showSelfSimilarity"]:
                ax = self.plot_group_similarity_connector_circular(ax, data, params)

            params["dpi"] = 600

            if params["layout"] == 'Circular':
                ax.set_aspect('equal')
                # PROPERTIES
                params["heightPx"] = 2000

                b = data["outerRadius"] + 5
                params["yLimMax"] = b
                params["yLimMin"] = -b
                params["xLimMax"] = b
                params["xLimMin"] = -b
            else:
                params["aspect"] = .3
                pl.gca().set_aspect(params["aspect"])

                params["showGrid"] = True

                # y-axis (pitch)
                maxPitch = max(data["pitch"])
                minPitch = min(data["pitch"])
                pitchRange = maxPitch - minPitch
                yMargin = max((params["minPitchRangeToPlot"] - pitchRange)/2., params["minPitchMargin"])
                yLimMax = maxPitch+yMargin
                yLimMin = minPitch-yMargin

                params["yLabel"] = "MIDI pitch"
                if params["showPatterns"]:
                    params["yLimMax"] = maxPitch+70
                    params["yLimMin"] = minPitch-5
                else:
                    params["yLimMax"] = yLimMax
                    params["yLimMin"] = yLimMin

                # Pitch axis -> ticks for all C's (multiples of pitch 12) within the pitch range
                params["yTickMajor"] = np.array(list(range(int(12*math.floor(float(params["yLimMin"])/12.)),
                                                      int(12*math.ceil(float(params["yLimMax"])/12.)),
                                                      12)))
                params["yTickMinor"] = np.arange(yLimMin, yLimMax)

                # Octave note labels ('C1','C2' ...)
                tick_octaves = params["yTickMajor"]/12 - 1
                params["yTickLabels"] = ['C' + str(_) for _ in tick_octaves]


                # x-axis (time)
                minTime = data["onset"][0]
                maxTime = data["onset"][-1] + data["duration"][-1]
                duration = maxTime - minTime
                xMargin = max((params["minDurationToPlot"] - duration)/2., params["minTimeMargin"])
                xLimMax = maxTime + xMargin
                xLimMin = minTime - xMargin

                params["xLabel"] = "Time [s]"

                params["xLimMax"] = xLimMax
                params["xLimMin"] = xLimMin

                # time axis ticks every 10 s
                params["xTickMajor"] = np.array(list(range(int(10*math.floor(float(params["xLimMin"])/10.)),
                                                      int(10*math.ceil(float(params["xLimMax"])/10.)),
                                                      10)))

                # adapt plot dimensions to pitch range
                widthInch = 3*duration/(10*2.54) # 3 cm per 10 seconds
                heightInch = pitchRange/(12*2.54) # 1 cm per octave

                # figure rescaling only for larger segments
                if not any([_ in data["itemLabels"][i] for _ in ["bars", "phrases", "chords", ""]]):
                    maxDots = max((params["dpi"]*widthInch, params["dpi"]*heightInch))
                    maxSizeDots = 32768
                    if maxDots > maxSizeDots:
                        scaling = maxSizeDots/maxDots
                        print(("Figure was rescaled by factor {}".format(scaling)))
                        widthInch *= scaling
                        heightInch *= scaling

                    pl.gcf().set_size_inches(widthInch, heightInch)


            params["title"] = vtools.clean_up_item_label(data["itemLabels"][i])
            vtools.set_figure_properties(pl, params)

            # SHOW / EXPORT
            fnBasic = vtools.clean_up_item_label(data["itemLabels"][i])
            if params["noteGroupingFeatureName"] is not None:
                if params["noteGroupingLabel"]:
                    fnBasic += '_'+params["noteGroupingLabel"]
                if params["noteGroupingSelect"] is not None:
                    fnBasic = fnBasic+'_'+str(params["noteGroupingSelect"])
            fnOut = fnBasic.replace(' ', '_')

            fileName = vtools.save_plot(pl, fnOut, params)
            params["outFile"].append(fileName)


        return params, data



    def rotate_and_flip_angle(self, ang):
        """ converts angle to start at 12 o'clock and count in clockwise direction
        Args:
            ang: Angle in degrees
        Returns:
            Converted angle in degrees
        """
        return (450-ang) % 360

    def getXYFromAngleAndRadius(self, ang, r):
        """ Converts angle - radius - pair to x,y coordinates
        Args:
            ang: Angle in degrees
            r: Radius
        Returns
            x: Coordinate
            y: Coordinate
        """
        return r*math.cos(math.pi*ang/180), r*math.sin(math.pi*ang/180)

    def lighten_up_color(self, col):
        """ Lightens up a given RGB color
        Args:
            col (list): color as RGB values
        Returns:
            col (list): lightened up color (RGB)
        """
        return [math.sqrt(c) for c in col]

    def plot_notes_linear(self, ax, data, params):
        """ Plot note events in linear piano-roll as rectangle collection
        Args:
            ax: figure axis
            data: Data dict
            params: Parameter dict
        Returns:
            ax: figure axis
        """
        patches = []
        for k in range(data["nNotes"]):
            patches.append(Rectangle((data["onset"][k], data["pitch"][k]-.5), data["duration"][k], 1))
        p = PatchCollection(patches, facecolors=data["colorNoteEvent"], edgecolors=data["colorNoteEvent"], antialiased=False)
#         p = PatchCollection(patches,facecolors=data["colorNoteEvent"],edgecolors=[0,0,0],antialiased=False)
        ax.add_collection(p)
        return ax

    def plot_notes_circular(self, ax, data, params):
        """ Plot note events in circular piano-roll as wedge collection
        Args:
            ax: figure axis
            data: Data dict
            params: Parameter dict
        Returns:
            ax: figure axis
        """
        patches = []
        for k in range(data["nNotes"]):
            patches.append(Wedge((0, 0), data["innerRadius"]+data["pitchNorm"][k]+1, data["angleStartNote"][k], data["angleEndNote"][k], width=1))
        p = PatchCollection(patches, facecolors=data["colorNoteEvent"], edgecolors=data["colorNoteEvent"])
#         p = PatchCollection(patches,facecolors=data["colorNoteEvent"],edgecolors=[0,0,0])
        ax.add_collection(p)
        return ax

    def plot_note_connectors(self, ax, data, params):
        """ Connect all note events within each phrase with a line to better show the melody contour
        Args:
            ax: figure axis
            data: Data dict
            params: Parameter dict
        Returns:
            ax: figure axis
        """
        # TODO write this shorter with new data variables!
        lines = []
        groupColors = []
        for group_id in list(set(data["noteGroupID"])):
            # notes in current group
            note_id_in_group = [_ for _ in range(data["nNotes"]) if data["noteGroupID"][_] == group_id]
            if len(note_id_in_group) > 1:
                # connect notes in current group with lines
                currLine = []
                for id in note_id_in_group:
                    currLine.append(data["noteCentroidCoordinates"][id])
                lines.append(currLine)
                groupColors.append(data["colorNoteEvent"][note_id_in_group[0]])
            l = LineCollection(lines, linewidths=(params["noteConnectorLineWidth"],), colors=groupColors)
            ax.add_collection(l)
        return ax

    def show_group_index(self, ax, data, params):
        """ Prints group index as number
        Args:
            ax: figure axis
            data: Data dict
            params: Parameter dict
        Returns:
            ax: figure axis
        """
        for k in range(data["num_groups"]):
            ax.text(data["groupIndexX"][k], data["groupIndexY"][k], str(k+1), color=[0, 0, 0], ha='center', va='center', size=params["fontSize"])
        return ax

    def plot_group_circular(self, ax, data, params):
        """ Plot groups in circular piano-roll as wedge collection
        Args:
            ax: figure axis
            data: Data dict
            params: Parameter dict
        Returns:
            ax: figure axis
        """
        patches = []
        for k in range(data["num_groups"]):
            patches.append(Wedge((0, 0), data["innerRadius"]+data["pitchRange"]+2, data["angleStartGroup"][k], data["angleEndGroup"][k], width=data["pitchRange"]+4, alpha=.3))
        p = PatchCollection(patches, facecolors=data["colorGroup"], edgecolors=data["colorGroup"])
        ax.add_collection(p)
        return ax

    def plot_group_linear(self, ax, data, params):
        """ Plot groups in linear piano-roll as rectangles
        Args:
            ax: figure axis
            data: Data dict
            params: Parameter dict
        Returns:
            ax: figure axis
        """
        patches = []
        for k in range(data["num_groups"]):
            patches.append(Rectangle((data["onsetGroup"][k], data["minPitchGroup"][k]-.5), data["offsetGroup"][k]-data["onsetGroup"][k], data["maxPitchGroup"][k]-data["minPitchGroup"][k]+1.5))
        p = PatchCollection(patches, facecolors=data["colorGroup"], edgecolors=data["colorGroup"], antialiased=False)
        ax.add_collection(p)
        return ax


    def plot_group_similarity_connector_circular(self, ax, data, params):
        """ Function connects groups of notes (wedges in the circular pianoroll) with lines. The width and color of the
            lines encode the degree of similarity between the pairs of groups (e.g. phrases)
        Args:
            ax: figure axis
            data: Data dict
            params: Parameter dict
        Returns:
            ax: figure axis
        """
        lines = []
        lineColors = []
        lineWidth = []
        for i in range(data["num_groups"]):
            for k in range(data["num_groups"]):
                sim = data["selfSimMat"][i][k]
                if sim > params["similarityThreshold"]:
                    simNorm = (sim-params["similarityThreshold"])/(1-params["similarityThreshold"])
                    lines.append([data["coordCenterGroups"][_] for _ in [i, k]])
                    lineColors.append([simNorm, 1-simNorm, 0, simNorm]) # last entry beeing the alpha value
                    lineWidth.append(simNorm*3)
        l = LineCollection(lines, linewidths=lineWidth, colors=lineColors)
        ax.add_collection(l)
        return ax

    def plot_patterns(self, ax, data, params, i):

        [patternStart, patternEnd] = self.getPatternStartEnd(params, data, i)
        patches = []
        colors = []
        maxPitch = max(data["pitch"])
        nPatterns = len(patternStart)
        for k in range(nPatterns):
            nOccurances = len(patternStart[k])
            col = [random.random(), random.random(), random.random()]
            for m in range(nOccurances-1):
                xOuter = .5*(data["onset"][patternStart[k][m]] + data["offset"][patternEnd[k][m+1]])
                yOuter = maxPitch#data["pitch"][patternStart[k][m]]
                radOuter = xOuter-data["onset"][patternStart[k][m]]
                w = data["offset"][patternEnd[k][m]]-data["onset"][patternStart[k][m]]

#                 xInner = .5*(data["onset"][patternEnd[k][m]] + data["offset"][patternStart[k][m+1]])
#                 yInner = data["pitch"][patternEnd[k][m]]
#                 radInner = xInner - data["onset"][patternEnd[k][m]]

                patches.append(Wedge((xOuter, yOuter), radOuter, 0, 180, width=w))
                colors.append(col)

        p = PatchCollection(patches, facecolors=colors, edgecolors=colors)
        ax.add_collection(p)


        return ax

    def prepare_data(self, data, i, params):
        """ Prepares data for visualization
        Args:
            data (dict): Data (from melfeature)
            params (dict): Parameters
        Returns:
            data (dict): Enriched data
        """
        # get note parameters
        data["onset"] = data["featureValues"][i][data["featureLabels"].index(params["onsetFeatureName"])]
        data["duration"] = data["featureValues"][i][data["featureLabels"].index(params["durationFeatureName"])]
        data["pitch"] = data["featureValues"][i][data["featureLabels"].index(params["pitchFeatureName"])]

        try:
            data["nNotes"] = len(data["onset"])
        except TypeError:
            # special treatment for scalar value (1 note)
            data["nNotes"] = 1
            data["pitch"] = [data["pitch"]]
            data["onset"] = [data["onset"]]
            data["duration"] = [data["duration"]]


        data["offset"] = [data["onset"][_] + data["duration"][_] for _ in range(data["nNotes"])]
        data["lastOffset"] = max(data["offset"])
        data["relOnset"] = [_/data["lastOffset"] for _ in data["onset"]]
        data["relOffset"] = [_/data["lastOffset"] for _ in data["offset"]]

        minPitch = min(data["pitch"])
        data["pitchNorm"] = [_ - minPitch for _ in data["pitch"]]
        data["pitchRange"] = max(data["pitchNorm"])

        # get self similarity matrix
        data["selfSimMat"] = []
        if params["selfSimFeatureName"] in data["featureLabels"]:
            data["selfSimMat"] = data["featureValues"][i][data["featureLabels"].index(params["selfSimFeatureName"])]
            if data["nNotes"] == 1:
                data["selfSimMat"] = [data["selfSimMat"]]

        noteGrouping = True if params["noteGroupingFeatureName"] in data["featureLabels"] else False

        # get note grouping ID
        if noteGrouping:
            data["noteGroupID"] = data["featureValues"][i][data["featureLabels"].index(params["noteGroupingFeatureName"])]
            if data["nNotes"] == 1:
                data["noteGroupID"] = [data["noteGroupID"]]
            noteGrouping = True
        else:
            # assign all notes to same group
            data["noteGroupID"] = [0 for _ in range(len(data["pitch"]))]

        # avoid overflow by always setting first group ID to zero
        data["noteGroupID"] = [_ - min(data["noteGroupID"]) for _ in data["noteGroupID"]]

        # reduce notes
        if noteGrouping and params["noteGroupingSelect"] is not None:
            idx2Select = [k for k in range(data["nNotes"]) if data["noteGroupID"][k] in params["noteGroupingSelect"]]
            data["pitch"] = [data["pitch"][k] for k in range(data["nNotes"]) if k in idx2Select]
            data["onset"] = [data["onset"][k] for k in range(data["nNotes"]) if k in idx2Select]
            data["duration"] = [data["duration"][k] for k in range(data["nNotes"]) if k in idx2Select]
            data["noteGroupID"] = [data["noteGroupID"][k] for k in range(data["nNotes"]) if k in idx2Select]
            data["nNotes"] = len(data["onset"])

        # radii for circular piano roll
        data["innerRadius"] = 20
        data["outerRadius"] = data["innerRadius"] + data["pitchRange"] + 2

        # compute wedge angles from relative offset to onset (flip necessary because of angle rotation / flip)
        data["angleStartNote"] = [self.rotate_and_flip_angle(360*_) for _ in data["relOffset"]]
        data["angleEndNote"] = [self.rotate_and_flip_angle(360*_) for _ in data["relOnset"]]

        # note centroids
        if params["layout"] == "Circular":
            data["noteCentroidRel"] = [(data["onset"][_]+.5*(data["offset"][_]-data["onset"][_]))/data["lastOffset"] for _ in range(data["nNotes"])]
            data["noteCentroidAngle"] = [self.rotate_and_flip_angle(360*_) for _ in data["noteCentroidRel"]]
            data["noteCentroidRadius"] = [data["innerRadius"] + data["pitchNorm"][_]+.5 for _ in range(data["nNotes"])]
            data["noteCentroidCoordinates"] = [self.getXYFromAngleAndRadius(data["noteCentroidAngle"][_], data["noteCentroidRadius"][_]) for _ in range(data["nNotes"])]
        else:
            data["noteCentroidCoordinates"] = [[data["onset"][n]+.5*data["duration"][n], data["pitch"][n]] for n in range(data["nNotes"])]

        # colors for note events
        alternating_colors = [params["foregroundColor"][_ % 2] for _ in range(data["nNotes"])]
        data["colorNoteEvent"] = [alternating_colors[data["noteGroupID"][_]] for _ in range(data["nNotes"])]

        # groups
        data["note_id_in_group"] = []
        data["onsetGroup"] = []
        data["offsetGroup"] = []
        data["relStartGroup"] = []
        data["relEndGroup"] = []
        data["colorGroup"] = []
        data["minPitchGroup"] = []
        data["maxPitchGroup"] = []

        group_id = list(set(data["noteGroupID"]))
        data["num_groups"] = len(group_id)

        for uid in group_id:
            # note IDs in current group
            note_id_in_group = [_ for _ in range(data["nNotes"]) if data["noteGroupID"][_] == uid]
            data["note_id_in_group"].append(note_id_in_group)
            data["onsetGroup"].append(data["onset"][note_id_in_group[0]])
            data["offsetGroup"].append(data["offset"][note_id_in_group[-1]])

            data["relStartGroup"].append(data["onsetGroup"][-1]/data["lastOffset"])
            data["relEndGroup"].append(data["offsetGroup"][-1]/data["lastOffset"])
            data["colorGroup"].append(self.lighten_up_color(data["colorNoteEvent"][note_id_in_group[0]]))

            pitchesInGroup = [data["pitch"][_] for _ in note_id_in_group]
            data["minPitchGroup"].append(min(pitchesInGroup))
            data["maxPitchGroup"].append(max(pitchesInGroup))

        if params["layout"]=="Circular":
            data["relCenterGroup"] = [.5*data["relStartGroup"][_] + .5*data["relEndGroup"][_] for _ in range(data["num_groups"])]
            data["angleStartGroup"] = [self.rotate_and_flip_angle(360*_) for _ in data["relEndGroup"]]
            data["angleEndGroup"] = [self.rotate_and_flip_angle(360*_) for _ in data["relStartGroup"]]
            data["angleCenterGroup"] = [self.rotate_and_flip_angle(360*_) for _ in data["relCenterGroup"]]
            data["coordCenterGroups"]  = [self.getXYFromAngleAndRadius(data["angleCenterGroup"][_], data["innerRadius"]-2) for _ in range(data["num_groups"])]

        # group index x,y coordinates
        if params["layout"]=="Circular":
            coord = [self.getXYFromAngleAndRadius(data["angleCenterGroup"][_], data["outerRadius"]+2) for _ in range(data["num_groups"])]
            data["groupIndexX"] = [_[0] for _ in coord]
            data["groupIndexY"] = [_[1] for _ in coord]
        else:
            data["groupIndexX"] = [.5*(data["onsetGroup"][_] + data["offsetGroup"][_]) for _ in range(data["num_groups"])]
            data["groupIndexY"] = [_+3 for _ in data["maxPitchGroup"]]


        return data

    def getPatternStartEnd(self, params, data, i):
        """ THIS IS A TEMPORARY HACK TO GET the pattern start & end indices (as complex datatype - list of list of list) from melfeature to the visualization ->
            transport it in the params dict """
                # get pattern start & end indices
        for f in params["featureList"][i]:
            sinkVals = f.getSinkModuleValues()
            if "patternStart" in list(sinkVals.keys()):
                data["patternStart"] = sinkVals["patternStart"]
            if "patternEnd" in list(sinkVals.keys()):
                data["patternEnd"] = sinkVals["patternEnd"]
        return data["patternStart"], data["patternEnd"]
