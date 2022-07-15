""" Class implementation of Beatometer"""
from functools import cmp_to_key

from melospy.basic_representations.accents import *
from melospy.basic_representations.beatometer_param import *
from melospy.basic_representations.gaussification import *
from melospy.basic_representations.jm_util import (diff, get_huron_code_raw, purify_period_track,
                                                   rayleigh2)
from melospy.basic_representations.meter_grid import *
from melospy.basic_representations.metrical_annotator import *
from melospy.basic_representations.note_track import *
from melospy.basic_representations.rhythm import *


class BeatometerDebugParams(object):

    def __init__(self, beat=False,
                 phase=False,
                 period=False,
                 framing=False,
                 glueing=False,
                 fillUp=False):
        self.beat = beat
        self.phase = phase
        self.period = period
        self.framing = framing
        self.glueing = glueing
        self.fillUp = fillUp

    def all_on(self):
        for k in self.__dict__:
            self.__dict__[k] = True

    def all_off(self):
        for k in self.__dict__:
            self.__dict__[k] = False

    def set_gaussbeat(self, val):
        self.beat = val
        self.phase = val
        self.period = val

    def gauss_beat_on(self):
        self.set_gaussbeat(True)

    def gauss_beat_off(self):
        self.set_gaussbeat(False)

    def set_beatometer(self, val):
        self.framing = val
        self.glueing = val
        self.fillUp = val

    def beatometer_off(self):
        self.set_beatometer(False)

    def beatometer_on(self):
        self.set_beatometer(True)

    def __str__(self):
        ret = "\n".join([str((k, self.__dict__[k])) for k in self.__dict__])
        return ret

class PeriodEstimate(object):
    def __init__(self, beat_dur=None, period=None, weight=None, force=False):
        self.beat_dur = beat_dur
        self.period = period
        self.weight = weight
        self.force = force

    def __str__(self):
        if self.beat_dur == None:
            return "T:N/A, P:N/A, w:N/A, force=N/A"
        return "T:{:0.3f}, P:{}, w:{}, force:{}".format(round(self.beat_dur, 3), self.period, round(self.weight, 3), self.force)

    def __repr__(self):
        if self.beat_dur == None:
            return "T:N/A, P:N/A, w:N/A, force:N/A"
        return self.__str__()

class BeatometerEstimate(PeriodEstimate):
    def __init__(self, beat_dur=None, beat_phase=None, period=None, meter_phase=None, weight=None, t0=None):
        PeriodEstimate.__init__(self, beat_dur, period, weight)
        self.beat_phase = beat_phase
        self.meter_phase = meter_phase
        self.t0 = t0

    def __str__(self):
        if self.beat_dur == None:
            return "(T: N/A, P: N/A, beat-phi: N/A, meter-phi: N/A, w: N/A)"
        if self.t0 != None:
            return "(t0:{}, T:{:0.3f}, P:{}, b-phi:{}, m-phi:{}, w: {})".format(round(self.t0, 3), round(self.beat_dur, 3), self.period, round(self.beat_phase, 3), round(self.meter_phase, 3), round(self.weight, 3))
        return "(T:{:0.3f}, P:{}, b-phi:{}, m-phi:{}, w:{})".format(round(self.beat_dur, 3), self.period, round(self.beat_phase, 3), round(self.meter_phase, 3), round(self.weight, 3))

    def __repr__(self):
        if self.beat_dur == None:
            return "T: N/A, P: N/A, b-phi: N/A, m-phi: N/A, w: N/A"
        return self.__str__()

class TempoPreference(object):
    def __init__(self, spontaneous_tempo=.5, beta=2):
        self.t0 = spontaneous_tempo
        self.beta = beta
        self.type="lognormal"

    def lognormal(self, v):
        if float_equal(v[0], 0.):
            return (v[0], 0.)
        return (v[0], v[1]*exp(-self.beta*log(v[0]/self.t0, 2)*log(v[0]/self.t0, 2)))

    def __call__(self, v):
        if self.type == "lognormal":
            return self.lognormal(v)
        return (v[0], 1)

class Gauss(object):
    def __init__(self, mu=0., sigma=1., factor=1.):
        self.mu = mu
        self.sigma = sigma
        self.factor = factor
        self.type="normal"

    def __call__(self, v):
        if self.type=="normal":
            kern = (v[0]-self.mu)/self.sigma
            return (v[0], self.factor*v[1]*exp(-kern*kern))
        return 1

