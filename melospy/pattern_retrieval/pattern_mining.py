import os

from melospy.basic_representations.jm_util import *
from melospy.pattern_retrieval.ngram_data_provider import *
from melospy.pattern_retrieval.ngram_database import *
from melospy.pattern_retrieval.ngram_simulate import *


class PatternRequest(object):
    allowed_displays = []

    def __init__(self, transform, display="list", label="", 
                 context_size_pre="", context_size_post="", main_pattern="", 
                 search=None, proc_func=None):
        transform = transform.lower()
        try:
            main_transform = transform.split("-")[0]
            self.valtype = transform_definitions[main_transform].valtype
        except:
            raise ValueError("Unknown transformation '{}'. ".format(transform))
        self.transform = transform

        if isinstance(display, str):
            display = display.split(",")
        display = [chomp(d).lower() for d in display]
        for d in display:
            if d not in self.allowed_displays:
                raise ValueError("Invalid display '{}'. ".format(d))
        self.search = search
        self.context_size_pre = context_size_pre
        self.context_size_post = context_size_post
        self.main_pattern = main_pattern
        self.display = display
        self.label = label
        self.type = "N/A"
        self.secondary = None
        self.proc_func = proc_func
        self.output_context = ""

    def _eval_pattern(self, pattern):
        try:
            pat = eval(pattern)
        except:
            pat = pattern

        if isinstance(pat, int):
            if self.valtype == "string":
                pat = str(pattern)
            else:
                pat = [pat]

        if isinstance(pat, tuple):
            pat = list(pat)

        return pat

    def __str__(self):
        line = "-"*40 + "\n"
        s = "\n".join(["{}: {}".format(a, self.__dict__[a]) for a in sorted(self.__dict__)])
        return "\n" + line  + s + "\n" + line

class PatternSearch(PatternRequest):
    allowed_displays = ["audio", "list", "midi", "stats", "lilypond", "pdf", "png"]

    def __init__(self, transform, pattern='', display="list", label='', secondary=None, output_context='', context_size_pre='', context_size_post='', main_pattern='', search=None):
        PatternRequest.__init__(self, transform, display, label, context_size_pre, context_size_post, main_pattern, search)
        self.pattern = pattern
        self.type = "search"
        self.context_size_pre  = context_size_pre
        self.context_size_post = context_size_post
        self.main_pattern = main_pattern
        self.search = search
        self.result = []
        self.output_context = output_context

        # secondary must be None, a dict or a PatternSecondarySearch object
        if isinstance(secondary, PatternSecondarySearch):
            self.secondary = secondary
        elif isinstance(secondary, dict):
            try:
                if "operation" in secondary:
                    operation = secondary["operation"]
                else:
                    operation = "match"
                sec_ps = PatternSecondarySearch(secondary["transform"], secondary["pattern"], operation)
                self.secondary = sec_ps
            except:
                raise ValueError("Invalid secondary pattern: {}".format(secondary))
        else:
            self.secondary = None

    @staticmethod
    def fromDict(s):
        pattern     = get_safe_value_from_dict(s, "pattern", msg = "Search {} missing.")
        context_size_pre  = get_safe_value_from_dict(s, "context_size_pre", 0)
        context_size_post = get_safe_value_from_dict(s, "context_size_post", 0)
        main_pattern = get_safe_value_from_dict(s, "main_pattern", "")
        try:
            search =  get_safe_value_from_dict(s, "search", None)
        except:
            search = None
        transform   = get_safe_value_from_dict(s, "transform", toLower=True, msg = "No {} found.")
        display     = get_safe_value_from_dict(s, "display", default= "list", toLower = True)
        label       = get_safe_value_from_dict(s, "label", "")
        secondary   = get_safe_value_from_dict(s, "secondary", "")
        output_context = get_safe_value_from_dict(s, "output_context", "")

        return PatternSearch(transform, pattern, display, label, secondary, output_context, context_size_pre, context_size_post, main_pattern, search)


    def process(self, ngram_db, verbose=False):
        if self.result:
            return self.result
        pat = self._eval_pattern(self.pattern)

        self.result = ngram_db.genreSearch(pat)

        return self.result

