__version__ = "1.1.0.1000"
import argparse
import csv
import os
import sys
import time
from os.path import expanduser

import numpy as np
import pandas as pd
import yaml
from pandas import DataFrame

import melospy.basic_representations.jm_util as jm_util
from melospy.basic_representations.config_param import *
from melospy.basic_representations.melody_cutter import *
from melospy.basic_representations.metrical_annotation_param import FlexQParams
from melospy.feature_machine.feature_machine_main import FeatureMachine
from melospy.input_output.esac_reader import *
from melospy.input_output.mcsv_reader import *
from melospy.input_output.mel_db_sqlite3_adapter import *
from melospy.input_output.melody_importer import *
from melospy.input_output.read_sv_project import *
from melospy.tools.commandline_tools.param_helper import *

separators = {'English':{'dec': '.', 'sep':';', 'col_sep':',', 'row_sep':':'},
              'Continental': {'dec': ',', 'sep':';', 'col_sep':':', 'row_sep':'|'}
             }

class FeatureExtractor(object):

    def __init__(self, params, src_dbi, dir_paths_params):
        self.params          = params
        self.wdir            = dir_paths_params.get("wdir")
        self.outdir          = self._outdir(dir_paths_params.get("outdir"))
        self.outfile         = params.get("outfile")
        self.feature_dir     = dir_paths_params.get("feature_dir")
        self.tunes           = params.get("tunes")
        self.segmentations   = params.get("segmentations")
        self.features        = params.get("features")
        self.convention      = params.get("convention")
        self.shortnames      = params.get("shortnames")
        self.wide_format     = params.get("wide_format")
        self.split_ids       = params.get("split_ids")
        self.NA_str          = params.get("NA_str")
        self.precision       = params.get("precision")
        #self.dummy_phrases   = params.get("add_dummy_phrases")
        self.song_cache      = {}
        self.src_dbi         = DBInfo.fromDict(src_dbi.as_dict())
        self.results         = []

        self.melody_importer_params = parse_melody_importer_params(params)
        self.use_cache       = self.melody_importer_params["melody_importer"].getValue("use_cache")

        if self.convention.lower()[0:3]  in ['ger', 'de', 'deu', 'con', 'fre']:
            self.convention = 'Continental'
        else:
            self.convention = 'English'
        self.dec             = separators[self.convention]["dec"]
        self.sep             = separators[self.convention]["sep"]
        self.col_sep         = separators[self.convention]["col_sep"]
        self.row_sep         = separators[self.convention]["row_sep"]


        #self.features, self.labels = self._prepare_feature_list()
        try:
            self.features, self.labels = self._prepare_feature_list()
        except Exception as e:
            raise RuntimeError("Invalid or missing features: {}".format(e))

        if self.outfile:
            self.outfile = prepend_path(self.outdir, self.outfile)
        else:
            raise RuntimeError("Missing result file!")

    def _outdir(self, outdir_param):
        if "%(home_dir)s" in outdir_param:
            return outdir_param % {"home_dir": expanduser("~")}
        return outdir_param

    def num_features(self):
        if self.split_ids == True:
            offset = 3
        else:
            offset = 1
        if self.results:
            return len(self.results[0])-offset
        return 0

    def num_entries(self):
        return len(self.results)

    def clearCache(self):
        self.song_cache = {}

    def process(self, write=False, proc_func=None, verbose=False):
        """main processing routine"""
        start = time.process_time()
        #clear all results
        self.results = []

        if verbose is None:
            try:
                verbose = self.params.get("verbose")
            except:
                verbose = False
        #importer_params = None

        #if self.dummy_phrases:
        #    importer_params = MIDIReaderParams(add_dummy_phrases=True)
        #else:
        #    importer_params = ConfigParameter()

        #importer_params.setValue("samples", self.samples)
        #importer_params.setValue("seed", self.seed)
        #importer_params.setValue("use_cache", self.use_cache)
        try:
            import_hook = proc_func["import"]
        except:
            import_hook = jm_util.void
        try:
            feature_hook = proc_func["feature"]
        except:
            feature_hook = jm_util.void

        mi = MelodyImporter(self.tunes,
                            self.wdir,
                            self.src_dbi,
                            params=self.melody_importer_params,
                            proc_hook=import_hook)
        if self.use_cache:
            mi.cache = self.song_cache
            #print "Cache len FE", len(self.song_cache)

        fetcher = mi.fetcher(verbose=verbose)
        ni = mi.getNumberItems()
        if ni == 0:
            if verbose:
                print("Nothing to process.")
            else:
                print("...")
            return 0, 0, 0

        mel = None
        i = -1
        nError = 0
        #print "melfeature_wrapper", self.segmentations
        mc = MelodyCutter(segmentations=self.segmentations, verbose=verbose)
        while True:
            #print "Start loop"
            i += 1
            try:
                filestart = time.process_time()
                mel = next(fetcher)
                #print mel.metadata
                #filename = mel.getMetadata().getTranscriptionInfo().filenamesv
                #print mel.getChordSections()
                filename = mi.tunes[mi.last_read_idx]
                if mel is None:
                    #offending_files.append((mi.tunes[i], "Invalid melody object"))
                    if verbose:
                        print("Error reading tune: {}".format(filename))
                    nError += 1
                    if feature_hook:
                        feature_hook(i, ni, filename, verbose, True)
                    continue
                if verbose:
                    print("="*60)
                    print("Read {} in {} s".format(filename, round(time.process_time()-filestart, 3)))
                filestart = time.process_time()
            except StopIteration:
                #print "StopIteration.."
                break
            #cutting melodies according to segmentations
            #mc.melody = mel
            #mel_list = mc.cut()
            try:
                mc.melody = mel
                mel_list = mc.cut()
            except Exception as e:
                #continue
                raise RuntimeError("Could not cut melody. Reason: {}".format(e.args[0]))
            #print len(mel)

            #calculate features
            feature_modules= []
            filestart = time.process_time()
            for j in range(len(self.features)):
                try:
                    feature_file = self._qualify_feature_file(self.features[j])
                    feature_modules.append(FeatureMachine().createFeatureFromYAMLFile(feature_file))
                except Exception as e:
                    raise Exception("Error parsing feature file '{}': {}".format(self.features[j], str(e)))
            
            self._calc_feature(filename, 
                               feature_modules, 
                               mel_list, 
                               verbose=verbose)

            if verbose:
                print("... done in {} s".format(round(time.process_time()-filestart, 3)))
            if feature_hook:
                feature_hook(i, ni, filename, verbose, False)

        if verbose:
            if i == 0:
                print("No features processed.")
            else:
                print("Successfully processed features in {} s".format(round(time.process_time()-start, 3)))
        #self.results_to_dataframe()

        if write:
            self.write_features(self.wide_format, verbose=verbose)
            if verbose:
                print("Written features to {}".format(self.outfile))

        if self.use_cache:
            self.song_cache = mi.cache
            #print "Cache len FE", len(self.song_cache)
        return i, nError, time.process_time()-start,
        #print "Results: ", len(self.results)
        #print "Line-length:", len(self.results[0])

    def _analyse_results(self, row):
        if len(self.results) == 0:
            raise RuntimeError("No results to convert!")
        ret = []
        matrices = []
        longest = 0
        #max_l = 0

        for i in range(1, len(row)):
            t = type(row[i])
            try:
                l = len(row[i])
            except:
                l = 1
            if isinstance(row[i], str):
                l = 1
            try:
                dim = len(np.shape(row[i]))
                if  dim > 1:
                    matrices.append(i)
            except:
                dim = 0
            ret.append({"idx": i, "type":t, "dim": dim, "len": l})
        ret = sorted(ret, key= lambda x: x["len"], reverse=True)
        longest = ret[0]["idx"]
        max_len = ret[0]["len"]
        return ret, longest, max_len, matrices

    def results_to_dataframe(self, padding="right"):
        #print "Enter results_to_dataframe"
        #sys.exit(-1)
        if len(self.results) == 0:
            raise RuntimeError("No results to convert!")

        labels = self.labels
        if self.shortnames:
            labels = [v.split(".")[1] for v in self.labels]


        #check for matix values featrues
        types, longest, max_len, matrices = self._analyse_results(self.results[0])
        if len(matrices) > 0:
            raise RuntimeError("Matrix features not available in long format yet")

        ret = []
        start = time.process_time()
        for row in self.results:
            #print "Converting {}".format(row[0])
            types, longest, max_len, matrices = self._analyse_results(row)
            #print "Types", types
            #print "longest: ", longest#, len(types[longest])
            try:
                l = len(row[longest])
            except:
                l = 1
            #print row[longest], type(row[longest]), l
            #print "length", l

            #start1 = time.process_time()
            if self.split_ids and len(self.segmentations)>0:
                ids = self._split_id(row[0])
                df = DataFrame({"id": [ids[0]]*l})
                df["seg_type"]=[ids[1]]*l
                df["seg_id"] = [ids[2]]*l
                #df = DataFrame({labels[longest-1] : row[longest]}, index=range(l))
            else:
                df = DataFrame({"id": [list(row)[0]]*l})
            #print "Initialised {} DataFrames in {} s".format(len(ret)+1, round(time.process_time()-start1,3))
            #print "Longest", longest, max_len
            #start2 = time.process_time()
            for var_def in types:
                #print var_def
                var_idx = var_def["idx"]
                #print "Var idx", var_idx, labels[var_idx-1]
                #if var_idx == longest:
                #    continue
                tmp = row[var_idx]
                #print "len(tmp) = {}, tmp: {}".format(len(tmp), tmp)
                if var_def["len"] > 1 and var_def["len"] <max_len:
                    right = padding == "right"
                    tmp = jm_util.pad_list(tmp, np.nan, max_len, right)
                #sometimes vectors have only one element,
                #make them a scalar
                if var_def["len"] == 1 and var_def["dim"] > 0:
                    tmp = tmp[0]
                if var_def["len"] == 0 and var_def["dim"] > 0:
                    tmp = None

                #if var_def["len"] > 1:
                #    print len(tmp), max_len
                #else:
                #    print 1, max_len
                #print type(first_row[var_idx])
                start4 = time.process_time()
                df[labels[var_idx-1]] = tmp
                #print "Added '{}' column to df in {} s".format(labels[var_idx-1], round(time.process_time()-start4,3))
                #print len(df.index)
                #print self.labels[var_idx-1], first_row[var_idx]
            #print df
            #print "Added '{}' columns to df in {} s".format(len(types), round(time.process_time()-start2,3))
            ret.append(df)
            #print "Appended dataframe to list in {} s".format(round(time.process_time()-start2,3))
        #print "Generated {} DataFrames in {} s".format(len(ret), round(time.process_time()-start,3))
        #start = time.process_time()
        df = pd.concat(ret)
        #print "Concatenated {} DataFrames in {} s".format(len(ret), round(time.process_time()-start,3))

        #print "Created DataFrame with {} rows".format(len(df.index))
        #df[self.labels[longest]] = first_row[longest]
        return df

    def write_features(self, wide_format=False, outfile=None, verbose=False):
        if wide_format:
            self.write_features_wide(outfile)
        else:
            self.write_features_long(outfile)
            try:
                pass
                #self.write_features_long(outfile)
            except:
                if verbose:
                    print("Matrix valued features not supported in long mode. Trying wide format.")
                self.write_features_wide(outfile)


    def write_features_long(self, outfile=None):
        """Write the results to a file in long formar"""
        if len(self.results) == 0:
            raise RuntimeError("No results to write!")
        #start = time.process_time()
        df = self.results_to_dataframe()
        #print "Converted results to pandas.DataFrame in {} s".format(round(time.process_time()-start,3))

        if outfile is None:
            outfile = self.outfile

        if self.outdir != ".":
             ensure_dir(self.outdir)
        #df["onset"][0] = None
        #mf =  list(df["f0_mod_range_cents"])
        #mf =  list(df["onset"])
        #print mf
        #print "\n".join([str(type(e)) for e in mf])
        df.to_csv(outfile,
                  sep=";",
                  decimal=self.dec,
                  index=False,
                  na_rep=self.NA_str, 
                  encoding='utf-8')

    def write_features_wide(self, outfile=None):
        """Write the results to a file in wide format"""
        if len(self.results) == 0:
            raise RuntimeError("No results to write!")

        if outfile is None:
            outfile = self.outfile

        if self.outdir != ".":
             ensure_dir(self.outdir)

        if self.split_ids and len(self.segmentations)>0:
            header = ["id", "seg_type", "seg_id"]
        else:
            header = ["id"]

        if not self.shortnames:
            header = header + self.labels
        else:
            header = header + [v.split(".")[1] for v in self.labels]

        header = self.sep.join(header)

        with open(outfile, 'w') as csvfile:
            csvfile.write(header+"\n")

        with open(outfile, 'a') as csvfile:
            csvwriter = csv.writer(csvfile, delimiter=self.sep, lineterminator="\n", quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for rows in self.results:
                if self.split_ids and len(self.segmentations)>0:
                    line = self._split_id(rows[0])
                else:
                    line = [rows[0]]
                for i in range(1, len(rows)):
                    entry = str(self._makeEntry(rows[i]))
                    try:
                        entry = str(self._makeEntry(rows[i]))
                        line.append(entry)
                    except:
                        line.append(self.NA_str)
                csvwriter.writerow(line)

    def _calc_feature(self, filename, feature_modules, melody_list, verbose=False):
        if verbose:
            print("Featuring...")

        sinkModuleValues = dict()

        for mel in melody_list:
            #melody_list contains tuples of the form
            #(melody object, segmentation_name)
            for j in range(len(feature_modules)):
                if mel[0] != None and len(mel[0]) == 0:
                    if verbose:
                        print("Melody segment empty, skipping.")
                    continue
                #out of try
                #feature_modules[j].process(mel[0])
                try:
                    feature_modules[j].process(mel[0])
                except Exception as e:
                    if verbose:
                        print("Feature failed, skipping.\nReason: " + str(e.args[0]))
                    continue
                prefix = self.features[j] + "."
                sinkModuleValues.update(prepend_to_keys(feature_modules[j].getSinkModuleValues(), prefix))
                #print prepend_to_keys(feature_modules[j].getSinkModuleValues(), prefix)

            seg_name = mel[1]
            result = []

            if seg_name != "":
                result = ["{}.{}".format(filename, seg_name)]
            else:
                result = [filename]

            for l in self.labels:
                try:
                    result.append(sinkModuleValues[l])
                except Exception as e:
                    if verbose:
                        print("Could not find feature '{}' in sink".format(l))
                    result.append(self.NA_str)
            self.results.append(result)

    def _makeEntry(self, val):
        # print "-"*15
        #print "val: ",val
        #print type(val)
        #print "Val {}".format(val)
        #print "Size {}".format(np.size(val))
        #
        if isinstance(val, str):
            return val
        if isinstance(val, np.int32):
            return val
        if isinstance(val, (float, int, np.int32, np.float)):
            val = str(round(val, self.precision))
            val = val.replace(".", self.dec)
            return val
        if isinstance(val, np.ndarray) or isinstance(val, list) or isinstance(val, tuple):
            if isinstance(val, np.ndarray):
                n     = np.size(val)
                shape = np.shape(val)
                dim   = len(shape)
            else:
                n = len(val)
                dim = 1
                shape = (1,)

            if dim > 2:
                raise RuntimeError("U CRAZY BITCH, NO TENSORS PLEASE!")

            if n > 1:
                tmp = []
                if dim>1:
                    for i in range(shape[0]):
                        tmp.append(self.col_sep.join([str(v) for v in val[i]]))
                    val = self.row_sep.join(tmp)
                    #print "FINAL val dim 2", val
                else:
                    val = self.col_sep.join([str(v) for v in val])
                    #print "FINAL val dim <2", val
            elif n == 0:
                return self.NA_str
            else:
                if dim == 0:
                    val = str(val)
                else:
                    val = str(val[0])

            val = val.replace(".", self.dec)
            return val
        #if isinstance(val, Chord) or isinstance(val, Key) or isinstance(val, Signature) or isinstance(val, FormDefinition) or isinstance(val, FormPart)
        try:
            s = str(val)
            return s
        except:
            pass
        return self.NA_str

    def _qualify_feature_file(self, feature_file_base):
        if not feature_file_base.endswith(".yml"):
            feature_file_base = feature_file_base + ".yml"
        feature_file_base = prepend_path(self.feature_dir, feature_file_base)
        return feature_file_base

    def _parse_feature_labels(self, featurefiles):
        labels = []
        for i in range(len(featurefiles)):
            feature_file = self._qualify_feature_file(featurefiles[i])
            with open(feature_file, 'r') as featurefile:
                yml = yaml.load(featurefile)
                for k in list(yml['feature']['sink'].keys()):
                    #labels.append(pre + yml['feature']['sink'][k]['label'])
                    labels.append(yml['feature']['sink'][k]['label'])
        return labels

    def _parse_label_list(self, labels):
        ret = []
        nNeg = 0
        for l in labels:
            if len(l) == 0:
                continue
            if l[0] == "~" or l[0] == "-":
                ret.append((l[1:], False))
                nNeg += 1
            else:
                ret.append((l, True))
        if nNeg>0:
            ret = [v[0] for v in ret if not v[1]]
        else:
            ret = [v[0] for v in ret if v[1]]
        return ret, nNeg>0

    def _prepare_feature(self, f):
        tmp_labels = []
        if isinstance(f, dict):
            feature_file = list(f.keys())[0]
            tmp_labels = f[feature_file].split(",")
        else:
            feature_file = f.split(":")[0]
            try:
                tmp_labels = f.split(":")[1].split(",")
            except:
                pass

        if len(tmp_labels)==0:
            labels = self._parse_feature_labels([feature_file])
        else:
            tmp_labels = [chomp(v) for v in tmp_labels]
            labels, is_neg_list = self._parse_label_list(tmp_labels)
            if is_neg_list:
                all_labels = self._parse_feature_labels([feature_file])
                labels = set(all_labels).difference(set(labels))

        prefix = feature_file + "."
        ret = [prefix + l for l in labels]
        return feature_file, ret

    def _prepare_feature_list(self):
        feature_files = []
        labels = []

        for f in self.features:
            feature_file, tmp_labels = self._prepare_feature(f)

            labels.extend(tmp_labels)
            feature_files.append(feature_file)

        return feature_files, labels

    def _split_id(self, id_s):
        el = id_s.split(".")
        if len(el) < 3:
            return [id_s, "", ""]

        first = ".".join([el[i] for i in range(len(el)-2)])
        return [first, el[-2], el[-1]]