class GaussBeat(object):
    """Beatometer is a class to annotate a given rhythm with a meter grid.
       Several algorithms can be used
    """
    def_sigma = .04
    def_wr = {"method":"gauss-standard",
              "params":{
                         "a_min":2,
                         "a_maj":3,
                         "sigma":def_sigma
                        }
             }

    def_period_probs_uniform   = {}
    def_period_probs_folk      = {2:.32, 3:.24, 4:.27}
    def_period_probs_jazz      = {2:.01, 3:.01, 4:.90, 5:.01}

    def __init__(self, rhythm, params=None, debug=None):
        if debug == None:
            debug = BeatometerDebugParams()

        self.debug = debug
        self.rhythm =rhythm
        self.beat_track = []
        self.period_estimates = []
        # lots of parameters
        self.sigma  = params.sigma
        self.dT     = params.deltaT
        self.maxL   = params.subjective_presence
        self.wr     = params.weight_rules
        self.t0     = params.spontaneous_tempo
        self.beta   = params.beta
        self.domain = params.domain
        self.min_tempo = params.min_tempo
        self.max_grad_cut = params.max_grad_cut
        self.gauss = Gaussification(rhythm.onsets, sigma=self.sigma, weightRules=self.wr)
        self.autocorr = self.gauss.autocorrelation(self.maxL, self.dT)

    def setRhythm(self, rhythm):
        self.rhythm = rhythm

    def getWeights(self):
        return self.gauss.weights

    def getPeriodProbs(self, period):
        prob = {}
        if self.domain=="uniform":
            prob = self.def_period_probs_uniform
        elif self.domain=="folk":
            prob = self.def_period_probs_folk
        elif self.domain=="jazz":
            prob = self.def_period_probs_jazz
        try:
            p = prob[period]
        except:
            p = .01
        return p

    def estimateBeatPhase(self, beat_dur, debugMsg="Beat"):
        N = int(round(self.rhythm.totalDuration()/beat_dur) + 1)
        tmp_sigma = self.sigma
        beat_track = Gaussification([i*beat_dur for i in range(N)], sigma=tmp_sigma, deltaT=self.dT, weightRules="const")

        start = self.rhythm.startTime()-2*self.sigma
        end = start + beat_dur + 4*self.sigma
        if self.debug.phase:
            print("="*40)
            print("{} phase estimation".format(debugMsg))
            print("="*40)
            print("Rhythm dur: {}, beat dur:{}, #beats:{}, start={}, end={}".format(self.rhythm.totalDuration(), beat_dur, N, start, end))
        self.gauss.sigma = tmp_sigma
        cc = self.gauss.crosscorrelation(beat_track, start=start, end=end, deltaT=self.dT)
        peaks = cc.maxvals()
        peaks.sortByVal(reverse=True)
        if self.debug.phase:
            print("CrossCorr Peaks:\n{}".format(peaks))
        try:
            phase = peaks.maxvals()[0]
        except:
            #print "Peaks:", peaks
            #cc.writeCSV("cc_empty.csv")
            return peaks[0]
        if self.debug.phase:
            print("Phase estimation: ({}, {})".format(round(phase[0], 3), round(phase[1], 3)))
        if self.debug.phase:
            cc.writeCSV("cc_test_{}.csv".format(debugMsg))
            print("Written cross correlation to cc_test_{}.csv".format(debugMsg))
            self.gauss.gaussify()
            self.gauss.writeCSV("tl_test.csv")
            beat_track1 = Gaussification([(i*beat_dur + phase[0]) for i in range(N)], sigma=self.sigma, deltaT=self.dT, weightRules="const")
            beat_track1.gaussify()
            beat_track1.writeCSV("beats_test.csv")
        return phase

    def estimatePeriod(self, beat_dur, period_suggestion=None):
        candidates = []

        if period_suggestion != None and period_suggestion.force:
            candidates.append(period_suggestion)
            return candidates

        max_v = self.autocorr.maxsals()

        if max_v.isEmpty():
            if period_suggestion != None:
                candidates.append(period_suggestion)
            return candidates
        maxN = int(round(max_v[-1][0]/beat_dur))+1
        if self.debug.period:
            print("="*40)
            print("GaussBeat period estimation")
            print("="*40)
            print("maxN=", maxN)
            print("period suggestion=", period_suggestion)
        if maxN == 2:
            if period_suggestion != None:
                candidates.append(period_suggestion)
            return candidates

        for period in range(2, maxN):
            apriori = self.getPeriodProbs(period)
            period_pref = Gauss(mu=period*beat_dur, sigma=period*self.sigma, factor=apriori)
            if self.debug.period:
                print("-"*40)
                print("beat_dur={}, mu={}, N={}, p={}".format(beat_dur, period*beat_dur, period, apriori))
            weighted = max_v.apply(period_pref)
            best = weighted.maxvals()
            if self.debug.period:
                print("Raw:\n{}".format(max_v))
                print("Weighted:\n{}".format(weighted))
                print("Best:\n{}".format(best))
            if not best.isEmpty():
                w = best[0][1]
                if period_suggestion != None and period_suggestion.period==period:
                    #print "Old: {}, new:{}\n".format(w, period_suggestion.weight)
                    w = period_suggestion.weight
                candidates.append(PeriodEstimate(beat_dur, period, w))
            else:
                if period_suggestion != None:
                    candidates.append(period_suggestion)


        if len(candidates)==0:
            return []

        candidates.sort(key=cmp_to_key(lambda x, y: get_huron_code_raw(x.weight, y.weight)))
        if self.debug.period:
            print("*"*40)
            print("Period Candidates for T={:0.3f}".format(beat_dur))
            print("\n".join([str(p) for p in candidates]))
            print("*"*40)

        return candidates

    def calculate(self, period_suggestion=None):
        self.beat_track= []
        max_v = self.autocorr.maxsals(mode="relaxed")
        #self.debugBeat = True
        if self.debug.beat:
            print("="*40)
            print("GaussBeat calculate")
            print("="*40)
            print("AutoCorr Peaks:\n", max_v)
        #print len(max_v)
        max_v = max_v.apply(TempoPreference(self.t0, self.beta))
        beat_est = max_v.maxvals(as_ts=True).sortByVal(reverse=True)

        if self.debug.beat:
            print("AutoCorr Peaks (weighted):\n", max_v)
            print("Beat Estimate:\n", beat_est)

        if len(beat_est)==0:
            self.beat_track.append(BeatometerEstimate())
            return self.beat_track
        cand =[]
        beat_dur = 0
        vals = []
        last_w = beat_est[0][1]
        for est in beat_est:
            if self.debug.beat:
                print("Testing estimate: {:0.3f}".format(est[0]))
            beat_dur = est[0]
            w = est[1]
            if abs((w-last_w)/last_w)>self.max_grad_cut:
                if self.debug.beat:
                    #print "Weight: {:0.3f}, Last: {:0.3f}. Rel diff:{:0.3f}".format(w, last_w, (w-last_w)/last_w)
                    print("Peak to low (rel. diff={:0.3f}), bailing out.".format((w-last_w)/last_w))
                break
            last_w = w
            while beat_dur > (self.min_tempo + .001):
                if self.debug.beat:
                    print("Tempo exceeds min. tempo {}s. Try doubling -> {}s".format(self.min_tempo, beat_dur/2))
                beat_dur = beat_dur/2
            while len(cand) == 0:
                cand = self.estimatePeriod(beat_dur, period_suggestion)
                if len(cand) > 0:
                    vals.append(cand[0])
                    break
                else:
                    if beat_dur >= 2*self.sigma:
                        if self.debug.beat:
                            print("No period found for {}s. Try doubling -> {}s".format(beat_dur, beat_dur/2))
                        beat_dur = beat_dur / 2
                    else:
                        break
        if len(vals) == 0:
            self.beat_track.append(BeatometerEstimate())
            return self.beat_track
        vals.sort(key=cmp_to_key(lambda x, y: get_huron_code_raw(x.weight, y.weight)))
        self.period_estimates = vals

        for v in vals:
            beat_phase = self.estimateBeatPhase(v.beat_dur)[0]
            meter_phase = self.estimateBeatPhase(v.period*v.beat_dur, debugMsg="Meter")[0]
            be = BeatometerEstimate(v.beat_dur, beat_phase, v.period, meter_phase, v.weight)
            self.beat_track.append(be)
        return self.beat_track

    def writeTimeLine(self, filename, delimiter=";", header=[]):
        if self.gauss.isEmpty():
            self.gauss.gaussify()
        self.gauss.writeCSV(filename, delimiter=delimiter, header=header)

    def writeAutoCorrelation(self, filename, delimiter=";", header=[]):
        self.autocorr.writeCSV(filename, delimiter=delimiter, header=header)

