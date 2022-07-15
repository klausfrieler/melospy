import os
from os.path import expanduser

import pandas

from melospy.pattern_retrieval.ngram_data_provider import *
from melospy.pattern_retrieval.pattern_mining import *
from melospy.pattern_retrieval.pattern_writer import *
from melospy.tools.commandline_tools.param_helper import *


class Melpat(object):
    def __init__(self, main_params, db_params, dir_paths_params, proc_hooks=None):
        self.main_params        = main_params
        self.db_params          = DBInfo.fromDict(db_params.as_dict())
        self.db_session         = db_params.get('session')
        self.wdir               = dir_paths_params.get("wdir")
        self.outdir             = self._outdir(dir_paths_params.get("outdir"))
        self.app_name           = main_params.get('app_name')
        self.audio_slicer       = main_params.get("audio_slicer")
        self.crop_images        = main_params.get("crop_images", False)
        self.requests           = main_params.get("requests")
        self.maxN               = main_params.get("maxN")
        self.verbose            = main_params.get("verbose")
        self.outfile            = main_params.get("outfile")
        self.tunes              = main_params.get("tunes")
        self.melody_importer_params = parse_melody_importer_params(main_params)
        self.use_cache  = self.melody_importer_params["melody_importer"].getValue("use_cache")
        self.song_cache = {}
        self.ndp        = NGramDataProvider(wdir=self.wdir,
                                            tunes=self.tunes,
                                            src_dbi=self.db_params,
                                            verbose=self.verbose,
                                            params=self.melody_importer_params,
                                            proc_hooks=proc_hooks)
        self.results     = []
        self.sep         = ";"
        self.precision   = main_params.get("precision")
        self.convention  = main_params.get("convention")
        self.outfiles    = None
        # proc_hooks must be a dictionary of process hooks
        # "database": Building N-gram database (partition and database requests)
        # "partition": pattern partitions
        # "search": for pattern searches
        self.proc_hooks  = proc_hooks

    def _outdir(self, outdir_param):
        if "%(home_dir)s" in outdir_param:
            return outdir_param % {"home_dir": expanduser("~")}
        return outdir_param

    def clearCache(self):
        self.song_cache = {}

    def _is_partition(self, pattern):
        """Check if parameter defines a search or a partition
            Args:
                pattern (string):
                    parameter that defines partitions
            Returns:
                Boolean:
                    **True** if partition,
                    **False** else
        """
        if not isinstance(pattern, str):
            return False
        pt = pattern.lower()
        return pt == "*" or pt == "partition" or pt =="max" or pt == "all"

    def _itemids_by_metadata(self, mel_rep, **kwargs):
        if not mel_rep or len(mel_rep) == 0:
            return None
        ret = []
        for i, mel in enumerate(mel_rep):
            smd = mel.metadata
            found = 0
            for field, value in list(kwargs.items()):
                if smd[field] == value:
                    found += 1
                    #print "Found {} for {}:{}".format(found, field, value)
            if found == len(list(kwargs.items())):
                #print "Found {} for {}:{}".format(i, field, value)
                ret.append(i)
        return ret

    def _get_items(self, s, mel_rep):
        default_items = "0-{}".format(len(mel_rep)-1)
        items = get_safe_value_from_dict(s, "items",  default_items)
        if items == None or len(items)==0:
            items = default_items
        if not isinstance(items, list):
            items = [items]

        itemset = IntSpan()
        for item in items:
            if isinstance(item, dict):
                tmp = self._itemids_by_metadata(mel_rep, **item)
            else:
                tmp = str(item)
            itemset.add(tmp)

        return itemset

    def _patch_items(self):
        mel_rep = self.ndp.mel_rep
        for r in self.requests:
            if self._is_partition(r["pattern"]):
                r["items"] = self._get_items(r, mel_rep)

    def _read_pattern_result_file(self, fname, path="", pd_query=""):
        if path != "":
            fname = os.path.join(path, fname)
        results = pandas.read_csv(fname, sep=";")
        if pd_query:
            results = results.query(pd_query)
        values = [str(v) for v in results["value"]]

        try:
            tags = [str(v) for v in  results["tag"]]
        except:
            tags = ["tag{}".format(i) for i in range(0, len(set(values)))]

        results = set(zip(values, tags))
        values = [eval(v[0]) for v in results]
        tags = [str(v[1]) for v in  results]

        return values, tags

    def _expand_pattern_searches(self, request):
        try:
            fname = request["pattern"]["file"]
            ftype = request["pattern"]["type"].lower()
        except:
            return [request]
        try:
            pd_query = request["pattern"]["query"]
        except:
            pd_query = ""
        if ftype != "pattern_list":
            print("Unknown file type: {}".format(ftype))
        values, tags = self._read_pattern_result_file(fname, pd_query=pd_query)
        ret = [None] * len(values)

        for i, v in enumerate(values):
            tmp = {k:request[k] for k in request}
            tmp["pattern"] = v
            try:
                label = tmp["label"]
                if not label:
                    label = os.path.splitext(os.path.basename(fname))[0]
                tmp["label"] = "{}_{}".format(label, tags[i])
            except:
                tmp["label"] = "{}".format(tags[i])

            #print "i: {}, pattern: {}, label: {} tag: {}".format(i, tmp["pattern"], tmp["label"], tags[i])
            ret[i] = tmp
        print("Added {} pattern searches.".format(len(ret)))
        return ret

    def _expand_requests(self):
        ret = []
        for r in self.requests:
            if not self._is_partition(r["pattern"]):
                if isinstance(r["pattern"], dict):
                    requests = self._expand_pattern_searches(r)
                    ret.extend(requests)
                else:
                    ret.append(r)
                continue
            min_N_is = IntSpan(r["minN"])
            try:
                min_occur_is = IntSpan(r["minOccur"])
            except:
                min_occur_is = IntSpan("2")
            try:
                min_source_is = IntSpan(r["minSource"])
            except:
                min_source_is  = IntSpan("1")
            for minN in min_N_is:
                for minO in min_occur_is:
                    for minS in min_source_is:
                        tmp = {k:r[k] for k in r}
                        tmp["minN"] = minN
                        tmp["minOccur"] = minO
                        tmp["minSource"] = minS
                        ret.append(tmp)
        return ret

    def process(self, write=False, verbose=None):
        self.results = []
        if self.requests == None or len(self.requests) == 0:
            raise RuntimeError("No pattern requests specified")

        if verbose == None:
            verbose = self.verbose

        self.ndp.importer_cache = self.use_cache

        if self.use_cache:
            self.ndp.song_cache = self.song_cache
        self.requests  = self._expand_requests()

        self.ndp.read_melodies()
        self.song_cache = self.ndp.song_cache
        self._patch_items()
        pm = PatternMiner(self.requests,
                          self.ndp,
                          self.maxN,
                          verbose=verbose)
        pm.set_process_hooks(self.proc_hooks)
        self.results = pm.process(verbose=verbose)

        if write:
            std_out = True if write == "std_out" else False
            outfile_filepath = self.write(std_out=std_out, verbose=verbose)

        return self.results

    def write(self, std_out=False, verbose=None):
        if not self.results:
            print("Nothing to write.")
            return
        if verbose == None:
            verbose = self.verbose
        try:
            write_hook = self.proc_hooks["write"]
        except:
            write_hook = None

        if self.outdir != ".":
            ensure_dir(self.outdir)

        pattern_writer = PatternWriter(self.outfile,
                          self.outdir,
                          self.ndp.mel_rep,
                          db_session = self.db_session,
                          app_name = self.app_name,
                          audio_slicer=self.audio_slicer,
                          convention=self.convention,
                          crop_images=self.crop_images,
                          verbose=verbose,
                          proc_hook=write_hook)
        pattern_writer.sep= self.sep
        pattern_writer.prec = self.precision

        for result in self.results:
            display = result.display[0]

            if verbose:
                print("-"*60)
                print("Writing '{}' results with display: {}".format(result.type, display))
            if result.type == "partition":
                if std_out:
                    pattern_writer.print_pattern_partition(result)
                else:
                    pattern_writer.write_pattern_partition(result)
            elif result.type == "search":
                if std_out:
                    if display == "audio" or display == "midi":
                        print("Cannot print {} to std.out".format(display))
                    else:
                        pattern_writer.print_search_result(result)
                else:
                    pattern_writer.write_search_result(result)
            elif result.type == "database":
                if std_out:
                    pattern_writer.print_database(result)
                else:
                    pattern_writer.write_database(result)
        self.outfiles = pattern_writer.outfile_cache

        outfile_filepath = None
        if len(self.outfiles) > 0:
            outfile_filepath = self.outfiles[-1]

        if outfile_filepath and verbose:
            print("Written to ", outfile_filepath)

        return outfile_filepath
