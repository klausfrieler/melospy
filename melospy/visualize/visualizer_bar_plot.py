
import matplotlib.pyplot as pl
import numpy as np
from matplotlib.patches import Rectangle

import melospy.visualize.visualizer_tools as vtools

#import applications.melvis_tools as mtools


class VisualizerBarPlot(object):
    '''
    Main class for bar plot visualization
    '''

    def get_default_param_values(self):
        """ Returns default parameter values
        Returns:
            Dict with default parameter values
        """
        dv = dict()
        dv["title"] = "Bar plot"
        dv["plotForEach"] = "feature"
        dv["showGrid"] = True
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

        params = vtools.add_missing_params_by_default_values(params, self.get_default_param_values())
        nFeatures = len(data["featureLabels"])
        nItems = len(data["itemLabels"])
        #print data["featureLabels"]
        if params["plotForEach"] == "feature":
            for p in range(nFeatures):
                featureVector = [data["featureValues"][_][p] for _ in range(nItems) ]

                if proc_func:
                    proc_func(p, nFeatures, data["featureLabels"][p])

                # PLOT
                pl.figure()
                pl.subplot(1, 4, (2, 3))
                if params["groupColoring"]:
                    [colors, groupColors] = vtools.get_unique_colors_for_grouping(data["itemGroupID"], True)
                else:
                    colors = ['b' for _ in featureVector]
                pl.barh(np.arange(len(featureVector))*params["barWidth"], featureVector, height=params["barWidth"], color=colors)

                # PROPERTIES
                params["yTickLabels"] = [vtools.clean_up_item_label(_) for _ in data["itemLabels"]]
                params["yTick"] = np.arange(len(featureVector))*params["barWidth"]+.5*params["barWidth"]
                params["yLimMax"] = len(featureVector)*params["barWidth"]
                params["yLimMin"] = 0
                valRange = max(featureVector) - min(featureVector)
                if valRange == 0:
                    valRange = .2
                params["xLimMax"] = max(featureVector) + .2*valRange
                params["xLimMin"] = min(featureVector) - .2*valRange
                params["title"] = data["featureLabels"][p]
                vtools.set_figure_properties(pl, params)

                if params["groupColoring"]:
                    pl.subplot(1, 4, 4)
                    vtools.add_legend_color_group_labels(pl, data["groupLabels"], groupColors, params["fontSize"])

                fileName = vtools.save_plot(pl, data["featureLabels"][p].replace('.', '_'), params)
                params["outFile"].append(fileName)


        elif params["plotForEach"] == "item":
            for i in range(nItems):

                if proc_func:
                    proc_func(i, nItems, data["itemLabels"][i])

                featureVector = [data["featureValues"][i][_] for _ in range(nFeatures) ]

                # PLOT
                pl.figure()
                pl.subplot(1, 4, (2, 3))
                pl.barh(np.arange(len(featureVector))*params["barWidth"], featureVector, height=params["barWidth"])

                # PROPERTIES
                params["yTickLabels"] = data["featureLabels"]
                params["yTick"] = np.arange(len(featureVector))*params["barWidth"]+.5*params["barWidth"]
                params["yLimMax"] = len(featureVector)*params["barWidth"]
                params["yLimMin"] = 0
                valRange = max(featureVector) - min(featureVector)
                if valRange == 0:
                    valRange = .2
                if "xLimMax" not in list(params.keys()):
                    params["xLimMax"] = max(featureVector) + .2*valRange
                if "xLimMin" not in list(params.keys()):
                    params["xLimMin"] = min(featureVector) - .2*valRange
                params["title"] = vtools.clean_up_item_label(data["itemLabels"][i])
                vtools.set_figure_properties(pl, params)

                fileName = vtools.save_plot(pl, vtools.clean_up_item_label(data["itemLabels"][i]), params)
                params["outFile"].append(fileName)

        else:
            raise Exception("Non-valid value for parameter plotForEach!")

        return params, data
