"""
    Class implementation of NGramDataProvider.
    Provides NGramDatabases.
"""

from melospy.basic_representations.jm_util import remove_from_list
from melospy.input_output.melody_importer import *
from melospy.pattern_retrieval.ngram_database import *
from melospy.pattern_retrieval.ngram_simulate import *
from melospy.tools.commandline_tools.dbinfo import DBInfo
from melospy.tools.commandline_tools.param_helper import SQLQuery


class EmptyRepositoryError(Exception):
    def __init__(self, msg):
        self.msg = msg

class InvalidTransformError(Exception):
    def __init__(self, msg):
        self.msg = msg

class TransformDef(object):

    def __init__(self, valtype, iOff, lOff, needsParam, optParam=""):
        self.valtype =valtype
        self.iOff = iOff
        self.lOff = lOff
        self.needsParam = needsParam
        self.optParam = optParam

    def __str__(self):
        return "Value type:{}, index offset: {}, len offset: {}, needs param:{}".format(self.valtype, self.iOff, self.lOff, self.needsParam)

transform_definitions = {
            "interval": TransformDef("int", 0, 1, False),
            "fuzzyinterval": TransformDef("int", 0, 1, False),
            "parsons": TransformDef("int", 0, 1, False),
            "pc": TransformDef("int", 0, 0, False),
            "cpc": TransformDef("int", 0, 0, True, "keepnc"),
            "tpc": TransformDef("int", 0, 0, False),
            "tdpc": TransformDef("string", 0, 0, False),
            "cdpc": TransformDef("string", 0, 0, True, "keepnc"),
            "cdpcx": TransformDef("string", 0, 0, True, "keepnc"),
            "pitch": TransformDef("int", 0, 0, False),
            "durclass":TransformDef("int", 0, 0, True),
            "ioiclass":TransformDef("int", 0, 1, True),
            "dur_ratio_class":TransformDef("int", 0, 2, False),
            "ioi_ratio_class":TransformDef("int", 0, 2, False),
            "mcm":TransformDef("int", 0, 0, False),
            "metricalweights":TransformDef("int", 0, 0, False),
            "accent":TransformDef("int", 0, 0, True)
           }



