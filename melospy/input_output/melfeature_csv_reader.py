'''
Created on 31.07.2013

@author: Jakob
'''
import csv
import re
from math import isnan

import numpy as np
from pandas import DataFrame, read_csv

separators = {'english':{'dec': '.', 'sep':';', 'col_sep':',', 'row_sep':':'},
              'german': {'dec': ',', 'sep':';', 'col_sep':':', 'row_sep':'|'}
             }
class MelfeatureCSVReader(object):
    '''
    Class to parse CSV files generated in the melfeature application
    '''

    def __init__(self):
        pass

    def string_vec_unique(self, stringList):
        """ Extracts unique elements from a list of strings

        Args:
            stringList: List of strings
        Returns:
            List of unique strings
        """
        uniqueStrings = []
        for s in stringList:
            try:
                uniqueStrings.index(s)
            except:
                uniqueStrings.append(s)
        return uniqueStrings

    def decode_item_labels(self, itemLabels):
        """ Decodes artist and solo name from item labels.

            Args:
                itemLabels (list): Strings with item labels (e.g. ["ArtistName1_Solo1","ArtistName2_Solo2"]
            Return:
                itemLabelsArtist (list): Strings with artist labels
                itelLabelsSolo (list): Strings with solo labels
        """
        itemLabelsArtist = []
        itemLabelsSolo = []
        for itemLabel in itemLabels:
            try:
                idx = itemLabel.index('_')
                itemLabelsArtist.append(itemLabel[:idx])
                itemLabelsSolo.append(itemLabel[idx+1:])
            except:
                itemLabelsArtist.append(itemLabel)
                itemLabelsSolo.append(itemLabel)

        return itemLabelsArtist, itemLabelsSolo

    def read_field(self, field, decode=True, convention="english"):
        """ Reads item feature value in melfeature CSV file, item can be scalar / string / list (=vector) or list of list (=matrix)
        Args:
            field: Item feature value from melfeature CSV file
        Returns:
            decoded field: Depending on the field content, either scalar / string / list (=vector) or list of list (=matrix)
        """
        import re
        #check for pure strings first
        #prevents vector and metrix feature of strings
        m = re.compile("[A-Za-z]")
        time_point = re.compile("[0-9]{1,2}[:][0-9]{2}")
        if time_point.match(field):
            #print "Found time point", field
            return self.read_scalar(field)

        if len(m.findall(field)) > 0:
            #print "Found string!", field
            return self.read_scalar(field)

        #transform to english convention
        if convention != "english":
            field = field.replace(",", ".")
            field = field.replace(":", ",")
            field = field.replace("|", ":")

        if decode:
            try:
                if field.find(":") != -1:
                    #print "Found matrix!", field
                    return self.read_matrix(field)
            except:
                pass
            try:
                if field.find(",") != -1:
                    return self.read_vector(field)
            except:
                pass
        return self.read_scalar(field)

    def read_scalar(self, field):
        """ Reads scalar field value
        Args:
            field: Field value
        Returns:
            Scalar field value as int or float
        """
        try:
            ret = float(field)
            if field.find(".") == -1:
                try:
                    ret = int(field)
                except:
                    pass
            return ret
        except ValueError:
            pass

        return str(field)

    def read_vector(self, field):
        """ Reads vector field values
        Args:
            field: Field value
        Return:
            List of vector elements (either as float or int)
        """
        floats =  field.find(".") != -1
        ret = field.split(",")
        try:
            if floats:
                ret = [float(_) for _ in ret]
            else:
                ret = [int(_) for _ in ret]
        except ValueError:
            # avoid cutting strings such as "Parker, Gillespie" in to vectors
            ret = field

        return ret

    def read_matrix(self, field):
        """ Reads matrix field values
        Args:
            field: Field value
        Return:
            Matrix values as list of list (first dimension = rows of matrix, second = columns)
        """
        rows = field.split(":")
        ret = []
        for row in rows:
            ret.append(self.read_vector(row))
        return ret

    def read_raw(self, CSVFileName, delimiter=";", decode=True, file_format="wide", convention="english"):
        if file_format == "wide":
            return self.read_wide_format(CSVFileName, delimiter=delimiter, decode=True, convention=convention)
        elif file_format == "long":
            return self.read_long_format(CSVFileName, delimiter=delimiter, convention=convention)
        raise ValueError("Unkown file format {}".format(file_format))

    def read_long_format(self, CSVFileName, delimiter=";", convention="english"):
        decimal = {"english":".", "german":","}[convention.lower()]
        if decimal == delimiter:
            raise ValueError("CSV delimiter '{}' identical to decimal separator '{}'".format(delimiter, convention))
        df = read_csv(CSVFileName, sep=delimiter, decimal=decimal)
        featureLabels = df.columns.tolist()
        first = featureLabels[0]
        featureLabels = featureLabels[1:]
        itemLabels = list(set(df[df.columns[0]]))
        featureValues = []
        for item in itemLabels:
            #print "Testing item", item
            try:
                query = '{} == "{}"'.format(first, item)
                tmp = df.query(query)
            except:
                print("Invalid pandas query: {}".format(query))
                continue
            itemVal = []
            for feat in featureLabels:
                #print "Testing feature", feat
                if len(set(tmp[feat])) == 1:
                    val = list(tmp[feat])[0]
                else:
                    val = list(tmp[feat])
                itemVal.append(val)
            featureValues.append(itemVal)
        ret = {'featureLabels':featureLabels, 'itemLabels':itemLabels, 'featureValues':featureValues}
        return ret

    def read_wide_format(self, CSVFileName, delimiter=";", decode=True, convention="english"):
        """ Raw decoding of the melfeature CSV files into itemLabels, featureLabels, and features
        Args:
            CSVFileName (string): Absolute filename of CSV file
            delimiter: Delimiter character in melfeature file
        Returns:
            data (dict): Raw data with keys
              'itemLabels' (list of strings): List of item labels
              'featureLabels' (list of strings): List of feature labels
              'featureValues' (list): List of item-wise features values, which themselves can be scalar numbers, strings, lists (vectors) or lists of lists (matrices)
        """
        with open(CSVFileName, 'r') as csvfile:
            content = csv.reader(csvfile, delimiter=delimiter)
            itemLabels = []
            features = []
            # row-wise decoding
            for rowCount, row in enumerate(content):
                if rowCount == 0:
                    # header line contains feature labels
                    featureLabels = row[1:]
                else:
                    # other lines have itemlabels with corresponding feature values
                    itemLabels.append(row[0])
                    currFeatures = []
                    # convert feature strings to float if possible
                    for feat in row[1:]:
                        #print "Reading feat", feat
                        currFeatures.append(self.read_field(feat, decode=decode, convention=convention))
                    features.append(currFeatures)

        # sanity check
        nFeatLabels= len(featureLabels)
        for i in range(len(features)):
            if len(features[i]) != nFeatLabels:
                raise Exception("item ", i, ", features read: ", len(features[i]), " expected: ", nFeatLabels)


        ret = {'featureLabels':featureLabels, \
                'itemLabels':itemLabels, \
                'featureValues':features}
        #print ret
        return ret
    def comparison_value_with_reference_value(self, val, op, refVal):
        """ Evaluates feature value relationship
        Args:
            val: Feature value
            op: comparison operator (see below)
            refVal: reference Value
        Return:
            Comparison result (bool)
        """
        try:
            if op == "in":
                return val in refVal
            elif op == ">":
                return val > refVal
            elif op == ">=":
                return val >= refVal
            elif op == "<":
                return val < refVal
            elif op == "<=":
                return val <= refVal
            elif op == "=":
                return val == refVal
