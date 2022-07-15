'''
Auxiliary functions for visualization tools
Created on 02.11.2013

@author: Jakob
'''

import math
import operator
import os
import random
import re

import numpy as np
import yaml
from matplotlib.ticker import FixedLocator

from melospy.rootpath import root_path


def clean_up_item_label(itemLabel):
    """ Removes file parts such as PREFINAL or .sv
    Args:
        itemLabel: Item label
    Returns:
        clean item label
    """
    if itemLabel.lower().find('.mid') > 0:
        itemLabel = os.path.split(itemLabel)[-1]
        itemLabel = itemLabel[:-4]
    else:
        itemLabel = itemLabel.replace(".sv", "")
        itemLabel = itemLabel.replace("_PREFINAL", "")
        itemLabel = itemLabel.replace("_FINAL", "")
    return itemLabel

def add_legend_color_group_labels(pl, groupLabels, groupColors, fontSize):
    """ Adds legend to bar plot with different colors for items of different groups
    Args:
        pl: pyplot instance
        groupLabels: List of group labels
        groupColors: List of RGB triples assigned to each group
        fontSize: Font size in pt
    """
    nGroups = len(groupColors)
    for i in range(nGroups):
        pl.gca().text(10, 1+i*(fontSize+3), groupLabels[i], fontsize=fontSize, color=groupColors[i])
    pl.gca().axes.get_xaxis().set_visible(False)
    pl.gca().axes.get_yaxis().set_visible(False)
    pl.gca().invert_yaxis()
    pl.gca().set_frame_on(False)
    pl.ylim(ymin=0, ymax=((4*nGroups)*(fontSize+3)))
    pl.xlim(xmin=0, xmax=100)

def set_figure_properties(plt, params):
    """ Sets figure properties as defined in dictionary params
        Args:
            plt: Plot handle
            params: Dictionary with parameters
    """
    if "showGrid" in list(params.keys()):
        plt.gca().grid(params["showGrid"], which='major')#, color=[.55,.55,.55], linestyle='-')
    if "showMinorGrid" in list(params.keys()):
        plt.gca().grid(params["showMinorGrid"], which='minor', color=[.85, .85, .85], linestyle='-')
    if "title" in list(params.keys()):
        plt.title(params['title'], fontsize=params["fontSize"])
    if "xLabel" in list(params.keys()):
        plt.xlabel(params['xLabel'], fontsize=params["fontSize"])
    if "yLabel" in list(params.keys()):
        plt.ylabel(params['yLabel'], fontsize=params["fontSize"])
    if "yTickLabels" in list(params.keys()):
        plt.gca().set_yticklabels(params["yTickLabels"])
    if "yTick" in list(params.keys()):
        plt.yticks(params["yTick"])
    if "xTickLabels" in list(params.keys()):
        plt.gca().set_xticklabels(params["xTickLabels"])
    if "xTick" in list(params.keys()):
        plt.xticks(params["xTick"])
    if "fontSize" in list(params.keys()):
        plt.tick_params(labelsize=params["fontSize"])
    if "xLimMax" in list(params.keys()):
        plt.xlim(xmax=params["xLimMax"])
    if "xLimMin" in list(params.keys()):
        plt.xlim(xmin=params["xLimMin"])
    if "xTickMajor" in list(params.keys()):
        plt.gca().xaxis.set_major_locator(FixedLocator(params["xTickMajor"]))
    if "xTickMinor" in list(params.keys()):
        plt.gca().xaxis.set_minor_locator(FixedLocator(params["xTickMinor"]))
    if "yLimMax" in list(params.keys()):
        plt.ylim(ymax=params["yLimMax"])
    if "yLimMin" in list(params.keys()):
        plt.ylim(ymin=params["yLimMin"])
    if "yTickMajor" in list(params.keys()):
        plt.gca().yaxis.set_major_locator(FixedLocator(params["yTickMajor"]))
    if "yTickMinor" in list(params.keys()):
        plt.gca().yaxis.set_minor_locator(FixedLocator(params["yTickMinor"]))
    if "colorBar" in list(params.keys()) and params["colorBar"]:
        cbar = plt.colorbar()
        cbar.ax.tick_params(labelsize=params["fontSize"])