class PatternSecondarySearch(PatternRequest):

    allowed_displays = [""]
    allowed_operations = ["match", "exclude", "find", "ignore"]

    def __init__(self, transform, pattern="", operation="match"):
        PatternRequest.__init__(self, transform, "", "")

        self.pattern = pattern
        self.type = "search"
        self.result = []
        operation = operation.lower()

        if operation in self.allowed_operations:
            self.operation = operation
        else:
            raise ValueError("Invalid operation: {}".format(operation))

    @staticmethod
    def fromDict(s):
        pattern     = get_safe_value_from_dict(s, "pattern", msg = "Search {} missing.")
        transform   = get_safe_value_from_dict(s, "transform", toLower=True, msg = "No {} found.")
        operation   = get_safe_value_from_dict(s, "operation", {})
        return PatternSecondarySearch(transform, pattern, operation)

    def process(self, ngram_db, verbose=False):
        if self.result:
            return self.result

        pat = self._eval_pattern(self.pattern)
        self.result = ngram_db.genreSearch(pat)

        return self.result

class PatternPartition(PatternRequest):
    allowed_displays = ["list", "stats"]
    def __init__(self, transform,
                         minN=5,
                         minOccur=2,
                         minSource=1,
                         simul=False,
                         trillFilter=None,
                         scaleFilter=None,
                         arpeggioFilter=None,
                         items="",
                         display="list",
                         label="",
                         order=1
                         ):
        PatternRequest.__init__(self, transform, display, label)
        self.type        = "partition"
        self.minN        = minN
        self.minOccur    = minOccur
        self.minSource   = minSource
        self.simul       = simul
        self.items       = items
        self.setTrillFilter(trillFilter)
        self.setScaleFilter(scaleFilter)
        self.setArpeggioFilter(arpeggioFilter)
        self.partitions = []
        self.order = order
        if self.minSource > self.minOccur:
            self.minOccur = self.minSource
            #print "No. of occurences {} was smaller than no. of sources: {}".format(minOccur, minSource)
        #print "Created PatternPartition with items: {}".format(items)

    @staticmethod
    def strictFromDict(s):
        pp = PatternPartition.fromDict(s)
        for item in s:
            if item != "display":
                pp.__dict__[item] = s[item]
        if pp.minSource > pp.minOccur:
            pp.minOccur = pp.minSource
        return pp

    @staticmethod
    def fromDict(s):
        transform   = get_safe_value_from_dict(s, "transform", toLower=True, msg="No {} found. Skipping")
        display     = get_safe_value_from_dict(s, "display", default="list", toLower=True)
        label       = get_safe_value_from_dict(s, "label", "")
        minN        = get_safe_value_from_dict(s, "minN", 5)
        order       = get_safe_value_from_dict(s, "order", 1)
        minOccur    = get_safe_value_from_dict(s, "minOccur", 2)
        minSource   = get_safe_value_from_dict(s, "minSource", 1)
        simul       = get_safe_value_from_dict(s, "simul", False)
        items       = get_safe_value_from_dict(s, "items",  "")
        #print "Create PatternPartition from dict", s
        trillfilter =  get_safe_value_from_dict(s, "trillfilter", "", toLower=True)
        scalefilter =  get_safe_value_from_dict(s, "scalefilter", "", toLower=True)
        arpeggiofilter =  get_safe_value_from_dict(s, "arpeggiofilter", "", toLower=True)
        return PatternPartition(transform,
                                minN,
                                minOccur,
                                minSource,
                                simul,
                                trillfilter,
                                scalefilter,
                                arpeggiofilter,
                                items,
                                display,
                                label,
                                order
                              )

    def setTrillFilter(self, trillFilter):
        self.trill_min= None
        self.trill_max= None
        self.trill_strict= None
        self.filter_trills = False
        try:
            tf  = trillFilter.split(",")
            self.trill_min= int(tf[0])
            self.trill_max= int(tf[1])
            self.trill_strict = int(tf[2]) if len(tf)>2 else True
            self.filter_trills = True
            #print "Trillfilter found, min={}, max={}".format(self.trill_min, self.trill_max)
        except:
            #print "No trillfilter found"
            pass

    def setScaleFilter(self, scaleFilter):
        self.filter_scales= False
        self.scale_directed = None
        try:
            sf = scaleFilter.lower()
            self.scale_directed = True if sf[0] == "d" else False
            self.filter_scales = True if sf[0] != "n" and sf[0] != "f" else False
            #print "Scale filter found, directed={}, active:{}".format(self.scale_directed, self.filter_scale)
        except:
            #print "No scale filter found"
            pass

    def setArpeggioFilter(self, arpeggioFilter):
        self.filter_arpeggios = False
        self.arp_directed = None
        try:
            af = arpeggioFilter.lower()
            self.arp_directed = True if af[0] == "d" else False
            self.filter_arpeggios = True if af[0] != "n" and af[0] != "f" else False
            #print "Arpeggio filter found, directed={}, active:{}".format(self.arp_directed, self.filter_arpeggio)
        except:
            #print "No arpeggio filter found"
            pass

    def process(self, ngram_db, verbose=False):
        #print "Items: ", self.items
        if self.partitions and self.items == None:
            #print "PatternPart cache hit"
            return self.partitions

        result = []
        items = self.items

        if not items:
            raise RuntimeError("No items specified!")

        if verbose:
            print("Calculating NGramPartitions with minN={}, minOccur={}, minSource={}".format(self.minN, self.minOccur, self.minSource))

        for i in items:
            if self.proc_func:
                self.proc_func(i, len(items))
            tmp_result = ngram_db.getMaximalNGramPartition(int(i), normalize=True, minN=self.minN, minOccur=self.minOccur, minSource=self.minSource)
            if len(tmp_result) == 0:
                next
            if self.filter_trills:
                tmp_result.filterTrills(self.trill_min, self.trill_max, self.trill_strict, self.transform)
            if self.filter_scales:
                tmp_result.filterScales(self.transform, self.scale_directed)
            if self.filter_arpeggios:
                tmp_result.filterArpeggios(self.transform, self.arp_directed)
            result.append(tmp_result)

        self.partitions = result
        return result

