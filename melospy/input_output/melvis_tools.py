""" melvis tools """

import yaml


def load_params_from_config_file(configFileName):
    """ Loads parameter from Melvis configuration file.

    Args:
        configFileName: Absolute filename of config YAML file
    Returns:
        A dict with YAML file content
    """
    with open(configFileName, 'r') as f:
        return yaml.load(f)


def clean_data_from_NaN(data,remove='item',nanLabel='NA'):
    """ Removes either features or items with NaNs
    Args:
        data (dict): data dictionary obtained with input_output.melfeature_csv_reader.MelfeatureCSVReader.read_raw()
        remove (string): "item" or "feature" (switch how deletion should be performed)
        nanLabel (string): nanLabel
    Return
        data (dict): cleaned data dictionary
    """
    itemsWithNaN = []
    featuresWithNaN = []
    numItems = len(data["featureValues"])
    numFeatures = len(data["featureValues"][0])
    for i in range(numItems):
        for f in range(numFeatures):
            try:
                if data["featureValues"][i][f] == nanLabel:
                    itemsWithNaN.append(i)
                    featuresWithNaN.append(f)
            except:
                pass
    if remove == 'item':
        if len(itemsWithNaN) == numItems:
            raise Exception("All items have NaN values and must be removed!")
        else:
            itemsValid = [_ for _ in range(numItems) if _ not in itemsWithNaN]
            data["featureValues"] = [data["featureValues"][_] for _ in itemsValid]
            data["itemLabels"] = [data["itemLabels"][_] for _ in itemsValid]

    elif remove == 'feature':
        if len(featuresWithNaN) == numItems:
            raise Exception("All features contain NaN values and must be removed!")
        else:
            featuresClean = []
            featuresValid = [_ for _ in range(numFeatures) if _ not in featuresWithNaN]
            for i in range(numItems):
                featuresClean.append([data["featureValues"][i][_] for _ in featuresValid])
            data["featureValues"] = featuresClean
            data["featureLabels"] = [data["featureLabels"][_] for _ in featuresValid]
    else:
        raise Exception('Parameter remove must be item or feature')
    return data
