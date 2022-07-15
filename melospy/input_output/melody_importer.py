#!/usr/bin/env python

""" Class implementation of MelodyImport"""
import os
import random

from melospy.input_output.esac_reader import *
from melospy.input_output.krn_reader import *
from melospy.input_output.mcsv_reader import *
from melospy.input_output.mcsv_writer import *
from melospy.input_output.mel_db_adapter_factory import *
from melospy.input_output.midi_reader import *
from melospy.input_output.midi_writer import *
from melospy.input_output.read_sv_project import *
from melospy.input_output.tony_csv_reader import *
from melospy.tools.commandline_tools.util import *


class MelodyImporter(object):
    """Class for reading melody data in various file formats or from a database"""

    input_format_map = {"esa": "esa", "esac":"esa", "tcsv":"tcsv", "csv":"mcsv1", "mcsv":"mcsv2", "mid":"mid", "midi":"mid", "sv": "sv", "txt":"notes", "krn":"**kern"}
    test_pattern_search_db =[
        {'query': {'conditions': {'solo_info': {'performer': 'D%', 'title': '%'}}, 'type': 'sv', 'display': {'transcription_info': 'filename_sv'}}}
        ]
    test_tunes_db =[
        {'query': {'conditions': {'solo_info': {'performer': 'Miles%', 'title': 'So%'}}, 'type': 'sv', 'display': {'transcription_info': 'filename_sv'}}},
        {'query': {'conditions': {'solo_info': {'performer': 'Miles%', 'title': 'Vierd%'}}, 'type': 'sv', 'display': {'transcription_info': 'filename_sv'}}},
        {'query': {'conditions': {'solo_info': {'performer': 'Miles%', 'title': 'Blues%'}}, 'type': 'sv', 'display': {'transcription_info': 'filename_sv'}}}
        ]
    test_tunes_esac =[{'query': {'conditions': {'esac_info': {'esacid': 'A0007%'}}, 'type': 'esac', 'display': {'esac_info': 'esacid'}}}]
    test_tunes_pop  =[{'query': {'conditions': {'popsong_info': {'filename': '010%'}}, 'type': 'popsong', 'display': {'popsong_info': 'filename'}}}]
    test_tunes_files = [{'files': 'MilesDavis_SoWhat_FINAL.sv'}]
    tunes_db_all =[{'query': {'conditions': {'solo_info': {'performer': '%', 'title': '%'}}, 'type': 'sv', 'display': {'transcription_info': 'filename_sv'}}}]
    esac_db_all =[{'query': {'conditions': {'esac_info': {'esacid': '%'}}, 'type': 'esac', 'display': {'esac_info': 'esacid'}}}]
    omnibook_db_all =[{'query': {'conditions': {'solo_info': {'performer': '%', 'title': '%'}}, 'type': 'sv', 'display': {'transcription_info': 'filename_sv'}}}]

    def _get_item_id(self, s, max_val=0):
        tmp = s.split("-")
        if len(tmp)<3:
            return 0
        val = min(max_val, int(tmp[2]))
        return val


    @staticmethod
    def queryFromSoloInfo(performer,title, title_addon=None, solo_part=None):
        inner_dict = {'performer': performer, 'title': title}
        if title_addon != None:
            inner_dict["titleaddon"] = title_addon
        if solo_part != None:
            inner_dict["solopart"] = solo_part

        query = {'query': {'conditions': {'solo_info': inner_dict}, 'type': 'sv', 'display': {'transcription_info': 'filename_sv'}}}
        return query

    @staticmethod
    def queryFromPopSongInfo(artist, title):
        inner_dict = {'artist': artist, 'title': title}

        query = {'query': {'conditions': {'popsong_info': inner_dict}, 'type': 'popsong', 'display': {'popsong_info': 'filename'}}}
        return query

    @staticmethod
    def queryFromEsacInfo(esacid, collection=None):
        inner_dict = {'esacid': esacid}
        if collection != None:
            inner_dict["collection"] = collection

        query = {'query': {'conditions': {'esac_info': inner_dict}, 'type': 'esac', 'display': {'esac_info': 'esacid'}}}
        return query

    def __init__(self, tunes, path=None, dbinfo=None, sep="/", params=None, input_format=None, proc_hook=None):

        if not isinstance(tunes, list):
            tunes = [tunes]
        try:
            if tunes[0][0:7]=="test-db":
                item = self._get_item_id(tunes[0],
                                         max_val=len(MelodyImporter.test_tunes_db))
                tunes = [MelodyImporter.test_tunes_db[item]]
            if tunes[0][0:9]=="test-esac":
                tunes = MelodyImporter.test_tunes_esac
            if tunes[0][0:9]=="test-pop":
                tunes = MelodyImporter.test_tunes_pop
            if tunes[0][0:10]=="test-files":
                tunes = MelodyImporter.test_tunes_files
            if tunes[0]=="all":
                tunes = MelodyImporter.tunes_db_all
        except:
            pass
        self.tunes  = None
        self.input_format = input_format
        self.melids = None
        self.params = params
        self.displays   = []
        self.tunetypes  = []
        self.sep    = sep
        self.cache = {}
        self.globber_multiplicities = []
        if path == None or len(path)==0:
            path = os.curdir

        self.path   = add_path_sep(path, sep)
        self.dbinfo = dbinfo
        self.dbmode = dbinfo.use if dbinfo is not None else False

        if self.dbmode:
            if self.dbinfo.type.lower() != "sqlite3":
                raise ValueError("DB type '{}' not supported".format(self.dbinfo.type))
            self.prepareDatabaseMode(tunes)
        else:
            self.prepareFileMode(tunes)

        self._evaluateParams()
        if proc_hook == None:
            self.proc_hook = jm_util.void
        else:
            self.proc_hook = proc_hook

    def _evaluateParams(self):
        try:
            self.use_cache = bool(self.params["melody_importer"].getValue("use_cache"))
        except:
            self.use_cache = True
        #raise
        #print "_evaluateParams"
        #print self.use_cache
        #print bool(self.params["melody_importer"].getValue("use_cache"))
        samples = 0
        try:
            samples = int(self.params["melody_importer"].getValue("samples"))
            #print "Got sample", samples
        except:
            pass
        try:
            seed = int(self.params["melody_importer"].getValue("seed"))
            #print "Got seed:", seed
            random.seed(seed)
        except:
            pass

        L = self.getNumberItems()
        #print samples, L
        self.samples = list(range(L))
        if  samples > 0 and L > 0:
            #print "Found sample count: {}".format(samples)
            if samples > L:
                samples = L
            self.samples = random.sample(list(range(L)), samples)
        #print "Sample idz: {}".format(self.samples)
        self.last_read_idx = -1

    def setParams(self, params):
        self.params = params
        self._evaluateParams()

    def getMelIDs(self, queries):
        tmp_ids = []
        if self.dbinfo.type.lower() == "sqlite3":
            with MelDBAdapterFactory(self.dbinfo).create() as mdb:
                for q in queries:
                    oldlen = len(tmp_ids)
                    #print "Querying: ", q
                    ids  = [row[0] for row in mdb.query(q)]
                    tmp_ids.extend(ids)
                    #print len(ids), len(tmp_ids)
                    self.globber_multiplicities.append(len(tmp_ids)-oldlen)
        #print "Glober_mult: ",self.globber_multiplicities
        return tmp_ids

    def getDisplayNamesByID(self, melids):
        tmp_displays= []
        if len(self.displays) == 0:
            return [str(i) for i in melids]
        displays = repeater(self.displays, self.globber_multiplicities)
        #print displays
        #sys.exit(0)
        if self.dbinfo.type == "sqlite3":
            with MelDBAdapterFactory(self.dbinfo).create() as mdb:
                for i, d in enumerate(self.displays):
                    table = list(d.keys())[0]
                    field = d[table]
                    #print "Querying: ", table, field
                    tmp_displays.extend(mdb.getDisplayNamesByMelIDs(melids, table, field))
        #print "Display: ", tmp_files
        return tmp_displays

    def getDisplayNames(self, queries):
        tmp_displays= []
        if len(self.displays) == 0:
            return [str(i) for i in self.melids]
        #print displays
        #sys.exit(0)
        if self.dbinfo.type == "sqlite3":
            with MelDBAdapterFactory(self.dbinfo).create() as mdb:
                for i, d in enumerate(self.displays):
                    table = list(d.keys())[0]
                    field = d[table]
                    #print "Querying: ", queries[i], table, field
                    tmp_displays.extend(mdb.getDisplayNamesByNestedSelect(queries[i], table, field))
        #print "Display: ", tmp_displays
        #sys.exit(0)
        return tmp_displays

    def uniquify(self):
        if len(self.tunes) != len(self.melids):
            raise RuntimeError("Tune list and melids do not match in length ({}<-> {})".format(len(self.tunes), len(self.melids)))
        comp = [(self.tunes[i], self.melids[i]) for i in range(len(self.melids)) ]
        uq = unique(comp, hash_list)
        tunes = [elements[0] for elements in uq]
        melids = [elements[1] for elements in uq]
        #print len(tunes), len(self.tunes)
        #print len(melids), len(self.melids)
        self.tunes = tunes
        self.melids = melids

    def parseQuery(self, query):
        try:
            conditions = query["conditions"]
        except:
            raise ValueError("No conditions for SQL query provided")
        try:
            self.displays.append(query["display"])
        except:
            #self.displays.append("")
            #raise ValueError("No display name for tunes provided")
            print("WARNING: No display name for tunes provided")
        try:
            self.tunetypes.append(query["type"])
        except:
            self.tunetypes.append("sv")
            print ("WARNING: No tune type provided. Assuming 'SV' format")
        #print "Display: ", self.displays
        #print "TT: ", self.tunetypes
        #print query, conditions
        keys = list(conditions.keys())[0]
        if keys == "SQL":
            return conditions[keys]

        sqlstatement = "SELECT DISTINCT(melid) FROM {} WHERE ".format(keys)
        conditions = conditions[keys]
        #print (conditions)
        if isinstance(conditions, dict):
            #print "WARNING: conditions should be list of <key>: <value> fields, not a dictionary."
            conditions =[{k:str(conditions[k])} for k in conditions]
            #print conditions
        negations = ["" for _ in range(len(conditions))]
        #for k in range(len(conditions)):
        #    print k
        #    negations[k] = ""
        #print "STOP"
        fields = [list(k.keys())[0] for k in conditions]
        values = []
        for k in range(len(conditions)):
            cur = list(conditions[k].values())[0]
            if cur[0] == "~" or cur[0] == "!" or cur[0] == "-":
                cur = cur[1:]
                negations[k] = "NOT"
            values.append(cur)
        #print "Conditions:", conditions
        #print "Fields:", fields
        #print "Values:", values
        #print "Negations: ", negations
        cond_elems = ['{} {} LIKE "{}"'.format(fields[k], negations[k], values[k].replace("*", "%")) for k in  range(len(fields))]
        #print "Cond elems", cond_elems
        whereclause = " AND ".join(cond_elems)
        #print "WHERE:", whereclause
        #print "SQL:", sqlstatement + whereclause
        return sqlstatement + whereclause

    def prepareDatabaseMode(self, tunes):
        queries = []
        for f in tunes:
            for q in f:
                if q != "query":
                    continue
                try:
                    queries.append(self.parseQuery(f[q]))
                except Exception as e:
                    print(str(e.args[0]))
                    pass
        if len(queries) == 0:
            raise ValueError("No song queries found")
        #print "QUERIES:", queries
        if os.path.dirname(self.dbinfo.path) == "":
            self.dbinfo.path = normpath(self.path + self.dbinfo.path)
        if self.dbinfo.type == "sqlite3":
            with open(self.dbinfo.path): pass
            try:
                with open(self.dbinfo.path): pass
            except IOError:
                raise ValueError("SQLITE DB file not found at "+ self.dbinfo.path)
        self.melids = self.getMelIDs(queries)
        self.tunes  = self.getDisplayNames(queries)
        self.tunetypes = repeater(self.tunetypes, self.globber_multiplicities)
        tt  = {}
        for i, melid in enumerate(self.melids):
            tt[melid] = self.tunetypes[i]
        self.tunetypes = tt
        #print self.melids, self.tunes,self.tunetypes
        self.uniquify()
        #print len(self.tunetypes)
        #sys.exit(0)

    def prepareFileMode(self, tunes):
        files = []
        for f in tunes:
            for q in f:
                if q[0:4] != "file":
                    continue
                try:
                    files.append(f[q])
                except Exception as e:
                    print(str(e.args[0]))
                    pass
        if len(files) == 0:
            raise ValueError("No files found")
        for i in range(len(files)):
            if os.path.dirname(files[i]) == "":
                files[i] = normpath(self.path + files[i])
        try:
            tmp_files = []
            for f in files:
                oldlen = len(tmp_files)
                sorted_files = sorted(glob.glob(f), key=lambda str: str.lower())
                if len(sorted_files) == 0:
                    print("Warning: No files for {} found".format(f))
                    continue
                tmp_files.extend([normpath(_) for _ in sorted_files])
                self.globber_multiplicities.append(len(tmp_files)-oldlen)

            self.tunes = tmp_files
            if len(self.tunes)==0:
                raise
        except Exception as e:
            raise ValueError("No files to process.")
        #print "Glober_mult: ",self.globber_multiplicities

    def readMelodyFromDatabase(self, melid):
        #print "readMelodyFromDatabase called"
        if self.use_cache:
            if melid in self.cache:
                #print "Cache hit!"
                return self.cache[melid]

        solo = None
        if self.dbinfo.type == "sqlite3":
            with MelDBAdapterFactory(self.dbinfo).create() as mdb:
                tt = self.tunetypes[melid].lower()
                print("Fetching tune with melid {} of type {}.".format(melid, tt))
                if tt == "sv":
                    solo = mdb.readSolos(melid)[melid]
                elif tt[0:3] == "esa":
                    solo = mdb.readEsacSongs(melid)[melid]
                elif tt[0:3] == "pop":
                    solo = mdb.readPopSongs(melid)[melid]
                else:
                    print("Warning: Unknown tune type '{}', assumming SV".format(self.tunetypes[melid]))
                    solo = mdb.readSolos(melid)[melid]

        if self.use_cache:
            if melid not in self.cache:
                #print "add to cache"
                self.cache[melid] = solo[melid]
        return solo

    def guessInputFormat(self, filename):
        ext = os.path.splitext(filename)[1][1:]
        if len(ext) == 0:
            raise ValueError("Cannot guess input format: No extension.")
        try:
            ipf = self.input_format_map[ext.lower()]
        except:
            raise ValueError("Unrecognized input format: '{}'".format(ext))
        return ipf

    def guess_csv_format(self, filename):
        """Guess format for csv file:
            returns:
                "mcsv1", "mcsv2", "tony", "unknown"
        """
        with open(filename, 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=';', lineterminator="\n", quotechar='|', quoting=csv.QUOTE_MINIMAL)
            first_line = next(csvreader)
            #print "first_line", first_line
            if first_line[0].find("Signature")>-1  and first_line[0].find("Ticks")>=0:
                return "mcsv1"
            if "onset" in first_line:
                return "mcsv2"
            try:
                first_line = [float(_) for _ in first_line[0].split(",")]
                #Tony exports three columns, whereas pYIN exports four
                if len(first_line) == 4 or len(first_line) == 3:
                    return "tcsv"
            except:
                pass
        return "unknown"

    def readMelodyFromFile(self, filename, input_format=None):
        if self.use_cache:
            if filename in self.cache:
                return self.cache[filename]
        if input_format == None:
            input_format = self.input_format
            if input_format == None:
                input_format = self.guessInputFormat(filename)
        #print "File: {}, format:{}".format(filename, input_format)
        ret = None
        #out of try:
        #mcsv_reader_params = get_safe_value_from_dict(self.params, "mcsv_reader", MCSVReaderParams())
        #csv_format = self.guess_csv_format(filename)
        #mr = MCSVReader(filename, mcsv_reader_params, csv_format)
        #sv_params = get_safe_value_from_dict(self.params, "sv_reader", SVReaderParams())
        #print "sv-params", sv_params
        try:
            if input_format == "sv":
                sv_params = get_safe_value_from_dict(self.params, "sv_reader", SVReaderParams())
                svread = SVReader(filename, sv_params)
                #flexq = get_safe_value_from_dict(self.params, "flexq", ConfigMetricalAnnotation())
                #flexq = self.params["flexq"] if isinstance(self.params["flexq"], ConfigMetricalAnnotation) else ConfigMetricalAnnotation()
                svread.bundle()
                smd = SoloMetaData(None, None, TranscriptionInfo(fileNameSV = filename), None)
                solo = svread.solo
                smd.soloinfo = solo.metadata.soloinfo
                solo.setMetadata(smd)
                ret = solo
            elif input_format in ["mcsv1", "mcsv2", "csv", "tcsv"]:
                #mr = MCSVReader(filename, params=self.params)
                csv_format = self.guess_csv_format(filename)
                print("Found {} format for {}".format(csv_format, filename))
                if csv_format == "unknown":
                    raise RuntimeError("Could not determine CSV file type")
                if csv_format == "tcsv":
                    mr = TonyCSVReader(filename, params=self.params)
                    ret = mr.melody
                else:
                    mcsv_reader_params = get_safe_value_from_dict(self.params, "mcsv_reader", MCSVReaderParams())
                    mr = MCSVReader(filename, mcsv_reader_params, csv_format)
                    ret = mr.melody
            elif input_format == "mid":
                params = self.params if isinstance(self.params, MIDIReaderParams) else None
                print("Reading MIDI {}".format(filename))
                mr = MIDIReader2(filename, params=params)
                print("...done")
                ret = mr.melody
            elif input_format == "**kern":
                krn_params = get_safe_value_from_dict(self.params, "krn_reader", KernReaderParams())
                kr = KernReader(filename, krn_params)
                ret =  kr.solo
                #raise RuntimeError("Unknown filetype with extension: '{}'".format(input_format))
            elif input_format == "esa":
                er = EsACReader(filename)
                s = er.solo
                if s != None:
                    s.__dict__["esacinfo"] = er.getEsACInfo()
                ret = s
            else:
                raise RuntimeError("Unknown filetype with extension: '{}'".format(input_format))
        except Exception as e:
            raise RuntimeError(e)

        if self.use_cache:
            if filename not in self.cache:
                self.cache[filename] = ret

        return ret

    def getNumberItems(self):
        if self.dbmode:
            return len(self.melids)
        return len(self.tunes)

    def __getitem__(self, i):
        return self.__melodies[i]

    def updateCache(self, verbose=False):
        if not self.use_cache:
            return

        new_ids= list(set(self.melids).difference(list(self.cache.keys())))
        if len(new_ids)>0:
            with MelDBAdapterFactory(self.dbinfo).create(proc_hook=self.proc_hook) as mdb:
                if verbose:
                    print("Reading songs into cache...")
                tmp_cache = mdb.readSongs(new_ids)
                self.cache.update(tmp_cache)

    def clearCache(self):
        del self.cache
        self.cache = {}

    def fetcher(self, verbose=True):
        #print "Tunes:", self.tunes
        if self.dbmode:
            self.updateCache(verbose)
            for i, melid in enumerate(self.melids):

                if i not in self.samples:
                    continue
                self.last_read_idx = i
                if not self.use_cache:
                    self.proc_hook(i, len(self.melids), i)
                try:
                    yield self.readMelodyFromDatabase(melid)
                except Exception as e:
                    #raise e
                    if verbose:
                        print("Error fetching melid: {}. Reason: {}".format(melid, e))
                    yield None
        else:
            for i, f in enumerate(self.tunes):
                if i not in self.samples:
                    continue
                #print "Yielding ", f
                self.last_read_idx = i
                self.proc_hook(i, len(self.tunes), os.path.basename(f))
                #out of try
                #yield self.readMelodyFromFile(f)
                try:
                    #pass
                    yield self.readMelodyFromFile(f)
                except Exception as e:
                    if verbose:
                        print("Error reading file: {}. Reason: {}".format(f, e.args[0]))
                    yield None

    def __iter__(self):
        return self.fetcher(verbose=False)
