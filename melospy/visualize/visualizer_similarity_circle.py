
#import applications.melvis_tools as mtools
import matplotlib.pyplot as pl
import numpy as np
from matplotlib.patches import Arc, Circle

import melospy.visualize.visualizer_tools as vtools
from melospy.similarity.self_similarity_matrix import SelfSimilarityMatrix


class VisualizerSimilarityCircle(object):
    '''
    Main class for bar plot visualization
    '''

    def get_default_param_values(self):
        """ Returns default parameter values
        Returns:
            Dict with default parameter values
        """
        dv = dict()
        dv["pitchFeatureName"] = "GENERAL_MELODY_RAW.pitch"
        dv["noteGroupingFeatureName"] = "GENERAL_MELODY_RAW.phraseid"
        dv["plotClassItems"] = True
        dv["plotClassCentroids"] = True
        dv["title"] = "Bar plot"
        dv["plotForEach"] = "feature"
        dv["showGrid"] = False
        dv["fontSize"] = 4
        dv["barWidth"] = 2
        dv["groupColoring"] = False

        return dv

    def process(self,params,data, proc_func = None):
        """ Main process function for bar plot visualization
        Args:
            params: Dictionary with visualization parameters
            data: Dictionary with dataset (see input_output/melfeature_csv_reader.py for details)
        Returns:
            params: Dictionary with visualization parameters
            data: Dictionary with dataset (see input_output/melfeature_csv_reader.py for details)
        """
        # set parameters
        params = vtools.add_missing_params_by_default_values(params, self.get_default_param_values())

        nFeatures = len(data["featureLabels"])
        nItems = len(data["itemLabels"])

        pitchAll = []
        phraseIDAll = []
        itemIDAll = []

        # collect
        phraseIDOffset = 0

        for i in range(nItems):

            pitch = data["featureValues"][i][data["featureLabels"].index(params["pitchFeatureName"])]
            phraseID = data["featureValues"][i][data["featureLabels"].index(params["noteGroupingFeatureName"])]

            # ? test: convert to interval
            pitch = [pitch[_+1]-pitch[_] for _ in range(len(pitch)-1)]
            pitch.append(0)

            # TODO: allow different representations?

            nNotes = len(pitch)
            for n in range(nNotes):
                pitchAll.append(pitch[n])
                phraseIDAll.append(phraseID[n]+phraseIDOffset)
                itemIDAll.append(i)
            # ensure unique phrases
            phraseIDOffset += phraseID[-1] +1


        print(len(pitchAll), ' ... ')

        # compute self-similarity matrix
#         selfSimMat = SelfSimilarityMatrix().process(np.array(pitchAll),np.array(phraseIDAll))


#         print selfSimMat
#         elif params["plotForEach"] == "item":
#             for i in range(nItems):
#
#                 featureVector = [data["featureValues"][i][_] for _ in range(nFeatures) ]
#                 s
        # PLOT
        pl.figure()
#         pl.subplot(1,4,(2,3))
#
#         a = Arc(xy=[74.2, 15], width=25, height=38, angle=21, theta1=18, theta2=249)
#         pl.gca().add_artist(a)
#         a.set_lw(3)
#
#         pl.savefig('test.png',format=params["figureExtension"],dpi=params["dpi"])
        pl.show()

#         pl.show()
#         pl.barh(np.arange(len(featureVector))*params["barWidth"],featureVector,height=params["barWidth"])
#
#         # PROPERTIES
#         params["yTickLabels"] = data["featureLabels"]
#         params["yTick"] = np.arange(len(featureVector))*params["barWidth"]+.5*params["barWidth"]
#         params["yLimMax"] = len(featureVector)*params["barWidth"]
#         params["yLimMin"] = 0
#         valRange = max(featureVector) - min(featureVector)
#         if valRange == 0:
#             valRange = .2
#         if "xLimMax" not in params.keys():
#             params["xLimMax"] = max(featureVector) + .2*valRange
#         if "xLimMin" not in params.keys():
#             params["xLimMin"] = min(featureVector) - .2*valRange
#         params["title"] = data["itemLabels"][i]
#         vtools.set_figure_properties(pl,params)
#
#         # SHOW / EXPORT
#         if params["showPlot"]:
#             pl.show()
#         if params["savePlot"]:
#             fileName = vtools.save_plot(pl,"bar_plot_"+data["itemLabels"][i],params)
#             if params["verbose"]:
#                 print "Saved figure to ",fileName
#             results = mtools.add_results(results,"visualizer","Saved figure to "+fileName, False)
#             params["outFile"].append(fileName)
#         else:
#             raise Exception("Non-valid value for parameter plotForEach!")
#



        return params, data