#             elif op == "matches":
#                 #TODO: implement this for matching of strings to regular expression!
#                 raise Exception("This must still be implemented!!!")
        except:
            raise Exception("Non valid syntax for value-with-reference-value-comparision!!")


    def get_item_IDs_from_selection(self, data, select):
        """ Obtains list of item IDs of a dataset that match a given item grouping (see group_items_and_select_features() for details)
        Args:
            data: Dataset dict (see group_items_and_select_features())
            select: Grouping selection - either dictionary (a) or list (b)
                a) e.g.
                     {"op":"&",
                         "set1":["MAKE_UP_METADATA.collection", "=", "ALTDEUTSCH"],
                         "set2":["MAKE_UP_METADATA.year", ">", 1952]
                      }
                   -> this recursively calls the same function for "set1" and "set2" with the following three-element-list to obtain
                      item IDs for both sets and finally combine both sets using the operation given by "op" (see below for possible options)
                b) e.g.
                     ["MAKE_UP_METADATA.year", ">", 1952]
                   -> this finds all items with the values of the feature "MAKE_UP_METADATA.year" greater than 1952
        Returns:
            List of item IDs that match the item grouping
        """

        if isinstance(select, dict):
            try:
                # operation to combine sets
                op = select["op"]
                # recursive function call for all sets that are defined
                groupKeys = [k for k in list(select.keys()) if k.find("set") >= 0]
                sets = []
                for key in groupKeys:
                    newSet = set(self.get_item_IDs_from_selection(data, select[key]))
                    if len(newSet) == 0:
                        print("Could not find item for set ", select[key])
                    sets.append(newSet)
                # perform operation to combine sets
                if op == "&":
                    # intersection (and)
                    return set.intersection(*sets)
                elif op == "|":
                    # union (or)
                    return set.union(*sets)
                elif op == "-":
                    # difference (not)
                    return set.difference(*sets)
                elif op == "^":
                    # symmetric difference (xor)
                    return set.symmetric_difference(*sets)
                else:
                    raise Exception("Operator " + op + " is not valid!")
            except:
                raise Exception("Non-valid syntax for select dict!")
        else:
            try:
                # get feature index
                featIdx = data["featureLabels"].index(select[0])
                # find all items that fullfill condition
                nItems = len(data["itemLabels"])
                return [i for i in range(nItems) if self.comparison_value_with_reference_value(data["featureValues"][i][featIdx], select[1], select[2])]
            except:
                raise Exception("Cannot find feature " + select[0] + " in list of available features!")




    def group_items_and_select_features(self,data,groups=None,selectFeatures=None, removeFeatures=None):
        """
        Function allows to group & select items of a dataset based on (arbitrary combinations of) feature value relations
        Args:
            data (dict): Raw data with keys
              'itemLabels' (list of strings)
              'featureLabels' (list of strings)
              'featureValues' (list of item-wise feature values)
            groups (list / dict):
                *) if groups = None : No grouping will be performed and all original items will be kept
                a) if group is a list, it must have the syntax [featureLabel,operator,value]
                  - featureLabel must be a valid feature label that exists in the dataset
                  - operator can be either "in"
                                         (e.g. groups = ["year","in",[1955,1956,1957]] or
                                               groups = ["artist","in",["Miles Davis", "John Coltrane"]])
                                    or one of the relations "=","<","<=",">",">="
                                         (e.g. groups = ["year",">=",1960])
                b) if group is a dict, it allows to combine different grouping relationships (as described above), e.g.:
                groups = [{
                     "groupLabel":"Altdeutsch_After_1952",
                     "select":
                     {"op":"&",
                         "set1":["MAKE_UP_METADATA.collection", "=", "ALTDEUTSCH"],
                         "set2":["MAKE_UP_METADATA.year", ">", 1952]
                      }
                   },
                     {
                         "groupLabel":"China_Before_1940",
                         "select":
                          {"op":"&",
                           "set1":["MAKE_UP_METADATA.collection", "=", "CHINA"],
                           "set2":["MAKE_UP_METADATA.year", "<", 1940]
                     }
                   }]
                   - the operator ("op") defines how the resulting sets 1 & 2 are combined to a final set:
                       "&" (intersection)
                       "|" (union)
                       "-" (difference)
                       "^" (symmetric difference)
                   - "set1" and "set2" are defined as explained in a), in general, an arbitrary number of groups (e.g. "set3" etc.) are possible
           selectFeatures: List of features to be selected (default = None -> all features are selected)
           removeFeatures: List of features to be excluded (default = None -> all features are selected)
       Returns:
           data (dict): Data with selected / grouped items and selected features
                -> the dict has the following additional keys:
             'groupLabels' : List of group labels
             'itemGroupID' : List of group ID values for each item
        """
        # item selection / grouping
        if groups is not None:
            groupLabels = []
            itemIdxInGroups = []
            for group in groups:
                # store group label
                groupLabels.append(group["groupLabel"])
                try:
                    # store item indices assigned to that group
                    itemIdxInGroups.append(list(self.get_item_IDs_from_selection(data, group["select"])))
                except:
                    print("No items found for group ", group["groupLabel"], ". Group will be ignored ...")
                    itemIdxInGroups.append([])
            data["groupLabels"] = groupLabels

            # check that no items are assigned to multiple groups
            allItemIdxInGroups = []
            for i in range(len(itemIdxInGroups)):
                for k in range(len(itemIdxInGroups[i])):
                    try:
                        allItemIdxInGroups.index(itemIdxInGroups[i][k])
                        # if no exception was thrown -> item is already assigned to another group
                        raise Exception("Item #" + itemIdxInGroups[i][k] + " is assigned to more than one group -> Item grouping is ambiguous!")
                    except:
                        allItemIdxInGroups.append(itemIdxInGroups[i][k])

            # get group ID for each item
            groupID = []
            for i in range(len(data["itemLabels"])):
                ID = -1
                for g in range(len(itemIdxInGroups)):
                    try:
                        itemIdxInGroups[g].index(i)
                        ID = g
                        continue
                    except:
                        pass
                groupID.append(ID)

            # remove all items which are assigned to no group
            data["featureValues"] = [data["featureValues"][i] for i in range(len(data["featureValues"])) if groupID[i] > -1]
            data["itemLabels"] = [data["itemLabels"][i] for i in range(len(data["itemLabels"])) if groupID[i] > -1]
            data["itemGroupID"] = [groupID[i] for i in range(len(groupID)) if groupID[i] > -1]
        else:
            # consider each item to be a group
            data["groupLabels"] = data["itemLabels"]
            data["itemGroupID"] = [i for i in range(len(data["itemLabels"]))]

        # select & exclude features
        nFeat = len(data["featureLabels"])
        featureLabelsIdx2Select = self.select_and_remove_items(data["featureLabels"], selectFeatures, removeFeatures)
        if len(featureLabelsIdx2Select) < nFeat:
            nFeat2Select = len(featureLabelsIdx2Select)
            if len(featureLabelsIdx2Select) == 0:
                raise Exception("No feature remains!")
            nItems = len(data["featureValues"])
            data["featureValues"] = [[data["featureValues"][i][featureLabelsIdx2Select[d]] for d in range(nFeat2Select)] for i in range(nItems)]
            data["featureLabels"] = [data["featureLabels"][featureLabelsIdx2Select[i]] for i in range(nFeat2Select)]

        return data

    def select_and_remove_items(self, allItems, items2Select=None, items2Remove = None):
        """ Selects and removes items from a given list of items and returns indices of remaining items
        Args:
            allItems (list): List of items
            items2select (list): Items to be selected
            items2remove (list): Items to be removed
        Returns:
            List of indices of the remaining items in the list of original items (allItems)
        """
        if items2Select is None:
            itemIdx2Select = list(range(len(allItems)))
        else:
            itemIdx2Select = [i for i in range(len(allItems)) if allItems[i] in items2Select]
        if items2Remove is None:
            itemIdx2Exclude = []
        else:
            itemIdx2Exclude = [i for i in range(len(allItems)) if allItems[i] in items2Remove]

        # remove list of items to be excluded from the list of items to be kept to get final list of items
        return list(set(itemIdx2Select) - set(itemIdx2Exclude))

    def read(self, CSVFileName):
        ''' Reads CSV file with feature values (generated by melfeature)

        Args:
            CSVFileName (string): Absolute filename of CSV file
        Returns:
            data (dict): Raw data dictionary with fields
                            'itemLabels': List with item labels (from SV file names)
                            'featureLabels': List with feature labels
                            'features': 2D List with raw unformatted features

        '''
        with open(CSVFileName, 'rb') as csvfile:
            content = csv.reader(csvfile, delimiter=';')
            rowCount = 0;
            itemLabels=[]
            features = []
            for row in content:
                # header line
                if rowCount == 0:
                    featureLabels = row[1:]
                    for i in range(len(featureLabels)):
                        featureLabels[i] = featureLabels[i][featureLabels[i].find('_')+1:]
                # feature lines
                else:
                    itemLabels.append(row[0])
                    featRow = []
                    for i in range(1, len(row)):
                        try:
                            # check if feature is matrix
                            row[i].index(':')
                            rowMatRows = re.split(":", row[i])
                            feat = []
                            for k in range(len(rowMatRows)):
                                dummy = re.split(",", rowMatRows[k])
                                feat.append([float(s) for s in dummy])
                            featRow.append(feat)
                        except ValueError:
                            # check if feature is vector
                            try:
                                row[i].index(',')
                                dummy = re.split(",", row[i])
                                feat = [float(a) for a in dummy]
                                featRow.append(feat)
                            except ValueError:
                                if row[i] == "N/A":
                                    featRow.append(float('NaN'))
                                else:
                                    try:
                                        featRow.append(float(row[i]))
                                    except ValueError:
                                        # bug: if row[i] is of syntax "[1.]"
                                        try:
                                            i1 = row[i].index('[')
                                            i2 = row[i].index(']')
                                            featRow.append(float(row[i][i1+1:i2]))
                                        except:
                                            raise Exception("Non valid format for float conversation!")
                            # feature is scalar -> just append it
                    features.append(featRow)
                rowCount += 1

            # remove SV file parts
            for i in range(len(itemLabels)):
                itemLabels[i] = itemLabels[i].replace("_PREFINAL.sv", "")
                itemLabels[i] = itemLabels[i].replace("_FINAL.sv", "")

            # decode artist and solo label from item label
            itemLabelsArtist, itemLabelsSolo = self.decode_item_labels(itemLabels)

        return {'itemLabels':itemLabels, \
                'itemLabelsArtist':itemLabelsArtist, \
                'itemLabelsSolo':itemLabelsSolo, \
                'featureLabels':featureLabels,\
                'features':features}

    def prepare_data_for_scikit_learn(self,data,featureNames,grouping="artist",removeNaNandInfFeatures=False,removeNaNandInfItems=False):
        """ Extracts feature matrix, class ids, and class labels from raw data dict from melfeature CSV results files.

        Args:
        {"category":"artist","old":{"MilesDavis","CharlieParker"},"new":{"SteveColeman","JoshuaRedman"}}
            data: Raw data obtained from read() function
            featureNames: List of feature names to be included into the feature matrix
            grouping: Item-to-class grouping, possible values:

              1) "artist" -> all files are grouped based on artist,

              2) "solo" -> all files are grouped based on solo name

              3) individual assignment between solo/artist to classes using this syntax:
                a) grouping = {"ClassLabel1":[["Artist1",["Solo1","Solo2"]],
                                             ["Artist2",["Solo3","Solo4"]]],
                              "ClassLabel2":[["Artist3",["Solo5","Solo6"]],
                                             ["Artist4",["Solo7","Solo8"]]]}

                     -> this would assign the selected solos from the selected artists to both classes

                b) grouping = {"ClassLabel1":[["Artist1"],
                                             ["Artist2"]],
                              "ClassLabel2":[["Artist3",["Solo5","Solo6"]],
                                             ["Artist4",["Solo7","Solo8"]]]}

              4) "esac" -> Special behaviour for the Esac database -> "itemLabelArtist" contains signatures such as "Z0083" with the first letter indicating the
                           source collection -> the grouping is performed into different collections
                 -> this would assign all solos from artist 1 & 2 to the first class but only the given solos of artist 3 & 4 to the second class

            removeNaNandInfFeatures: Switch to remove those features from the data with NaN or Inf values
            removeNaNandInfItems: Switch to remove those items from the data with NaN or Inf values
        Return:
            X (2D numpy array): Feature matrix (nItems, nFeatures)
            y (1D numpy array): Class IDs for all items
            classLabels: Labels of all classes
        TODO:
            - make sure that items are not accidentaly assigned to different classes
        """

        # features to be used
        availFeatureNames = data["featureLabels"]
        featureIdx2Select = []
        for feature in featureNames:
            try:
                featureIdx2Select.append(availFeatureNames.index(feature))
            except:
                print("Could not find feature ", feature, "in given dataset!")

        # construct feature matrix
        X = data["features"]

        # get gr
        availArtists = data["itemLabelsArtist"]
        availSolos = data["itemLabelsSolo"]

        # remove subsections, e.g. convert "Serenity.chorus.5" - > "Serenity"
        availSolosNew = []
        for solo in availSolos:
            try:
                availSolosNew.append(solo[:solo.index('.')])
            except:
                availSolosNew.append(solo)
        availSolos = availSolosNew

        check = ["artist", "solo"]
        fields = ["itemLabelsArtist", "itemLabelsSolo"]
        y = []

        if grouping == "esac":
            # remove
            firstChar = [i[0] for i in data["itemLabelsArtist"]]
            classLabels = self.string_vec_unique(firstChar)
            y = [classLabels.index(fc) for fc in firstChar]

        else:
            try:
                # get the item class names according to the grouping criteria
                itemClassLabels = data[fields[check.index(grouping)]]
                # unique entries are the class names
                classLabels = self.string_vec_unique(itemClassLabels)
                # get class ids
                y = [classLabels.index(c) for c in itemClassLabels]
            except:
                try:
                    classLabels = list(grouping.keys())
                    idxItemsInClass = []
                    for i, c in enumerate(classLabels):
                        classArtistSolo = grouping[c]
                        nArtists = len(classArtistSolo)
                        for a in range(nArtists):
                            artist = classArtistSolo[a][0]
                            allSolos = len(classArtistSolo[a]) == 1
                            if not allSolos:
                                # select specific solos of that artist
                                nSolos = len(classArtistSolo[a][1])
                                for s in range(nSolos):
                                    solo = classArtistSolo[a][1][s]
                                    try:
                                        checkArtist = [availArtist == artist for availArtist in availArtists]
                                        checkSolo = [availSolo == solo for availSolo in availSolos]
                                        check = [ca and cs for ca, cs in zip(checkArtist, checkSolo)]
                                        try:
                                            idxItemsInClass.append(check.index(True))
                                            y.append(i)
                                        except:
                                            print(artist, " - ", solo, " not found!!!")
                                    except ValueError:
                                        print("Solo")
                            else:
                                # select all solos of this artist
                                checkArtist = [availArtist == artist for availArtist in availArtists]
                                try:
                                    newIdx = [i for i in range(len(check)) if check[i] == True]
                                    for idx in newIdx:
                                        idxItemsInClass.append(idx)
                                    y.append(i)
                                except:
                                    print(artist, " not found!!!")

                    X = [X[i] for i in idxItemsInClass]
                except:
                    raise Exception("Non-valid syntax of parameter grouping!")

        # TODO there must be a more efficient way to do this.
        X = np.array(X)
        X = X.T
        X = X[featureIdx2Select]
        X = X.T

        # remove NaN and Inf
        if removeNaNandInfFeatures:
            X = X.T
            nItems = X.shape[0]
            validIdx = [idx for idx in range(nItems) if ( not np.isnan(np.min(X[idx])) and not np.isinf(np.min(X[idx])) )]
            X = X[validIdx]
            X = X.T

        if removeNaNandInfItems:
            nItems = X.shape[0]
            validIdx = [idx for idx in range(nItems) if ( not np.isnan(np.min(X[idx])) and not np.isinf(np.min(X[idx])) )]
            X = X[validIdx]
            y = [y[i] for i in validIdx]

        return X, y, classLabels

    def find_item_IDs_for_classes(self, itemLabels, itemsInClasses):
        itemIDsInClasses = []
        nClasses = len(itemsInClasses)
        for c in range(nClasses):
            currItemIDsInClass = []
            for i in range(len(itemsInClasses[c])):
                try:
                    currItemIDsInClass.append(itemLabels.index(itemsInClasses[c][i]))
                except:
                    print(itemsInClasses[c][i], " not found!!!")
            itemIDsInClasses.append(currItemIDsInClass)
        return itemIDsInClasses


    def read2(self,CSVFileName, delimiter = ";"):
        '''
        Method to read CSV file
        Returns dictionary with raw data
        'itemLabels': List with item labels (from SV file names)
        'featureLabels': List with feature labels
        'features': 2D List with raw unformatted features
        '''
        with open(CSVFileName, 'rb') as csvfile:
            content = csv.reader(csvfile, delimiter=';')
            rowCount = 0;
            itemLabels=[]
            features = []
            for row in content:
                # header line
                featureValues = {}
                if rowCount == 0:
                    featureLabels = row[1:]
                    for i in range(len(featureLabels)):
                        featureLabels[i] = featureLabels[i][featureLabels[i].find('.')+1:]
                # feature lines
                else:
                    itemLabels.append(row[0])
                    featRow = []
                    for i in range(1, len(row)):
                        featureValues[featureLabels[i-1]] = self.read_field(row[i])
                    features.append(featureValues)
                rowCount += 1
            # remove SV file parts
            for i in range(len(itemLabels)):
                itemLabels[i] = itemLabels[i].replace("_PREFINAL.sv", "")
                itemLabels[i] = itemLabels[i].replace("_FINAL.sv", "")

            # decode artist and solo label from item label
            itemLabelsArtist, itemLabelsSolo = self.decode_item_labels(itemLabels)

        return {'itemLabels':itemLabels, \
                'itemLabelsArtist':itemLabelsArtist, \
                'itemLabelsSolo':itemLabelsSolo, \
                'featureLabels':featureLabels,\
                'featureValues':features}

    def getFeatureMatrix(self, fnCSV):
        """ Returns feature matrix as 2D np.ndarray. Items that have too few feature dimensions are discarded
        Args:
            fnCSV: melfeature result file
        Return:
            featMat: 2D np.ndarray with feature matrix (nItems x nFeatures)
            validItems np.ndarray with valid feature dimensions of original feature matrix
            labels: Feature dimension labels
            """

        data = self.read_raw(fnCSV)
        features = data["featureValues"]
        X = []

        # read features vector & feature dimensions
        Xraw = []
        Xdim = []
        labels = []
        nItems = len(features)
        for i in range(nItems):
            xdim = []
            xraw = []
            xlabels = []
            # create 1D list (merge multi- and one-dimensional feature vectors)
            for m in range(len(features[i])):
                currFeat = features[i][m]
                if isinstance(currFeat, list):
                    L = len(currFeat)
                    xraw += currFeat
                    xlabels += [data["featureLabels"][m]+'_'+str(k+1) for k in range(L)]
                else:
                    xraw.append(currFeat)
                    xlabels.append(data["featureLabels"][m])
            # replaces N/A with nan
            for i in range(len(xraw)):
                try:
                    if xraw[i] == 'N/A':
                        xraw[i] = float('nan')
                except:
                    pass
            labels.append(xlabels)
            Xraw.append(xraw)

        # find valid items (with right feature vector length)
        featVecLen = [len(x) for x in Xraw]
        nDim = max(featVecLen)
        validItems = [i for i in range(nItems) if featVecLen[i]==nDim]

        # feature dimension labels
        labels = labels[validItems[0]]

        # generate feature matrix from valid items
        Xraw = [Xraw[validItems[i]] for i in range(len(validItems))]

        return np.array(Xraw, dtype='float'), np.array(validItems), labels

    def read_feature_column_from_raw_data(self, data, featureName):
        """ Returns feature values for given feature from raw matrix as list
        Args:
            data: Raw data dict (from read_raw() )
            featureName: Feature name
        Returns:
            featureValues: List with feature values
        """
        index = [_ for _ in range(len(data["featureLabels"])) if data["featureLabels"][_]==featureName][0]
        return [data["featureValues"][_][index] for _ in range(len(data["featureValues"]))]


    def convert_feature_matrix_to_numpy_array(self, mat):
        for i1 in range(len(mat)):
            for i2 in range(len(mat[i1])):
                if mat[i1][i2] in ('N/A', 'nan', 'NA'):
                    mat[i1][i2] = float('NaN')
                else:
                    try:
                        mat[i1][i2] = float(mat[i1][i2])
                    except:
                        mat[i1][i2] = float('NaN')
        return np.array(mat)