class PatternDatabase(PatternRequest):
    allowed_displays = ["list", "stats", "tree"]
    def __init__(self, transform,
                         minOccur=1,
                         minN=1,
                         maxN=2,
                         simul=False,
                         display="list",
                         label="",
                         minSource=1,
                         order=1
                         ):
        PatternRequest.__init__(self, transform, display, label)
        self.type        = "database"
        self.minOccur    = minOccur
        self.minSource   = minSource
        if minOccur < minSource:
            self.minOccur = minSource
        self.minN        = minN
        self.maxN        = maxN
        self.simul       = simul
        self.order = order
        if self.maxN < self.minN:
            self.maxN = self.minN
    @staticmethod
    def fromDict(s):
        transform   = get_safe_value_from_dict(s, "transform", toLower=True, msg="No {} found. Skipping")
        display     = get_safe_value_from_dict(s, "display", default="list", toLower=True)
        label       = get_safe_value_from_dict(s, "label", "")
        minOccur    = get_safe_value_from_dict(s, "minOccur", 1)
        minSource   = get_safe_value_from_dict(s, "minSource", 1)
        minN        = get_safe_value_from_dict(s, "minN", 1)
        maxN        = get_safe_value_from_dict(s, "maxN", 2)
        simul       = get_safe_value_from_dict(s, "simul", False)
        order       = get_safe_value_from_dict(s, "order", 1)
        return PatternDatabase(transform,
                               minOccur,
                               minN,
                               maxN,
                               simul,
                               display,
                               label,
                               minSource,
                               order
                              )

    def process(self, ngram_db, verbose=False):
        return ngram_db

class PatternMiningResult(object):
    """Container class for results of PatternMining operations
        Holds all data necessary for further processing
    """
    def __init__(self, pattern_request,  result):
        self.type = pattern_request.type
        self.pattern_request = pattern_request
        self.result = result
        self.transform = pattern_request.transform
        self.display = pattern_request.display
        self.output_context = pattern_request.output_context