def sort_data(data,sortAfter,sortDirection="ascending"):
    """ Sorts feature matrix in dataset according to values of one feature (most often a metadata feature such as artist)
    Args:
        data: Dictionary with dataset (see input_output/melfeature_csv_reader.py for details)
        sortAfter: Feature label to be used as sorting criterion
        sortDirection: "ascending" or "descending"
    Returns:
        data: Dictionary with dataset (see input_output/melfeature_csv_reader.py for details)
    """
    try:
        # index of feature used as sort criterion
        featureIdx = data["featureLabels"].index(sortAfter)
        # feature values
        sortAfterVals = [data["featureValues"][i][featureIdx] for i in range(len(data["featureValues"]))]
    except ValueError:
        raise Exception("Value of sortAfter not found in feature list!")

    reverseItems = False if sortDirection == "descending" else True
    idx = sorted(enumerate(sortAfterVals), key=operator.itemgetter(1), reverse=reverseItems)
    for i, item in enumerate(idx):
        idx[i] = operator.itemgetter(0)(item)

    # resort data
    data["itemLabels"] = [data["itemLabels"][_] for _ in idx]
    data["featureValues"] = [data["featureValues"][_] for _ in idx]
    return data


def convert_folder_names_to_absolute_path(folderNames):
    """ Converts a list of folder names (path hierachy within Melospy framework) to an absolute path
    Args:
        folderNames: List of folder names (relative to MeloSpy root path)
    Returns:
        absPath: Absolute path of last folder in given folder list
    """
    # start with root directory
    absPath = root_path()
    # append folder names
    for folder in folderNames:
        absPath = os.path.join(absPath, folder)
    return absPath

def save_plot(pl, fileSuffix, params):
    """ Saves a given matplotlib figure to a file
    Args:
        params: Dict with melvis parameters
        fileSuffix: Filename suffix (e.g. "scatter_plot")
        pl: instance of matplotlib.pyplot holding the figure to be saved
    Returns:
        fileName: Filename of exported image file
    """
    #for file mode, fileSuffix might contain path information which result in
    #invalid file names, so use the base name

    fileSuffix = os.path.basename(fileSuffix)
    fileName = os.path.join(params["outDir"], params["filePrefix"]+"_"+fileSuffix+"." + params["figureExtension"])
    nonValidCharacters = ['!', '"', '$', '%', '&', '?', '*', '<', '>']
    for _ in nonValidCharacters:
        fileName = fileName.replace(_, '_')
    pl.savefig(fileName, dpi=params["dpi"], bbox_inches='tight', pad_inches=0.1)
    return fileName

def remove_nan_or_inf(data,remove="features",verbose=False):
    """ Removes all features from given data dict with feature values of NaN or Inf
    Args:
        data: Data dictionary
        remove: either "features" or "items" depending on what shall be removed from the data matrix
        verbose: Switch for verbose output (which features were eliminated
    Returns:
        data: (Modified) data dictionary
    """
    if remove not in ["items", "features"]:
        raise Exception("Parameter remove must be set to items or features!")
    if remove == "features":
        data["featureValues"] = data["featureValues"].T

    nUnitItems = data["featureValues"].shape[0]
    validIdx = [idx for idx in range(nUnitItems) if ( not np.isnan(np.min(data["featureValues"][idx])) and not np.isinf(np.min(data["featureValues"][idx])) )]
    if len(validIdx) == 0:
        raise Exception("After removing all "+remove+", the feature matrix is empty! Try another setting of parameter removeNaNorInf...")

    data["featureValues"] = data["featureValues"][validIdx]

    if remove == "features":
        data["featureValues"] = data["featureValues"].T
        data["featureLabels"] = [data["featureLabels"][i] for i in range(len(data["featureLabels"])) if i in validIdx]
    else:
        data["itemLabels"] = [data["itemLabels"][i] for i in range(len(data["itemLabels"])) if i in validIdx]

    if verbose:
        removedIdx = [i for i in range(nUnitItems) if i not in validIdx]
        if len(removedIdx) > 0:
            print("Two following "+remove+" were removed from the dataset due to Inf's and Nan's ")
            if remove=="features":
                for idx in removedIdx:
                    print(data["featureLabels"][idx])
            else:
                for idx in removedIdx:
                    print(data["itemLabels"][idx])

    return data

def dict_to_YML(d, fnYML):
    """
    Saves dictionary to YAML file
    Args:
        d: Dictionary
        fnYML: Absolute filename of YAML file
    """
    with open(fnYML, 'w') as yaml_file:
        yaml.dump(d, yaml_file)