class NGramDataProvider(object):
    """Class for providing data for pattern mining applications
        Read a set of melodies from a given specification and returns
        a melody repository as well as derived NgramDatabase object for
        derived transformations. Provides also simulated NGramDatabases.
    """

    def __init__(self,
                 wdir,
                 tunes,
                 src_dbi=None,
                 verbose=False,
                 params=None,
                 proc_hooks=None):
        """ initialization of object
        Args:
            wdir (string)       : working directory for input data
            tunes (list of dict): list of tunes of DB querues
            src_dbi (DBInfo): Database information
        Ret:

        """
        #working directory
        self.wdir            = wdir
        #tune specs (list of file names, SQL Query stuff)
        self.tunes           = tunes
        #DBInfo object for DB use
        self.src_dbi         = src_dbi
        #Melody repository
        self.mel_rep         = []
        #List of (helper) keys per melody, used in NGramDatabase for back ref
        self.keys            = []
        #Cache of simulated NGramDatabases
        self.simulated_dbs   = {}
        #Cache of derived NGramDatabases
        self.ngram_dbs       = {}
        #Cache of NGramRefRepositories
        self.ref_reps        = {}
        #being talkative?
        self.verbose         = verbose
        #seed for simulation, can be set before calling simulate_ngramdb
        self.seed            = None
        #Extra params for melody  importer
        self.params = params
        #MelodyImporter cache use
        self.importer_cache  = True

        #MelodyImporter cache use
        self.song_cache = {}
        #function hook for building databases and such
        #signature should be proc_func(N, maxN)
        self.proc_hooks = proc_hooks

    def clear_cache(self):
        self.ngram_dbs = {}

    def read_melodies(self, force=False):
        """
            Reads melodies into repository.
            Mandatory call before anything else can be done.
            Args:
                force (Boolean):
                    enforce re-reading of melodies
            Returns:
        """

        #do only once, if not forced
        if len(self.mel_rep) != 0 and not force:
            return
        start = time.process_time()
        if self.verbose:
            print("Reading melodies...")

        proc_hook = None
        try:
            proc_hook = self.proc_hooks["import"]
        except:
            proc_hook = None

        mi = MelodyImporter(self.tunes,
                            self.wdir,
                            self.src_dbi,
                            params=self.params,
                            proc_hook=proc_hook)
        mi.use_cache = self.importer_cache

        if self.importer_cache:
            mi.cache = self.song_cache

        fetcher = mi.fetcher()
        #self.mel_rep = [mel for mel in fetcher if mel != None]
        self.mel_rep = [mel for mel in fetcher]
        self.keys = mi.tunes
        #assert(len(self.mel_rep) == len(self.keys)
        if len(self.mel_rep) == 0:
            raise RuntimeError("No melodies found.")
        else:
            if self.verbose:
                print("Read {} melodies in {} s".format(len(self.mel_rep), round(time.process_time()-start, 3)))

    @staticmethod
    def parse_transform(transform):
        transform = transform.lower()
        optParam = ""
        needsParam = False
        tmp = transform.split("-")
        has_param = False
        if len(tmp) > 1:
            transform = tmp[0]
            optParam = tmp[1]
            has_param =  True
        try:
            needsParam = transform_definitions[transform].needsParam
            if not has_param:
                optParam = transform_definitions[transform].optParam
        except:
            raise InvalidTransformError("Invalid transformation: {}".format(transform))
        #print "Tranform: {}, optParam: {}".format(transform, optParam)
        if needsParam and len(optParam) == 0:
            raise InvalidTransformError("Transformation '{}' needs parameter".format(transform))

        return transform, optParam

    @staticmethod
    def get_transform_offsets(transform):
        """
            Return offsets for transforms.
            Necessary for correct back referencing.

            Args:
                transform (string):
                Name of melody transformation

            Returns:

                indexOffset (int)
                lengthOffset (int)
        """
        main_transform, optParam = NGramDataProvider.parse_transform(transform)
        iOff, lOff = (0, 0)
        iOff, lOff = transform_definitions[main_transform].iOff, transform_definitions[main_transform].lOff

        return iOff, lOff


    def get_transform_rep(self, transform, fix_errors=True):
        """
            Builds a repository of derived transformations from the
            melody repository if not already found in internal cache.

            Args:
                transform (string):
                    Name of melody transformation
            Returns:
                NGramRefRepository object
        """
        if transform in self.ref_reps:
            if self.verbose:
                print("Found NGramRefRepository for transform '{}' in cache".format(transform))
            return self.ref_reps[transform]

        main_transform, optParam = NGramDataProvider.parse_transform(transform)

        if len(self.mel_rep) == 0:
            raise RuntimeError("No melodies in repository")

        ret = []
        valtype = "string"
        try:
            valtype = transform_definitions[main_transform].valtype
        except:
            if self.verbose:
                print("Unknown value type for transformation '{}'. Let's try our luck with strings.".format(transform))
        bad_solos = []

        for i, solo in enumerate(self.mel_rep):
            try:
                if valtype == "int":
                    vec = [int(v) for v in solo.export(main_transform, optParam=optParam)]
                elif valtype == "float":
                    vec = [float(v) for v in solo.export(main_transform, optParam=optParam)]
                else:
                    vec = "".join([str(v) for v in solo.export(main_transform, optParam=optParam)])
            except:
                # print("empty")
                vec = []

            if len(vec) == 0:
                #raise RuntimeError(msg)
                if  solo != None:
                    try:
                        main_id = solo.get_main_id()
                    except:
                        main_id = "NA"
                    msg = "WARNING: Got empty export vector for {}".format(main_id)
                    print(msg)
                bad_solos.append(i)
            ret.append(vec)


        if len(bad_solos) > 0:
            if not fix_errors:
                print(EmptyRepositoryError("Could not build transform repository"))
                #raise EmptyRepositoryError("Could not build transform repository")
            else:
                #ids = [solo.__dict__["esacinfo"].getField("esacid") for solo in self.mel_rep]
                #print ids[0], self.keys[0], ids[0] == self.keys[0]

                #print "Before", sum([int(p[0] == p[1]) for p in zip(ids,self.keys)])
                #print len(ids)
                self.mel_rep = remove_from_list(self.mel_rep, bad_solos)
                self.keys    = remove_from_list(self.keys, bad_solos)
                ret          = remove_from_list(ret, bad_solos)
                print("Removed ", len(bad_solos), " melodies")
                #ids = [solo.__dict__["esacinfo"].getField("esacid") for solo in self.mel_rep]
                #print "After", sum([p[0] == p[1] for p in zip(ids,self.keys)])/len(ids)

                if len(ret) == 0:
                    raise EmptyRepositoryError("Could not build transform repository due to all empty exports.")

        nr = NGramRefRepository(valtype)
        nr.extend(ret, self.keys)
        self.ref_reps[transform] = nr

        if self.verbose:
            print("NGramRefRepository for transform '{}' successfully built".format(transform))
        return nr


    def get_database(self, transform, build_db=True, maxN=30, fix_errors=True):
        """
            Builds a NGramDatabase object from a NGramRefRepository
            if not already found in internal cache.

            Args:
                transform (string):
                    Name of transformation
                build_db (Bool):
                    If **False**, NGramDataBase will not be properly built,
                    but object can provide search functionality.
                    If **True**, NGramDatabase will be built, necessary for
                    partition mode. Might take a while.
                maxN (int):
                    Maximal N for building the NGramDatabase
            Returns:
                NGramDatabase object
        """
        #main_transform, optParam = self.parse_transform(transform)
        start = time.process_time()
        #print "get_database", self.ngram_dbs.keys(), len(self.ngram_dbs)
        if (transform, maxN) in self.ngram_dbs:
            #print "NgramDataProvider cache hit"
            return self.ngram_dbs[(transform, maxN)]

        nr = self.get_transform_rep(transform, fix_errors)
        if build_db and self.verbose:
            print("Building pattern database for '{}'... (maxN = {})".format(transform, maxN))

        if build_db and self.verbose and len(nr)>1000:
            print("WARNING: This might take a LONG time...")

        ndb = NGramDatabase(nr, maxN=maxN, transform=transform, build=build_db, verbose=self.verbose, proc_hooks=self.proc_hooks)

        self.ngram_dbs[(transform, maxN)] = ndb
        #print self.ngram_dbs.keys(), len(self.ngram_dbs)
        if build_db and self.verbose:
            print("Finished in {} s".format(round(time.process_time()-start, 3)))

        return ndb

    def simulate_database(self, transform, maxN, order, display_name="SIMUL", cache=False):
        """ Simulation of a NGramDataBase with Markov model of order *order*.
            Args:
                transform (string):
                    Name of transformation
                maxN (int):
                    Maximal N for building NGramDatabase
                order (int):
                    Order of the Markov model to be used
                display_name (string):
                    Display name
                cache (Bool):
                    Shall simulated database be cached?
            Returns:
                NGramDatabase object
        """
        #orig_transform = transform
        #print "simulate_database", orig_transform
        #transform, optParam = NGramDataProvider.parse_transform(transform)
        #print "simulate_database", orig_transform
        if cache:
            if transform in self.simulated_dbs:
                return self.simulated_dbs[(transform, order, prune)]

        sim = SimulateNGramDB(self.verbose, self.seed)
        ndb = self.get_database(transform, build_db=True, maxN=maxN)
        ndb.verbose = False
        ndb = sim.simulate2(ngram_db=ndb, maxN=maxN, transform=transform, order=order, display_name=display_name)
        ndb.verbose=self.verbose
        if cache:
            self.simulated_dbs[(transform, order)] = ndb
        return ndb