class PatternMiner(object):
    """Encapsulation of pattern mining functionality """

    def __init__(self, requests, ngram_data_provider, maxN=30, verbose=False):
        """initializes class

            Args:
                requests (var, mandatory):
                    either a list of dictionaries containing
                    parameters defining requests
                    or a list of objects inheriting from PatternRequest
                ngram_data_provider (NGramDataProvider, mandatory):
                    object of class NGramDataProvider
                maxN (integer, optional):
                    global maximum N for partitions.
        """
        self._prepare_requests(requests)
        self.results = []
        self.ndp = ngram_data_provider
        self.ndp.verbose = verbose
        self.maxN = maxN
        self.proc_hooks = None
        self.verbose = verbose

    def set_process_hooks(self, proc_hooks):
        self.proc_hooks = proc_hooks


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
        return pt == "partition" or pt == "all"

    def _get_request_type(self, pattern):
        """Check if request is database, search or partition
            Args:
                pattern (string):
                    parameter that defines request type
            Returns:
                string:
                    "database", "partition" or "search"
        """
        if not isinstance(pattern, str):
            return "search"

        pt = pattern.lower()
        pr_type = ""
        if pt == "partition" or pt == "all":
            pr_type = "partition"
        elif pt == "database":
            pr_type = "database"
        else:
            pr_type = "search"
        return pr_type

    def _prepare_requests(self, requests):
        """Prepares interal list of pattern requests
            Args:
                requests (var, mandatory):
                    either a list of dictionaries containing
                    parameters defining requests
                    or a list of objects inheriting from PatternRequest
        """
        self.requests = []
        #self.build_db = False
        for r in requests:
            if isinstance(r, PatternRequest):
                #be trustful that all elements in the list
                #are PatternRequests
                tmp = r
                pr_type = self._get_request_type(r.type)
            else:
                pr_type = self._get_request_type(r["pattern"])
                if pr_type == "partition":
                    tmp = PatternPartition.strictFromDict(r)
                elif pr_type == "database":
                    tmp = PatternDatabase.fromDict(r)
                else:
                    tmp = PatternSearch.fromDict(r)
            self.requests.append(tmp)

        if len(self.requests) == 0:
            raise ValueError("No requests found.")
        #print "PatternMining._prepare_request done"

    def _get_ngramdb_for_request(self, request, fix_errors=True):
        """helper function that retrieves a NGramDatabase from the
            NGramDataProvider.

            Args:
                request (PatternRequest object):
            Returns:
                NGramDataBase object
        """
        try:
            simul = request.simul
        except:
            simul = False

        try:
            maxN = request.maxN
        except:
            maxN = self.maxN

        build_db = True
        if request.type == "search":
            build_db = False

        if simul:
            try:
                order = request.order
            except:
                order = 1
            #print "_get_ngramdb_for_request, order", request.order
            ndb = self.ndp.simulate_database(transform=request.transform, maxN=maxN, order=order, cache=True)
        else:
            ndb = self.ndp.get_database(transform=request.transform, build_db=build_db, maxN=maxN, fix_errors=fix_errors)
        return ndb


    def _process_secondary(self, request, primary_request, result, verbose):
        #print "Secondary processing..."
        #print result
        iOff1, lOff1 = NGramDataProvider.get_transform_offsets(request.transform)
        iOff2, lOff2 = NGramDataProvider.get_transform_offsets(primary_request.transform)
        iOff = iOff1 - iOff2
        lOff = lOff2 - lOff1
        #print "Sec offsets:", iOff1, lOff1
        #print "Prm offsets:", iOff2, lOff2
        #print "Net offets:", iOff, lOff
        ndb = self._get_ngramdb_for_request(request, fix_errors=False)
        nrefrep = ndb.getRep()
        #print nrefrep
        nr = nrefrep.filter_by_ngrams(result, lengthOffset=lOff, indexOffset=iOff)
        #print "-"*60
        #print "Filtered rep"
        #print nr
        #print "-"*60
        red_ndb = NGramDatabase(nr, maxN=30, transform=request.transform, build=False, verbose=self.verbose, proc_hooks=self.proc_hooks)
        tmp = request.process(red_ndb, verbose=verbose)
        #print "="*60
        #print "Secondary results"
        #print tmp
        #print "="*60
        npos_filter = []
        for t in tmp:
            for pos in t:
                npos = nr.getKeyFromId(pos.seqid)
                npos_filter.append(npos)

        ret = result.filter_by_positions(npos_filter, mode=request.operation)
        #ret.setPositionFreq()
        ret.setPositionFrequencies(nrefrep=nrefrep)
        #print len(npos_filter), result.positionCount(), ret.positionCount()
        return ret

    def process(self, verbose=None):
        self.ndp.read_melodies()
        results = []
        if verbose == None:
            verbose = self.verbose

        for i, r in enumerate(self.requests):
            start = time.process_time()
            if  self.proc_hooks != None and r.type in self.proc_hooks:
                r.proc_func = self.proc_hooks[r.type]

            ndb = self._get_ngramdb_for_request(r)
            tmp = r.process(ndb, verbose=verbose)

            if r.secondary and r.secondary.operation != "ignore":
                tmp = self._process_secondary(request=r.secondary, result=tmp, primary_request=r, verbose=verbose)
            else:
                if isinstance(tmp, NGramBag):
                    tmp.setPositionFrequencies(nrefrep=ndb.getRep())

            if isinstance(tmp, NGramDatabase) or len(tmp):
                results.append(PatternMiningResult(r, tmp))
            else:
                if r.type == "search" and self.verbose:
                    print("No matching patterns found!")
            if verbose:
                print("Finished in {} s".format(round(time.process_time()-start, 3)))
                print("-"*60)

        return results
