import os
import platform

import matplotlib

if platform.system() == 'Darwin':
    matplotlib.use("macosx")
elif platform.system() == 'Linux':
    pass
elif platform.system() == 'Windows':
    matplotlib.use("TkAgg")
else:
    raise Exception('Operating system is not supported by melvis currently...')

import melospy.input_output.melvis_tools as mtools
import melospy.visualize.visualizer_tools as vtools
from melospy.input_output.melfeature_csv_reader import MelfeatureCSVReader
from melospy.visualize.visualizer import Visualizer


class Melvis(object):
    """ Class implementation of melfeature visualizer (Melvis) """

    def __init__(self):
        pass

    def get_default_param_values(self):
        """
        Creates a dictionary with default values for melvis
        Returns:
            default_values (dict): Default parameter values
        """
        default_values = dict()
        default_values["inFile"] = "melvis.csv"
        default_values["inDir"] = ["applications", "test", "melfeature", "results"] # relative to MeloSpy root folder
        default_values["grouping"] = None
        default_values["learnMode"] = None
        default_values["selectFeatures"] = None # meaning that all features are kept
        default_values["removeFeatures"] = None
        default_values["outDir"] = ["applications", "test", "melvis", "results"]
        default_values["outFile"] = []
        default_values["showPlot"] = False
        default_values["filePrefix"] = "visualization"
        default_values["removeNaN"] = "item"
        default_values["NaNLabel"] = "NA"
        default_values["sortDatasetAfter"] = None
        default_values["sortDatasetDirection"] = "ascending"
        return default_values

    def process(self, config_file):
        """
        Main function for melvis
        Args:
            config_file: Configuration file for melvis
            verbose: Switch for verbose output
        Returns:
            params: Dict with parameters
            data: Dict with data
        """
        # load parameters from config file
        params = mtools.load_params_from_config_file(config_file)
        return self.process_with_params(params)

    def process_with_params(self, params, data=None, proc_func=None):
        """
        Main function for melvis that can be called with given parameters
        Args:
            params (dict): Melvis parameters (from config file)
        Returns:
            params: Dict with parameters
            data: Dict with data
        """

        # add default values for missing parameters
        params = vtools.add_missing_params_by_default_values(params, self.get_default_param_values())

        if not data:
            # convert directories to absolute paths if given as list of directories (relative to MeloSpy root directory)
            if isinstance(params["inDir"], list):
                params["inDir"] = vtools.convert_folder_names_to_absolute_path(params["inDir"])
            if isinstance(params["outDir"], list):
                params["outDir"] = vtools.convert_folder_names_to_absolute_path(params["outDir"])

            # add path if inFile is just given as file name without path
            infile_path = os.path.dirname(params["inFile"])
            if not infile_path:
                params["inFile"] = os.path.join(params["inDir"], params["inFile"])
            else:
                params["outDir"] = infile_path
            file_format = params["file_format"]
            convention = params["convention"]
            # FEATURES
            reader = MelfeatureCSVReader()
            data = reader.read_raw(params["inFile"], file_format=file_format, convention=convention)


        return self.process_with_params_and_data(params, data, proc_func=proc_func)
    def hotfix_reformat_feature_values(self, feature_values):
        def len_wrap(v):
            l = len(v) if isinstance(v, list) else 1
            return l
        fv = feature_values
        max_len = max([len_wrap(v) for v in fv])
        ret = []

        for i in range(max_len):
            row = []
            for _, val in enumerate(fv):
                if isinstance(val, list):
                    v = val[i]
                else:
                    v = val
                row.append(v)
            ret.append(row)

        return ret

    def hotfix_segmentation_groups(self, data):
        """Temporary fix of vizualisation with segmentations
            by imitating the no segmentation case
            TODO: Rework melvis desing by using pandas and internal communication
            instead of using feature result files.
        """
        #tmp_featurelabels = [_ for _ in data["featureLabels"] if _ not in ["seg_type", "seg_id"]]
        tmp_featureLabels = list(set(data["featureLabels"]).difference({"seg_type", "seg_id"}))
        #print "tmp_featurelabels", tmp_featureLabels
        #print data["featureValues"]
        #seg_ids = data["featureValues"]["seg_id"]
        #seg_types = data["featureValues"]["seg_type"]
        gL = data["groupLabels"]
        tmp_groupLabels = []
        #print len(data["featureValues"]), len(gL)
        tmp_featureValues = []
        for i, label in enumerate(gL):
            seg_type = data["featureValues"][i][0]
            seg_id = data["featureValues"][i][1]
            if isinstance(seg_id, list):
                for _, si in enumerate(seg_id):
                    tmp_label = "{}.{}.{}".format(label, seg_type, si)
                    tmp_groupLabels.append(tmp_label)
                tmp_fv = self.hotfix_reformat_feature_values(data["featureValues"][i][2:])
                tmp_featureValues.extend(tmp_fv)
            else:
                tmp_label = "{}.{}.{}".format(label, seg_type, seg_id)
                tmp_groupLabels.append(tmp_label)
                tmp_featureValues.append(data["featureValues"][i][2:])
                #print "groupLabel", tmp_label
        #print "tmp_featureValues", tmp_featureValues
        data["featureLabels"] = tmp_featureLabels
        data["groupLabels"] = tmp_groupLabels
        data["itemLabels"] = tmp_groupLabels
        data["featureValues"] = tmp_featureValues
        data["itemGroupID"] = list(range(len(tmp_groupLabels)))
        return data

    def process_with_params_and_data(self, params, data, proc_func=None):

        # CLEANING FROM NAN VALUES
        data = mtools.clean_data_from_NaN(data, remove=params["removeNaN"], nanLabel=params["NaNLabel"])

        # SORTING
        if params["sortDatasetAfter"] is not None:
            data = vtools.sort_data(data, params["sortDatasetAfter"], params["sortDatasetDirection"])

        # GROUPING
        reader = MelfeatureCSVReader()
        data = reader.group_items_and_select_features(data, groups=params["grouping"], selectFeatures=params["selectFeatures"], removeFeatures=params["removeFeatures"])
        if "seg_type" in data["featureLabels"]:
            data = self.hotfix_segmentation_groups(data)
        #print "data.keys", data.keys()
        #print "data.featureLabels", len(data["featureLabels"]), data["featureLabels"]
        #print "data.groupLabels", len(data["groupLabels"]), data["groupLabels"]
        #print "data.itemGroupID", len(data["itemGroupID"]), data["itemGroupID"]
        #print "data.itemLabels", len(data["itemLabels"]), data["itemLabels"]
        #print "data", data["featureValues"]

        # VISUALIZATION
        params, data = Visualizer().process(params, data, proc_func=proc_func)

        return params, data