def get_marker_and_color_matplotlib(N, darkerColors=False):
    """ Returns marker & color values for N unique classes to be used for Matplotlib visualizations
    Args:
        N: Number of classes
        darkerColors: Switch to enforce darker colors
    Returns:
        markers: List of Matplotlib marker characters
        colors: List of Matplotlib color triples
    """
    marker = "ov^<>sphD";
    marker = marker*int(math.ceil(float(N)/float(len(marker))))
    if darkerColors:
        colors = [[.5*random.random() for _ in range(3)] for _ in range(N)]
    else:
        colors = [[random.random() for _ in range(3)] for _ in range(N)]
    return marker, colors

def add_missing_params_by_default_values(params, defaultValues):
    """ Adds missing parameters by default values

        Args:
            params (dict): Parameters
            defaultValues (dict): Parameters to be set with default values
        Returns:
            params (dict): Parameters with added parameters

    """
    for key in list(defaultValues.keys()):
        if not key in list(params.keys()):
            params[key] = defaultValues[key]
    return params

def get_group_id_values(data, groupItem):

    """ Returns list of group IDs for each items grouped after a specific criterion
        Args:
            data (dict): Raw data
            groupItem: Grouping criterion ("artist", "solo")
        Returns:
            groupIDs (list): Group IDs for each item
            groupValues (list): Group values

    """
    if groupItem == "artist":
        items = data["itemLabelsArtist"]
        pass
    elif groupItem == "solo":
        items = data["itemLabelsSolo"]
        pass
    else:
        raise Exception("groupItem has no valid value!")
    uniqueItems = list(set(items))
    return [uniqueItems.index(x) for x in items], uniqueItems

def set_default_parameters_if_required(params, defaultParams):
    """ Sets default values to global parameters if they are not set.
        Args:
            params (dict): Parameters
            defaultParams (dict): Parameters to be checked with default values.
    """
    for key, value in list(defaultParams.items()):
        if key not in list(params.keys()):
            params[key] = value
    return params

def generate_dict_from_dict_using_key_list(source, keyList):
    """ Returns dictionary with key-value-pairs taken from given dictionary based on key list.
        Args:
            source (dict): Source dictionary
            keyList (list/tuple): List with keys of interest in source dictionary
        Returns
            target (dict): Newly created dictionary
    """
    target = dict()
    for key in keyList:
        target[key] = source[key]
    return target


def reformat_title(title):
    """ Re-formats title from camel case with underscore to readable format

        Args:
            title (string/list): Unformatted title / List of unformated titles (e.g. "MilesDavis_MySolo")
        Returns:
            titleFormatted (string): Formatted title (e.g. "Miles Davis - My Solo")

    """
    if isinstance(title, list):
        return [reformat_title(x) for x in title]
    titleFormatted = re.sub("([A-Z])", r" \g<0>", title)
    titleFormatted = titleFormatted.replace("_", " -")
    if titleFormatted[0] == ' ':
        titleFormatted = titleFormatted[1:]
    return titleFormatted

def map_values_to_range(values, minVal, maxVal):
    """ Maps values to range defined by minVal and maxVal and returns relative values in [0,1]

        Args:
            values (list): Values to be mapped
            minVal (float): Lower bound of range
            maxVal (float): Upper bound of range
        Return:
            valuesMapped (list): Original values mapped to [0,1] based on defined range

    """
    valRange = maxVal-minVal
    return [((float(v) - float(minVal))/valRange) for v in values]


# -------------------
# NOT TESTED SO FAR ...
# -------------------


def clean_up_feature_vector(featureVector):
    """ Removes InF and NaNs from feature vector

        Args:
            featureVector (list): Raw feature vector
        Returns
            featureVector (list): Feature vector with replaced NaN and Infs
    """
    defaultVal = min(featureVector)
    return [val if ( not np.isnan(val) and np.isfinite(val) ) else defaultVal for val in featureVector]

def get_feature_vector(data,featureLabel,itemLabel=""):
    """ Extracts feature vector (numpy array) from a feature matrix, which is stored
        as two-dimensional list
        data: Dictionary with raw data
        featureLabel: Label of feature to be selected """
    if type(featureLabel) not in (list, tuple):
        idx = data["featureLabels"].index(featureLabel)
        isScalarFeature = True
        # TODO raise exception if feature was not found!
    #        if isScalarFeature:
        featureVector = [];
        for row in data["features"]:
            itemFeature = row[idx]
            if not isinstance(itemFeature, list):
                featureVector.append(itemFeature)
            else:
                isScalarFeature = False
                featureVector.append(np.array(itemFeature))
        if isScalarFeature:
            return np.array(featureVector)
        else:
            return featureVector
    else:
        # find row in feature matrix for itemLabel
        idx = data["itemLabels"].index(itemLabel)
        itemLabelFeatureVector = data["features"][idx]
        featureVector = []
        for feature in featureLabel:
            idx = data["featureLabels"].index(feature)
            featureVector.append(itemLabelFeatureVector[idx])
        return featureVector