class Beatometer(object):
    """Beatometer is a class to annotate a given rhythm with a meter grid.
       Several algorithms can be used
    """
    def __init__(self, rhythm=None, params=None, debug=None):
        if debug == None:
            debug = BeatometerDebugParams()

        self.debug = debug
        self.__rhythm = rhythm
        self.setParams(params)
        self.glob_candidates = []

    def setRhythm(self, rhythm):
        if rhythm is None or isinstance(rhythm, Rhythm):
            self.__rhythm = rhythm
        else:
            raise TypeError("Expected 'Rhythm' object or 'None'")
        return self

    def getRhythm(self):
        return self.__rhythm

    def setParams(self, params):
        #if not isinstance(params, BeatometerParameters):
        #    raise ValueError("Expected BeatometerParameters, got {}".format(type(params)))
        self.__params = params
        return self

    def getParams(self):
        return self.__params

    def removeShorties(self, rhythm, threshold=.05):
        if rhythm == None or len(rhythm)==0:
            raise ValueError("No rhythm specified")
        iois = rhythm.getIOIs()
        shorties = [i for i in range(len(iois)) if iois[i]<threshold]
        return rhythm.without(shorties)

    def fillUpBeats(self, beat_track, glue_threshold=1.8):
        decay = 1
        onsets = beat_track.times

        if len(onsets)<=2:
            return beat_track

        filled = [beat_track[0]]
        iois = diff(onsets)
        anchor = iois[0]

        for i in range(1, len(iois)):
            if self.debug.fillUp:
                print("-"*40)
                print("onset[i]={}, onset[i+1]={}, iois[i]={}, anchor={}".format(onsets[i], onsets[i+1], iois[i], anchor))
            filled.append(beat_track[i])

            if iois[i] > glue_threshold*anchor:
                N = int(round(iois[i]/anchor))
                assert(N>1)
                bd = iois[i]/N
                offset = onsets[i]
                if self.debug.fillUp:
                    print("bd={}, N={}, offset={}".format(bd, N, offset))
                tmp_beats = [(bd*i + offset, -1) for i in range(1, N)]
                filled.extend(tmp_beats)
                if self.debug.fillUp:
                    print("Added {} beats".format(len(tmp_beats)))
            else:
                if self.debug.fillUp and decay<1:
                    print("Old Anchor: {}, New_anchor:{} ".format(anchor, decay*anchor + (1-decay)*iois[i]))
                anchor = decay*anchor + (1-decay)*iois[i]

        #add last beat, too
        filled.append(beat_track[-1])
        if self.debug.fillUp:
            onsets = [t for t, v in filled]
            print("IOIs:")
            print(", ".join([str(round(ioi, 3)) for ioi in diff(onsets)]))
        return TimeSeries(filled)

    def glueFrames(self, estimates, window_size, glue_sigma=.04, glue_threshold=1.8, deltaT=.01, period_suggestion=None):
        """ Method to glue frames each having different beat, meter phase estimates
        """
        if self.debug.glueing:
            print("="*40)
            print("Beatometer glueFrames")
            if period_suggestion != None:
                print("Period suggestion", period_suggestion)
            print("="*40)
        onsets =[ ]
        meter_phases = []
        periods = []
        frame_starts = []

        #print "len(estimates)", len(estimates)

        #prepare data
        #calculate beat onsets for every frame
        # store them in one big list ()
        for est in estimates:
            if est.beat_dur == None:
                continue
            N = int(round((window_size-est.beat_phase+est.t0)/est.beat_dur))
            tmp_onsets = [i*est.beat_dur + est.beat_phase for i in range(-1, N+1)]
            #print "t0:{}, beat_dur:{}, beat_phase:{}, N:{}, N*beat_dur:{}, wt:{}".format(t0, beat_dur, beat_phase, N, N*beat_dur, window_size)
            onsets.extend(tmp_onsets)
            meter_phases.append(est.meter_phase)
            periods.append(est.period)
            frame_starts.append(est.t0)

        if len(onsets)==0:
            return []

        #join onsets using some clever tricks
        #first: get rid of dublets
        onsets = sorted([e for e in set(onsets)])

        #second: sort them

        #third: submit the onsets to a gaussification
        #very close peaks will end up in a broad peak,
        g = Gaussification(onsets, sigma=glue_sigma, deltaT=deltaT, weightRules="const")
        g.gaussify()
        #so peak picking will finde kind of an interpolation between two close beats
        max_v= g.maxvals()
        #print len(max_v)

        #unfortunately it can happen, that sometime "holes" occur,
        #fill them up with some intermediate values
        max_v = self.fillUpBeats(max_v, glue_threshold)

        if len(max_v) == 0:
            if self.debug.glueing:
                print("WARNNIG: No common beats found!")
            return []

        #now phases and periods of the single frames have to be joined
        #in some reasonable way
        signatures = []
        cur_frame = 0
        cur_period = periods[0]
        last_period = 0

        offset = max_v.findClosest(meter_phases[0]) % cur_period
        frame_starts.append(frame_starts[-1]+window_size)
        frame_t = frame_starts[0]

        #enumerate over beats
        for i, bt in enumerate(max_v.times):
            #print i, round(bt, 3), cur_period, offset, last_period
            #Do have a "one" of a new measure?
            #add new signatures if period has changed
            if (i % cur_period) == offset and last_period != cur_period:
                #sig = str(cur_period) + "/4"
                signatures.append((i, cur_period))
                last_period = cur_period
                #print "Gotcha", len(signatures)
            #are changing fames?
            #if yes update running vars
            if bt >= frame_t:
                #print "Bt: {}, frame_t:{}, cur_frame:{}, cur_period:{}".format(bt, frame_t, cur_frame, cur_period)
                cur_frame += 1
                #last beat might be behind last frame due to round off errors
                #just break, nothing bad can happen
                try:
                    cur_period = periods[cur_frame-1]
                    frame_t = frame_starts[cur_frame]
                except:
                    break
                    #print cur_frame-1, len(periods)
                    #print cur_frame, len(frame_starts)

        if len(signatures)==0:
            print("WARNNIG: No signatures found!")
            return []

        if self.debug.glueing:
            print("Signatures: {}".format(signatures))
        signatures = purify_period_track(signatures)
        if self.debug.glueing:
            print("Purified: {}".format(signatures))
        beat_track = max_v.toRhythm()
        beat_track.setValues(val=None)
        for i, sig in signatures:
            beat_track[i].value = Signature(sig, 4)
        #print beat_track
        return beat_track

    def calculateFrames(self, rhythm, params, window_size=8., hop_size=1.0, period_suggestion=None):
        start = rhythm.startTime()
        end   = rhythm.endTime()
        t = start
        if window_size <= 0:
            wt = end-start + 1
            hop_t = wt
        else:
            wt = window_size
            hop_t = hop_size * wt
        estimates = []
        beat_durs = []
        if self.debug.framing:
            print("="*40)
            print("Beatometer calculateFrames")
            print("Start: {}, end : {}, wt: {}, hop: {}".format(start, end, wt, hop_t))
            if period_suggestion:
                print("Period suggestion: ", period_suggestion)
            print("="*40)

        while t < end:
            r = rhythm.sliceByTime(t, t + wt)
            if r == None:
                t += hop_t
                continue
            bm = GaussBeat(r, params, debug=self.debug)
            est = bm.calculate(period_suggestion=period_suggestion)
            if params.propagate and not params.single_meter and len(bm.period_estimates)>0:
                period_suggestion = bm.period_estimates[0]
                if self.debug.framing:
                    print(">>>Period_suggestion: ", period_suggestion)

            if self.debug.framing:
                print("+"*60)
                print("Framestart: {}, #cand: {}".format(t, len(est)))

            if len(est)>0:
                first_est = est[0]
                first_est.t0 = t
                estimates.append(first_est)
                beat_durs.append(first_est.beat_dur)
                if self.debug.framing:
                    #print "....Beat_dur: {}, #period:{}".format(first_est.beat_dur, period)
                    if len(est)>1:
                        print("\n...".join([str(e) for e in est]))
                    else:
                        print("...", est)
                    print("+"*60)
            #sys.exit(0)
            t += hop_t

        beats = self.glueFrames(estimates, wt, params.glue_sigma, params.glue_threshold, period_suggestion=period_suggestion)
        if len(beats) == 0:
            if self.debug.framing:
                print("WARNING: Empty beat track!")
            return beats

        while rhythm[-1].onset > beats[-1].onset:
            re = RhythmEvent(beats[-1].onset+beats.getIOIs()[-1])
            beats.append(re)

        while rhythm[0].onset < beats[0].onset:
            re = RhythmEvent(beats[0].onset-beats.getIOIs()[0])
            beats.insert(re)

        # beats.writeCSV("beats_debug.csv", delimiter=";", header=["t", "val"])

        return beats

    def calculate(self, method="dummy", rhythm=None, params=None):
        """Returns meter annotated beat_track
        """
        if rhythm == None:
            rhythm = self.__rhythm

        if rhythm == None:
            raise ValueError("No rhythm specified")

        if params == None:
            params = self.__params
        candidates = []
        self.glob_candidates  = []

        if method == "dummy":
            return candidates
        elif method=="gaussification":
            try:
                if params.min_ioi > 0.0:
                    rhythm = self.removeShorties(rhythm, params.min_ioi)
            except:
                pass
            period_suggestion = None
            if params.single_meter and params.window_size > 0:
                bm = GaussBeat(rhythm, params, debug=self.debug)
                bm.calculate()
                # bm.writeTimeLine("tl_debug.csv")
                # bm.writeAutoCorrelation("autocor_debug.csv")
                try:
                    period_suggestion = bm.period_estimates[0]
                except:
                    period_suggestion = PeriodEstimate(.5, 2, 1.0)

                period_suggestion.force = True
            candidates  = self.calculateFrames(rhythm, params, window_size=params.window_size, hop_size=params.hop_size, period_suggestion=period_suggestion)
        else:
            raise ValueError("Invalid beat annotation method {} specified".format(method))
        return  candidates

    def getDefaultParameters(self, params=None):

        if params == None:
            params = {"beatometer": None, "flexq": None}
        if not "beatometer" in params or params["beatometer"] == None:
            params["beatometer"]  = BeatometerParameters()
        if not "flexq" in params or params["flexq"] == None:
            params["flexq"]  = FlexQParams()

        return params

    def annotate(self, method="dummy", rhythm=None, params=None):
        if rhythm == None:
            r = self.__rhythm

        if r == None:
            raise ValueError("No rhythm specified")

        if params == None:
            params = self.__params

        mg = None

        if method == "dummy":
            mg = MeterGrid.createIsoMeter(len(r))
        elif method == "gaussification":
            if len(r) == 1:
                mg = MeterGrid.createIsoMeter(len(r), signature="1/4")
                return mg
            params = self.getDefaultParameters(params)
            beat_track = self.calculate(method, r, params["beatometer"])
            #if no beat track was found, probably degeneration is present
            #provide minimal spanning dummy beat ttrack
            #print r.onsets, beat_track.onsets
            if len(beat_track) == 0:
                tot_dur = r.totalDuration()
                if tot_dur<.5:
                    N = 2
                else:
                    N = int(round(tot_dur/.5)+1)
                beat_track = Rhythm.beat_track(N=N, signature="1/4", start=r[0].onset, ioi=0.5)
                #print "Rhythm:\n ", r
                #print "Beat:\n", beat_track
                #print tot_dur, N, len(beat_track)
            #beat_track.magneticMove(r, max_dist=.10)
            if isinstance(r, Rhythm):
                #print beat_track

                ma = MetricalAnnotator(r, beat_track, params=params["flexq"])
                mg = ma.annotate()
                #try:
                #except Exception, e:
                    #msg = "Error during metrical annotation: {}".format(e.args[0])
                    #raise Exception(msg)
            #do some fancy stuff
        else:
            raise ValueError("Invalid beat annotation method {} specified".format(method))
        return mg

    rhythm    = property(getRhythm, setRhythm)
    params    = property(getParams, setParams)
