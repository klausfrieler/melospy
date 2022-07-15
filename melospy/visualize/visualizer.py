import tkinter
import tkinter.filedialog

import melospy.visualize.visualizer_tools as vtools
from melospy.visualize.visualizer_bar_plot import VisualizerBarPlot
from melospy.visualize.visualizer_matrix_plot import VisualizerMatrixPlot
from melospy.visualize.visualizer_piano_roll import VisualizerPianoRoll
from melospy.visualize.visualizer_scatter_plot import VisualizerScatterPlot
from melospy.visualize.visualizer_similarity_circle import VisualizerSimilarityCircle


class Visualizer(object):
    '''
    Main class for visualization & result output
    '''

    def get_default_param_values(self):
        """ Returns default parameter values
        Returns:
            Dict with default parameter values
        """
        dv = dict()
        dv["figureExtension"] = "pdf"
        dv["dpi"] = 400

        return dv

    def process(self,params,data, proc_func=None):
        """ Main process function for visualization
        Args:
            params: Dictionary with visualization parameters
            data: Dictionary with dataset (see input_output/melfeature_csv_reader.py for details)
        Returns:
            params: Dictionary with visualization parameters
            data: Dictionary with dataset (see input_output/melfeature_csv_reader.py for details)
        """
        params = vtools.add_missing_params_by_default_values(params, self.get_default_param_values())

        if params["visualizeMode"] == "ScatterPlot":
            params, data = VisualizerScatterPlot().process(params, data, proc_func=proc_func)
        elif params["visualizeMode"] == "BarPlot":
            params, data = VisualizerBarPlot().process(params, data, proc_func=proc_func)
        elif params["visualizeMode"] == "PianoRoll":
            params, data = VisualizerPianoRoll().process(params, data, proc_func=proc_func)
        elif params["visualizeMode"] == "MatrixPlot":
            params, data = VisualizerMatrixPlot().process(params, data, proc_func=proc_func)
        else:
            raise Exception("Non-valid value for visualizeMode")

        return params, data