def generate_axis_tick_and_label(values,numberTicks=5,numberDecimalPlacesTickLabels=2,marginInPercentOfRange = 0.2):
    """ Generates vectors with tick values and tick labels for a given vector to be plotted. Lower and upper margin can be set to make sure that minimum and maximum ticks are outside the value range.

        Args:
            values (list): Values to be plotted
            numberTicks (int): Number of ticks to partition the value range
            numberDecimalPlacesTickLabels (int): Numeric precision (number of decimal places) for float-string conversion to generate the axis tick labels
        Returns:
            tickValues (list): Tick values
            tickLabels (list): Tick labels

    """
    marginInPercentOfRange = float(marginInPercentOfRange)
    maxVal = max(values)
    minVal = min(values)
    valRange = maxVal-minVal

    # margin correction
    minVal = minVal - marginInPercentOfRange*valRange
    maxVal = maxVal + marginInPercentOfRange*valRange

    deltaVal = float(valRange) / float(numberTicks)
    tickValues = [minVal+float(i)*deltaVal for i in range(numberTicks+1)]
#     else:
#         # find numeric precision
#         stepSizeRaw = valRange / float(numberTicks)
#         stepSizeRaw = 0.1 if stepSizeRaw < .01 else stepSizeRaw
#         stepSize = 10**(math.floor(math.log10(stepSizeRaw)))
#
#         # find axis tick boundaries based on stepSize including a margin around minimum and maximum value
#         minTickVal = math.floor(minVal/stepSize)*stepSize - 5*stepSize
#         maxTickVal = math.ceil(maxVal/stepSize)*stepSize + 5*stepSize
#
#         tickValues = np.arange(minTickVal,maxTickVal,stepSize).tolist()
#
#         # reduce number of ticks if necessary
#         #     while ( len(tickValues) >= 2*numberTicks ):
#         #         tickValues = [v for v in tickValues[0:len(tickValues)-1:2]]

    tickLabels = [str(round(f, numberDecimalPlacesTickLabels)) for f in tickValues]
    return tickValues, tickLabels

def get_unique_color_shape_pairs(nPairs):
    """ Returns two lists of color & shape labels to be used for Protovis / JavaScript

    Args:
        nPairs: Required number of unique color-shape pairs
    Returns:
        colors: List of color labels
        shapes: List of shape labels
    """
    # color and shape values for all classes
    shapes = ["circle", "square", "triangle", "cross", "diamond"]
    # more colors here: http://www.w3.org/TR/SVG/types.html#ColorKeywords
    colors = ["black", "blue", "maroon", "seagreen", "darkviolet", "olive", "lightcoral", "teal"]

    # TODO: this is not necessary if we define more colors ;)
    if nPairs > len(shapes)*len(colors):
        raise Exception("Too many groups to find unique shape - color combinations...")

    nShapes = len(shapes)
    nColors = len(colors)

    # extend shapes to number of groups
    shapes = shapes*int(math.ceil(nPairs/nShapes))
    shapes = shapes[:nPairs-1]

    # extend colors to number of groups
    n = int(math.ceil(nPairs/nColors))
    colorsTemp = []
    for i in range(len(colors)):
        for k in range(n):
            colorsTemp.append(colors[i])
    colors = colorsTemp[:nPairs-1]

    return colors, shapes

def get_unique_colors_for_grouping(groupIDs,darkerColors=False):
    """ returns a list of RGB triples (3 element list with elements between 0 and 1) for items based on
        item group IDs
    Args:
        groupIDs: List of group IDs (int)
        darkerColors: Switch to enforce darker colors
    Returns:
        colors: List of RGB color triples (3 element lists) with color value for each item
    """
    # make sure ids start at 0
    minID = min(groupIDs)
    groupIDs = [groupIDs[_] - minID for _ in range(len(groupIDs))]

    nGroups = len(set(groupIDs))
    marker, colors = get_marker_and_color_matplotlib(nGroups, darkerColors)
    return [colors[groupIDs[i]] for i in range(len(groupIDs))], colors
