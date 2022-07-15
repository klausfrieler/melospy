#import applications.melvis_tools as mtools
import matplotlib.pyplot as pl
import numpy as np

import melospy.visualize.visualizer_tools as vtools


class VisualizerMatrixPlot(object):
    '''
    Main class for matrix plot visualization
    '''

    def get_default_param_values(self):
        """ Returns default parameter values
        Returns:
            Dict with default parameter values
        """
        dv = dict()
        dv["fontSize"] = 4
        dv["plotFeature"] = "ssm"
        dv["barWidth"] = 2
        dv["zeroIndexing"] = False
        dv["segmentUnit"] = "Phrase"
        dv["colorMap"] = "RdYlGn_r"
        dv["title"] = "Self-Similarity Matrix"

        return dv

    def process(self,params,data, proc_func = None):
        """ Main process function for matrix plot visualization
        Args:
            params: Dictionary with visualization parameters
            data: Dictionary with dataset (see input_output/melfeature_csv_reader.py for details)
        Returns:
            params: Dictionary with visualization parameters
            data: Dictionary with dataset (see input_output/melfeature_csv_reader.py for details)
        """
        params = vtools.add_missing_params_by_default_values(params, self.get_default_param_values())

        # find feature to plot
        featureIdx = data["featureLabels"].index(params["plotFeature"])
        nItems = len(data["itemLabels"])

        pl.figure()

        for i in range(nItems):
            if proc_func:
                proc_func(i, nItems, data["itemLabels"][i])

            mat = np.array(data["featureValues"][i][featureIdx])

            # create matrix for one segment case
            if np.size(mat) == 1:
                mat = np.array([[1]])

            pl.clf()
            pl.imshow(mat, aspect='equal', interpolation='Nearest', cmap=params["colorMap"])

            # set figure properties
            xtick = list(range(mat.shape[1]))
            ytick = list(range(mat.shape[0]))

            if params["zeroIndexing"]:
                xticklabels = [str(k) for k in xtick]
                yticklabels = [str(k) for k in ytick]
            else:
                xticklabels = [str(k+1) for k in xtick]
                yticklabels = [str(k+1) for k in ytick]

            params["xTick"] = xtick
            params["yTick"] = ytick
            params["xTickLabels"] = xticklabels
            params["yTickLabels"] = yticklabels
            params["xLabel"] = params["segmentUnit"]
            params["yLabel"] = params["segmentUnit"]
            params["colorBar"] = True

            vtools.set_figure_properties(pl, params)

            # SHOW / EXPORT
            fileName = vtools.save_plot(pl, vtools.clean_up_item_label(data["itemLabels"][i]), params)
            params["outFile"].append(fileName)

        return params, data
