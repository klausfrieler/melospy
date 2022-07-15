
#import applications.melvis_tools as mtools
import matplotlib.pyplot as pl
import numpy as np

import melospy.visualize.visualizer_tools as vtools


class VisualizerScatterPlot(object):
    '''
    Main class for scatter plot visualization
    '''

    def get_default_param_values(self):
        """ Returns default parameter values
        Returns:
            Dict with default parameter values
        """
        dv = dict()
        dv["plotClassItems"] = True
        dv["plotClassCentroids"] = True
        dv["showGrid"] = True
        dv["title"] = "Scatter plot"
        dv["maxClasses"] = 20
        return dv

    def process(self,params,data, proc_func = None):
        """ Main process function for scatter plot visualization
        Args:
            params: Dictionary with visualization parameters
            data: Dictionary with dataset (see input_output/melfeature_csv_reader.py for details)
        Returns:
            params: Dictionary with visualization parameters
            data: Dictionary with dataset (see input_output/melfeature_csv_reader.py for details)
        """
        params = vtools.add_missing_params_by_default_values(params, self.get_default_param_values())

        nClasses = len(data["groupLabels"])
        nItems = len(data["itemLabels"])
        maxClasses = params["maxClasses"]
        if nClasses <= maxClasses:
            markers, colors = vtools.get_marker_and_color_matplotlib(nClasses)
        else:
            markers = "x"*nClasses
            colors = [0, 0, 0]*nClasses

        if proc_func:
            proc_func(0, 1, params["title"])

        pl.figure()
        pl.subplot(1, 3, (1, 2))

        data["featureValues"] = np.array(data["featureValues"])

        nClassItems = [0 for _ in range(nClasses)]
        for c, m, i, groupLabel in zip(colors, markers, list(range(nClasses)), data["groupLabels"]):
            idx = np.array([id for id in range(nItems) if data["itemGroupID"][id] == i])
            nClassItems[i] = len(idx)
            if nClassItems[i] > 0:
                if params["plotClassItems"]:
                    pl.scatter(data["featureValues"][idx, 0], data["featureValues"][idx, 1], c=c, marker=m, label=groupLabel, s=80)
            else:
                print("No class items for class ", groupLabel, " found!")

        # for c, m, i, groupLabel in zip(colors, markers, range(nClasses), data["groupLabels"]):
        #     idx = np.array([id for id in range(nItems) if data["itemGroupID"][id] == i])
        #     if nClassItems[i] > 0 and params["plotClassCentroids"]:
        #         pl.scatter(np.mean(data["featureValues"][idx, 0]), np.mean(data["featureValues"][idx, 1]), c=c, marker=m, label=groupLabel, s=120)

        # legend with small font size
        if nClasses <= maxClasses:
            pl.legend(bbox_to_anchor=(1.05, 1), scatterpoints=1, loc=2, borderaxespad=0., prop={'size':7}, ncol=2, numpoints=1).draggable()
            pl.setp(pl.gca().get_legend().get_texts(), fontsize = 8)
        pl.title(params["title"])

        # safety axis margin
        maxX = np.max(data["featureValues"][:, 0])
        maxY = np.max(data["featureValues"][:, 1])
        minX = np.min(data["featureValues"][:, 0])
        minY = np.min(data["featureValues"][:, 1])
        marginX = max(.01, .2*(maxX - minX))
        marginY = max(.01, .2*(maxY - minY))
        pl.xlim(minX-marginX, maxX+marginX)
        pl.ylim(minY-marginY, maxY+marginY)
        pl.xlabel(data["featureLabels"][0])
        pl.ylabel(data["featureLabels"][1])
        if params["showGrid"]:
            pl.grid()
        fileName = vtools.save_plot(pl, data["featureLabels"][0].replace('.', '_')+'_'+data["featureLabels"][1].replace('.', '_'), params)
        params["outFile"].append(fileName)

        return params, data
