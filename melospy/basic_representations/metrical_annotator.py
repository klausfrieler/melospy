""" Class implementation of MetricalAnnotator"""

from melospy.basic_representations.annotated_beat_track import *
from melospy.basic_representations.jm_stats import mean, sd, var
from melospy.basic_representations.jm_util import break_ties_causal, diff
from melospy.basic_representations.meter_grid import *
from melospy.basic_representations.metrical_annotation_param import *
from melospy.basic_representations.note_track import *
from melospy.basic_representations.rhythm import *


class MetricalAnnotator(object):

    def __init__(self, noteTrack=None, beatTrack=None, params=None):
        #if not isinstance(noteTrack, NoteTrack):
        #    raise TypeError("Expected 'NoteTrack' object'")

        self.__notetrack = noteTrack
        self.setBeatTrack(beatTrack)
        self.setParams(params)


    def setNoteTrack(self, noteTrack):
        if noteTrack is None or isinstance(beatTrack, NoteTrack):
            #use a deep copy, you'll never know...
            self.__notetrack= noteTrack.clone()
        else:
            raise TypeError("Expected 'Rhythm' object or 'None'")
        return self

    def getNoteTrack(self):
        return self.__noteTrack

    def setBeatTrack(self, beatTrack):
        if beatTrack is None:
            self.__beattrack = beatTrack
        elif isinstance(beatTrack, Rhythm):
            #use a deep copy, you'll never know...
            self.__beattrack = beatTrack.clone()
        else:
            raise TypeError("Expected 'Rhythm' object or 'None'. Got: {}".format(type(beatTrack)))
        return self

    def getBeatTrack(self):
        return self.__beattrack

    def setParams(self, params):

        if params is None:
            #use cool defaults, baby
            self.__params = FlexQParams()
        elif isinstance(params, FlexQParams):
            self.__params = params
        else:
            raise TypeError("Expected 'FlexQParams' object or 'None'. Got:{}.".format(type(params)))
        return self

    def getParams(self):
        return self.__params

    def closestGridPoints(self, x, grid, spread=True, scale=.85, debug=False):
        """Return a list of indices of closest gridpoint for vector x"""
        #type_check(x, list)
        #type_check(grid, list)
        #type_check(scale, float)
        debug = False
        spread = bool(spread)
        if scale <= 0.0 or scale > 1.0:
            raise ValueError("Scale must be a value between 0 and 1")
        #type_check_vec(x, (int, float))
        #type_check_vec(grid, (int, float))

        ret = [0 for _ in range(len(x))]
        raw_ret = [0 for _ in range(len(x))]
        offset = 0
        #one grid point, yeah, well, the only possibility
        if len(grid) == 1:
            return [0]
        N = len(grid)
        #we need a right closed grid
        if float(grid[-1]) != 1.0:
            grid.append(1.0)

        if debug:
            print("\nTesting vector \n{}\n with grid\n{}".format(x, grid))
            print("================================")

        for j in range(len(x)):
            if debug: print("Testing element {} with val {}".format(j, x[j]))
            if x[j] < grid[0]:
                ret[j] = 0
                raw_ret[j] = 0
                if debug: print("Left out of range: 0")
                #if it is the second or a later one, we have to propagate!
                if j > 0 and ret[j] == ret[j-1]:
                    ret[j] = min_max(0, ret[j]+1, N)
                    offset = offset+1
                    if debug: print("Propagate idx to {}.".format(ret[j]))
                continue
            if x[j] >= grid[-1]:
                ret[j] = N
                raw_ret[j] = N
                if debug: print("Right out of range. Value: {}".format(ret[j]))
                continue
            for i in range(N):
                if x[j] >= grid[i] and x[j] < grid[i+1]:
                    #if debug: print "x:{}, grid[i]:{} grid[i+1]:{}".format(x[j], grid[i], grid[i+1])
                    if debug: print("x:{} in  [{}, {}]".format(x[j], i, i+1))
                    eff_grid_size = scale * (grid[i+1]-grid[i])
                    #if debug: print "Gridsize: {}, scale:{}".format(eff_grid_size, scale)
                    diff_left = abs(x[j]-grid[i])
                    diff_right= abs(x[j]-grid[i+1])
                    rel_diff = abs(diff_left-diff_right)/abs(diff_left+diff_right)

                    #if debug: print "Diff left: {}, diff right:{}, rel. diff: {}".format(diff_left, diff_right, round(rel_diff, 3))

                    if diff_left < diff_right or (diff_right < diff_left and rel_diff<.1):
                        ret[j] = min_max(i + offset, 0, N)
                        raw_ret[j] = i
                        if debug: print("Found left at idx {} -> {}".format(i, ret[j]))
                    else:
                        if debug and rel_diff<.13: print("Diff left: {}, diff right:{}, rel. diff: {}".format(diff_left, diff_right, round(rel_diff, 3)))
                        ret[j] = min_max(i + 1 + offset, 0, N)
                        raw_ret[j] = i+1
                        if debug: print("Found right at idx {} -> {}".format(i, ret[j]))

                    if spread and j > 0 and ret[j] <= ret[j-1]:
                        ret[j] = min_max(ret[j]+1, 0, N)
                        offset = offset+1
                        if debug: print("Propagate idx to {}. New offset {}".format(ret[j], offset))

                    if offset > 0 and j > 0 and ret[j]>(ret[j-1]+1):
                        #offset -= 1
                        if debug: print("New offset {}.".format(offset))
                    break
                if j > 0 and ret[j] == ret[j-1]:
                    ret[j] = min_max(0, ret[j]+1, N)
                    if debug: print("Propagate idx to {}.".format(ret[j]))
                #print j, offset, ret, ret[j]


        #print "ret", ret, N
        #print "raw_ret", raw_ret, N
        #print "resolved raw", break_ties_causal(raw_ret), N
        return break_ties_causal(raw_ret)

    def quantize(self, events, rhythmThreshold, debug=False, max_division=None):
        """ here the magic is done, assumes normalized events!"""
        debug = False
        #preparation
        #short hands
        a = self.params.getValue("oddDivisionPenalty")
        b = self.params.getValue("mismatchPenalty")
        c = self.params.getValue("distPenalty")
        d = self.params.getValue("spreadPenalty")
        scale = self.params.getValue("scaleFactor")
        N = len(events)
        try:
            onsets = events.getOnsets()
        except:
            onsets = events
        # find maximum grid size
        # maximum size is either rhythmThreshold or the smallest IOI found in the onset
        # better check for very close events first (possibly nasty doublets) before entering this function
        #old Version:
        #minIOI = min([onsets[0], abs(1-onsets[-1])] +  diff(onsets))
        if not float_equal(onsets[0], 0):
            minIOI = min([onsets[0], abs(1-onsets[-1])] +  diff(onsets))
        else:
            minIOI = min([abs(1-onsets[-1])] +  diff(onsets))
        minIOI = max(minIOI,  rhythmThreshold)
        if minIOI == 0:
            #print diff(onsets)
            raise ValueError("Invalid minimum IOI of zero-value found. Check parameters")
        maxN = int(round(1/minIOI))
        if float_equal(rhythmThreshold, 0) and  max_division is not None:
            maxN = min(maxN, max_division)
        if maxN == N:
            maxN = N + 3
        #print "Events: {}, minIOI = {} maxN = {}".format(onsets, minIOI, maxN)

        if debug: print("\n\n=============================================\nEnter Quantize")
        if debug: print("rhythmThreshold: {}, maxN: {}, minIOI: {}".format(rhythmThreshold, maxN, minIOI))

        #more preparation
        cost = 0
        minCost = 1e32

        bestGrid = N
        bestPositions  = []
        bestDist = 0
        for M in range(N, maxN+1):
            #optimization: Due to the nature of the cost function at some higher N the cost cannot get less, so bail out
            if self.params.getValue("optimize") and b*(M-N)>minCost:
                if debug: print("Break! b:{}, M:{}, N:{}, b*(M-N)= {}, minCost:{}".format(b, M, N, b*(M-N), minCost))
                break

            # calculate the grid...
            grid = constant_grid(M)
            #... and found closestPositions (as indices into the grid lis)
            if debug: print("\n\n=============================================\nCheck grid {}".format(M))
            positions = self.closestGridPoints(onsets,
                                               grid,
                                               spread=True,
                                               scale=scale,
                                               debug=debug)

            spread = 0
            dv = None
            #if no position is outside the grid, calculate euclidean distance and standard deviation
            if max(positions) < M:
                # calculate vector of distances of onsets to optimal grid points
                dv = diff_vec([grid[i] for i in positions], onsets)
                # the overrall euclidean length of the distance vector
                dist = sqrt(sum([x*x for x in dv]))
                #print var(dv)
                if len(dv) > 1:
                    spread =  sd(dv)
            else:
                #really high punishment, yes.
                dist = 1e32

            #calculate a penalty if the division is an evil odd number
            penal_odd = 0
            #old:
            #if M == 1 or  M % 3 == 0 or  M % 5 == 0 or M % 7 == 0:
            #    penal_odd = 1

            #new 18.12.2015
            if M % 2 == 1:
                penal_odd = 1

            #be less harsh with single and triple divisions
            if M == 1 or  M == 3:
                penal_odd = .5


            #total costs: oddDivisionsPenalty + mismatchPenalty + distancePenaly + spreadPenalty
            cost = a * penal_odd + b*(M-N) + c * dist + d * spread
            #debug = True
            if debug: print("M: {}, cost: {}".format(M, cost))
            if debug: print("penal_odd: {}, (M-N):{}, dist: {}, spread:{}".format(penal_odd, M-N, dist, spread))
            if debug: print("a*penal_odd: {}, b*(M-N): {}, c*dist:{}, d*spread:{}".format(a * penal_odd, b*(M-N), c * dist, d * spread ))
            #debug = False
            #minimum picking
            #if equal cost prefer smaller distances,
            #if same distances, prefer smaller grid
            newBest = False
            if float_equal(cost, minCost):
                if float_equal(dist, bestDist):
                    if M < bestGrid:
                        newBest = True

                elif dist < bestDist:
                    newBest = True
            elif cost < minCost:
                newBest = True

            if newBest:
                minCost = cost
                bestGrid = M
                bestPositions = positions
                bestDist = dist

        #that's all, folks, the show is over
        return bestGrid, bestPositions


    def annotate(self, startBar=1, startBeat=1):
        """Calculates metrical positions for the note track events from a beat track.
          * The beat track has to be a Rhythm object which should have signature events attached for tracking meter changes.
            First event should have signature value, if not found, 4/4 are assumed
          * startBar and start Beat are global offsets for the mnetrical annotation
          * Returns a 'MeterGrid' object
        """
        debug = False

        if self.__beattrack is None or self.__beattrack.isEmpty():
            raise ValueError("'beatTrack' empty, this cannot work, dude.")

        annotated_beat_track = True if isinstance(self.__beattrack, AnnotatedBeatTrack) else False
        #print "annotated_beat_track", annotated_beat_track
        for e in self.__notetrack:
            #TODO: Just warn user and continue using only note events in scope of beat track
            if e.getOnsetSec()<(self.__beattrack[0].getOnsetSec()):
                raise ValueError("Beat track does not cover note track, buddy. Event at {} s is before first beat.".format(round(e.getOnsetSec(), 4)))

            if e.getOnsetSec()>(self.__beattrack[-1].getOnsetSec()):
                raise ValueError("Beat track does not cover note track, buddy. Event at {} s is past last beat.".format(round(e.getOnsetSec(), 4)))

        tolerance = self.params.getValue("tolerance")
        #prepare beat track
        bt = self.__beattrack.clone()
        if not annotated_beat_track:
            self._enumerateBeatTrack(bt)
        #print bt
        if self.params.getValue("adapt_beat_track"):
            bt = self._adaptBeatTrack(self.__notetrack, bt, tolerance)
            print("Adapted beattrack.")
        #well, that was the easy part.
        #set up an empty container
        mg = MeterGrid()
        last_beat = bt[-1].onset
        last_event = self.__notetrack[-1].onset

        # kind of a hack
        # if the last event of the beat track is too close to the last event
        # the annotation will be one to short, since the last event won't be found
        # solution: Add event to the beat track
        if (last_beat-last_event) <= tolerance:
            last_beat_dur = bt.iois[-1]
            dummy = bt[-1].clone()
            dummy.onset += dummy.onset + bt.iois[-1]
            bt.append(dummy)
            if debug:
                print("WARNING: Last event too close to last beat. Appending ghost beat.")

        #iterate thru every beat in the beat track and annotate the nopte events between beats
        for i in range(len(bt)-1):
            if debug: print("\n" + "="*60)
            if debug: print("Checking beat:")
            if debug: print(bt[i])
            if debug: print("="*60 + "\n")
            if annotated_beat_track:
                mi = bt[i].metrical_position.getMeterInfo()
            else:
                mi = bt[i].getValue().getMeterInfo()

            #find notes in notetrack between this beat and the next beat
            left  = bt[i].getOnsetSec()
            right = bt[i+1].getOnsetSec()
            #paranoid checking
            if float_equal(right - left, 0):
                raise RuntimeError("Beat track is crappy, because it contains duplicate elements at position {}/{}".format(i, i+1))

            start = None
            try:
                start, end = self.__notetrack.getIDsFromRegion(left-tolerance, right-tolerance)
            except Exception as e:
                print(e.args)

            #no elements between beats? move on!
            if start == None:
                #print "No events found for beats {}/{}".format(left,right)
                if debug:
                    print("No events in beat span")
                continue
            if debug:
                print("\nLeft beat: {}, right beat: {}, tolerance: {}".format(left, right, tolerance))

            #it's a rhythm baby, let's clone and scale it
            events      = Rhythm(self.__notetrack[start:(end+1)]).clone()
            eventsNorm  = Rhythm(self.__notetrack[start:(end+1)]).clone().normalize(left, right)

            #print "Beat left: {}, beat right: {}".format(left, right)
            #print "Onsets: {}".format(events.onsets)
            #print "Start:{}, end:{}".format(start, end)
            #debug = True
            if debug: print("\nRaw:")
            if debug: print(events)

            if debug: print("\nNormalized:")
            if debug: print(eventsNorm)
            #debug = False

            #scale rhythm threshold too
            rhythmThreshold = self.params.getValue("rhythmThreshold")/(right-left)
            #print "Right, left, diff", right, left, (right-left), self.params.getValue("rhythmThreshold")
            #now find optimal grid and best positions
            tatum, positions = self.quantize(eventsNorm, rhythmThreshold, debug)
            if debug: print("\ntatum:{}, positions:{}\n".format(tatum, positions))
            #no positions found, that's bad
            #TODO: Move on events to the next beat region
            if len(positions) == 0:
                raise RuntimeError("Could not determine positions for \n{}\nBailing out.".format(events) )

            #print "\nevents:\n{}, \ntatum:{}, positions:{}\n".format(eventsNorm, tatum, positions)
            ev = eventsNorm.getOnsets()
            #print "="*60

            fv = fill_vector(ev, tatum, positions)
            #print "Filled 1: {} ({})".format(fv, len(fv))
            if not float_equal(fv[-1], 1):
                fv.append(1)
            #print "Tatum:, ", tatum
            #print "Pos: {} ({})".format(positions, len(positions))
            #print "Events: {} ({})".format(ev, len(ev))
            #print "Filled 2: {} ({})".format(fv, len(fv))
            #print "Durs: {}".format(diff(fv))
            prop = proportions(fv)
            #print "Props: {} ({})".format(prop, len(prop))
            if len(positions) != len(eventsNorm):
                #print eventsNorm
                raise RuntimeError("Expected {} annotated points, got: {}".format(len(eventsNorm), len(positions)))

            #well thats it, basically,
            #now make up some nice data
            bi = BeatInfo(tatum, right - left, tuple(prop))
            mc = MetricalContext(bi, mi)
            #print "Found {} for {} events".format(len(positions), len(eventsNorm))

            for j in range(len(positions)):
                if annotated_beat_track:
                    mp = MetricalPosition(bt[i].metrical_position.getBar(), bt[i].metrical_position.getBeat(), positions[j]+1, 0, mc)
                else:
                    mp = MetricalPosition(bt[i].getValue().getBar(), bt[i].getValue().getBeat(), positions[j]+1, 0, mc)
                if j < (len(positions)-1):
                    durTatum = positions[j+1]-positions[j]
                else:
                    durTatum = tatum - positions[j]
                durTatum = (tatum * events[j].getDurationSec()/bi.getBeatDurationSec())
                me = MetricalEvent(events[j].getOnsetSec(), mp, events[j].getDurationSec(), durTatum)
                #print "I:{}, bt:{}, mp:{}".format(i, bt[i], mp)
                #print me
                mg.append(me)

        #print "\nResult:\n==================================\n"
        #print mg
        return mg

    def _adaptBeatTrack(self, rhythm, beat_track, max_diff):
        """
            Will find closest events in rhythm for each beat not farther
            than max_diff apart and substitute this value in beat track
        """
        tmp_beat_track = beat_track.clone()
        for i in range(len(beat_track)):
            found = find_closest(rhythm.onsets, beat_track[i].onset, max_diff)
            if found and found>=0:
                #print "Beat: {} -> closest: {}, ".format(beat_track[i].onset, rhythm.onsets[found] )
                tmp_beat_track[i].onset = rhythm[found].onset
            else:
                pass
                #print "Beat: {} no element found".format(beat_track[i].onset)
        return tmp_beat_track

    def _enumerateBeatTrack(self, beatTrack):
        """Expects a BeatTrack as from parse(), with attached Signature objects.
           First Signature event is taken as bar 1 beat 1.
           Annotation is done in-place.
           Should be part of annotate, but kept separate to not clutter
           annotate() even further
        """
        type_check(beatTrack, Rhythm)
        if beatTrack.isEmpty():
            raise RuntimeError("No events")
        #find first signature event
        signature = None
        start = None
        for i in range(len(beatTrack)):
            if isinstance(beatTrack[i].getValue(), Signature):
                signature = beatTrack[i].getValue()
                start = i
                break
        if signature == None:
            raise ValueError("BeatTrack does not contain Signature object")

        mi = MeterInfo(signature.getNumerator(), signature.getDenominator())
        period  = mi.getPeriod()
        bar     = -(start/period) if (start % period) != 0 else -(start/period)+1
        #print "Start ({})/Period({}) = {}, bar:{}".format(start, period, -(start/period), bar)
        beat    =  (period - start) % period
        iois    = beatTrack.getIOIs()
        iois.append(0)
        for i in range(len(beatTrack)):
            b  = beatTrack[i]
            if isinstance(beatTrack[i].getValue(), Signature):
                if beat != 0 and i != start:
                    raise RuntimeError("Signature object not on first beat of a bar. Offender: " + str(b))
                signature = beatTrack[i].getValue()
                mi = MeterInfo(beatTrack[i].getValue().getNumerator(), beatTrack[i].getValue().getDenominator())
                period = mi.getPeriod()
            bi  = BeatInfo(1, iois[i])
            b.setValue(MetricalPosition(bar, beat+1, 1, 0, MetricalContext(bi, mi)))
            beat += 1
            if beat == period:
                beat = 0
                bar += 1

    beattrack = property(getBeatTrack, setBeatTrack)
    params    = property(getParams, setParams)
