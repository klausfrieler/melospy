""" Class implementation of MelDBSqliteAdapter2"""

from melospy.input_output.mel_db_sqlite3_adapter import *


class MelDBSqliteAdapter2(MelDBSqliteAdapter):

    def __init__(self, filename = ":memory:", version={"major":1, "minor":0}, verbose=False, proc_hook=None):
        """ Initialize module """
        MelDBSqliteAdapter.__init__(self, filename, version, verbose, proc_hook)


    def dropTables(self):
        self.cursor.executescript("""
            DROP TABLE IF EXISTS melody;
            DROP TABLE IF EXISTS beats;
            DROP TABLE IF EXISTS sections;
            DROP TABLE IF EXISTS melody_type;
            DROP TABLE IF EXISTS solo_info;
            DROP TABLE IF EXISTS transcription_info;
            DROP TABLE IF EXISTS track_info;
            DROP TABLE IF EXISTS record_info;
            DROP TABLE IF EXISTS composition_info;
            DROP TABLE IF EXISTS esac_info;
            DROP TABLE IF EXISTS popsong_info;
            DROP TABLE IF EXISTS db_info;
            VACUUM;
            """)
        if self.verbose:
            print("Tables dropped")


    def createDatabase(self, withConfig=False, withIndex=False):
        self.dropTables()
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS melody(
              eventid     INTEGER PRIMARY KEY AUTOINCREMENT,
              melid       INTEGER,
              onset       REAL,
              pitch       REAL,
              duration    REAL,
              period      INTEGER,
              division    INTEGER,
              bar         INTEGER,
              beat        INTEGER,
              tatum       INTEGER,
              subtatum    INTEGER,
              num         INTEGER,
              denom       INTEGER,
              beatprops   TEXT,
              beatdur     REAL,
              tatumprops  TEXT,
              f0_mod      TEXT,
              loud_max    REAL,
              loud_med    REAL,
              loud_sd     REAL,
              loud_relpos REAL,
              loud_cent   REAL,
              loud_s2b    REAL,
              f0_range    REAL,
              f0_freq_hz  REAL,
              f0_med_dev  REAL
            );

            CREATE TABLE  IF NOT EXISTS beats(
              beatid  INTEGER PRIMARY KEY AUTOINCREMENT,
              melid   INTEGER,
              onset   REAL,
              bar INTEGER,
              beat INTEGER,
              signature TEXT,
              chord TEXT,
              form TEXT,
              bass_pitch INTEGER,
              chorus_id INTEGER,
              FOREIGN KEY(melid) REFERENCES melody(melid)
            );

            CREATE TABLE IF NOT EXISTS sections(
              melid  INTEGER,
              type   TEXT,
              start  INTEGER,
              end    INTEGER,
              value  TEXT,
              FOREIGN KEY(melid) REFERENCES melody(melid)
            );

            CREATE TABLE  IF NOT EXISTS melody_type(
              melid       INTEGER,
              type        TEXT,
              FOREIGN KEY(melid) REFERENCES melody(melid)
            );

            CREATE TABLE  IF NOT EXISTS transcription_info(
              melid             INTEGER,
              filename_sv       TEXT,
              filename_solo     TEXT,
              solotime          TEXT,
              solostart_sec     FLOAT,
              status            TEXT,
              trackid          INTEGER REFERENCES track_info(trackid),
              FOREIGN KEY(melid) REFERENCES melody(melid)
            );

            CREATE TABLE  IF NOT EXISTS solo_info(
              melid         INTEGER,
              trackid       INTEGER,
              compid        INTEGER,
              recordid      INTEGER,
              performer     TEXT,
              title         TEXT,
              titleaddon    TEXT,
              solopart      INTEGER,
              instrument    TEXT,
              style         TEXT,
              avgtempo      FLOAT,
              tempoclass    TEXT,
              rhythmfeel    TEXT,
              key           TEXT,
              signature     TEXT,
              chord_changes TEXT,
              chorus_count  INTEGER,
              FOREIGN KEY(melid)    REFERENCES melody(melid),
              FOREIGN KEY(trackid)  REFERENCES track_info(trackid),
              FOREIGN KEY(compid)   REFERENCES composition_info(compid),
              FOREIGN KEY(recordid) REFERENCES record_info(recordid)
            );

            CREATE TABLE  IF NOT EXISTS record_info(
              recordid     INTEGER PRIMARY KEY AUTOINCREMENT,
              artist        TEXT,
              recordtitle   TEXT,
              label         TEXT,
              recordbib     TEXT,
              mbzid         TEXT,
              releasedate   TEXT
            );

            CREATE TABLE  IF NOT EXISTS track_info(
              trackid        INTEGER PRIMARY KEY AUTOINCREMENT,
              filename_track TEXT,
              recordid       INTEGER REFERENCES record_info(recordid),
              lineup         TEXT,
              mbzid          TEXT,
              trackno        INTEGER,
              recordingdate  TEXT,
              compid         INTEGER REFERENCES composition_info(compid)
            );

            CREATE TABLE  IF NOT EXISTS composition_info(
              compid       INTEGER PRIMARY KEY AUTOINCREMENT,
              title         TEXT,
              composer      TEXT,
              form          TEXT,
              template      TEXT,
              tonalitytype  TEXT,
              genre         TEXT
            );

            CREATE TABLE  IF NOT EXISTS esac_info(
              melid         INTEGER,
              collection    TEXT,
              title         TEXT,
              esacid        TEXT,
              key           TEXT,
              unit          TEXT,
              signature     TEXT,
              region        TEXT,
              function      TEXT,
              comment       TEXT,
              source        TEXT,
              cnr           TEXT,
              tunefamily    TEXT,
              text          TEXT,
              melstring     TEXT,
              lcm_tatum     INTEGER,
              FOREIGN KEY(melid) REFERENCES melody(melid)
            );

            CREATE TABLE  IF NOT EXISTS popsong_info(
              melid         INTEGER,
              artist        TEXT,
              title         TEXT,
              avgtempo      REAL,
              tempoclass    TEXT,
              signature     TEXT,
              key           TEXT,
              filename      TEXT,
              chordchanges  TEXT,
              year          INTEGER,
              country       TEXT,
              style         TEXT,
              FOREIGN KEY(melid) REFERENCES melody(melid)
            );

            CREATE TABLE  IF NOT EXISTS db_info(
                name                TEXT,
                creator             TEXT,
                major               INTEGER,
                minor               INTEGER,
                release             TEXT,
                created             TEXT,
                license             TEXT,
                status              TEXT
            );


        """)
        if self.verbose:
            print("Database created")
        if withConfig:
            self.setDBConfigs()
        if withIndex:
            self.dropIndices()
            self.createIndices()

    def createIndices(self):
        self.cursor.executescript("""
            CREATE INDEX IF NOT EXISTS melind ON melody (melid, eventid);
            CREATE INDEX IF NOT EXISTS esacind ON esac_info (melid, collection, esacid);
            CREATE INDEX IF NOT EXISTS soloind ON solo_info (melid, performer, title);
            CREATE INDEX IF NOT EXISTS transind ON transcription_info (melid, filename_sv);
            CREATE INDEX IF NOT EXISTS trackind ON track_info (trackid, filename_track);
            CREATE INDEX IF NOT EXISTS compind ON composition_info (compid, title);
            CREATE INDEX IF NOT EXISTS sectind ON sections (melid, type);
            CREATE INDEX IF NOT EXISTS typeind ON melody_type (melid, type);

        """)
        if self.verbose:
            print("Indices created")

    def dropIndices(self):
        self.cursor.executescript("""
            DROP INDEX IF EXISTS melind;
            DROP INDEX IF EXISTS esacind;
            DROP INDEX IF EXISTS soloind;
            DROP INDEX IF EXISTS transind;
            DROP INDEX IF EXISTS trackind;
            DROP INDEX IF EXISTS sectind;
            DROP INDEX IF EXISTS typeind;

        """)
        if self.verbose:
            print("Indices dropped")



    def findRecord(self, artist, recordtitle, label, recordbib):
        self.cursor.execute("""SELECT recordid
                               FROM record_info
                               WHERE recordbib = (?)
                               AND artist = (?)
                               AND recordtitle = (?)
                               AND label = (?)""", (recordbib, artist, recordtitle, label))
        row = self.cursor.fetchone()
        record_id = None
        if row:
            return int(row[0])

        return record_id

    def findComposition(self, title, composer=None):
        if composer!= None:
            self.cursor.execute("""SELECT compid
                               FROM composition_info
                               WHERE title = (?) AND composer = (?)""", (title, composer))
        else:
            self.cursor.execute("""SELECT compid
                               FROM composition_info
                               WHERE title = (?)""", (title,))

        row = self.cursor.fetchone()
        comp_id = None
        if row:
            return int(row[0])

        return comp_id

    def insertComposition(self, title, composer, form, harmony_template, tonalitytype, genre):
        """
            Insert composition into composition info using title and composer
            as unique identifier combination
        """
        comp_id = self.findComposition(title)
        if comp_id != None:
            #print "'{}' by {} already in database".format(title, composer)
            return comp_id
        comp_id = self.findFreeID("composition_info", "compid")
        self.cursor.execute("""INSERT INTO composition_info
         (compid, title, composer, form, template, tonalitytype, genre)
         VALUES (?, ?, ?, ?, ?, ?, ?)""",\
         (comp_id, title, composer, form, harmony_template, tonalitytype, genre))
        #print "Inserted composition '{}' by {} with id {}".format(title, composer, comp_id)
        return comp_id

    def findTrack(self, filename_track):
        self.cursor.execute("""SELECT trackid
                               FROM track_info
                               WHERE filename_track = (?)""", (filename_track,))
        row = self.cursor.fetchone()
        track_id = None
        if row:
            return int(row[0])

        return track_id

    def insertTrack(self, record_id, comp_id, filename_track, lineup, mbzid, trackno, recordingdate):
        track_id = self.findTrack(filename_track)

        if track_id != None:
            #print "Entry [{}] already in database".format(filename_track)
            return track_id
        track_id = self.findFreeID("track_info", "trackid")
        self.cursor.execute("""
            INSERT INTO track_info
            (trackid, recordid, compid, filename_track, lineup, mbzid, trackno, recordingdate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ? )""", (track_id, record_id, comp_id, filename_track, lineup, mbzid, trackno, recordingdate)
            )
        return track_id

    def insertRecord(self, artist, recordtitle, label, recordbib, mbzid, releasedate):
        record_id = self.findRecord(artist, recordtitle, label, recordbib)
        if record_id != None:
            #print "Entry [{},{},{},{}] already in database".format(artist, recordtitle, label, recordbib)
            return record_id
        record_id = self.findFreeID("record_info", "recordid")
        self.cursor.execute("""
            INSERT INTO record_info
            (recordid, artist, recordtitle, label, recordbib, mbzid, releasedate)
            VALUES (?, ?, ?, ?, ?, ?,? )""", (record_id, artist, recordtitle, label, recordbib, mbzid, releasedate)
            )
        return record_id

    def insertSoloMetadata(self, solo, melID):
        artist          =   solo.metadata.recordinfo.artist
        recordtitle     =   solo.metadata.recordinfo.recordtitle
        lineup          =   solo.metadata.recordinfo.lineup
        label           =   solo.metadata.recordinfo.label
        recordbib       =   solo.metadata.recordinfo.recordbib
        mbzid           =   solo.metadata.recordinfo.musicbrainzid
        trackno         =   solo.metadata.recordinfo.tracknumber
        releasedate     =   str(solo.metadata.recordinfo.releasedate)
        recordingdate   =   str(solo.metadata.recordinfo.recordingdate)
        filename_sv     =   os.path.basename(solo.metadata.transinfo.filenamesv)
        filename_solo   =   solo.metadata.transinfo.filenamesolo
        filename_track  =   solo.metadata.transinfo.filenametrack
        solotime        =   solo.metadata.transinfo.solotime
        solostart_sec   =   solo.metadata.transinfo.solostart
        status          =   solo.metadata.transinfo.status

        try:
            #print "SM:", solo.metadata.compinfo.form, type(solo.metadata.compinfo.form)
            title  =   solo.metadata.soloinfo.title
            composer  =   solo.metadata.compinfo.composer
            if isinstance(solo.metadata.compinfo.form, FormDefinition):
                form =  solo.metadata.compinfo.form.getShortForm(withLengths=True)
            else:
                form = solo.metadata.compinfo.form
            harmony_template =   solo.metadata.compinfo.harmonytemplate
            tonalitytype  =   solo.metadata.compinfo.tonalitytype
            genre =   solo.metadata.compinfo.genre
            comp_id = self.insertComposition(title, composer, form, harmony_template, tonalitytype, genre)
        except Exception:
            print("Could not insert composition: {} by {}".format(title, composer))
            comp_id = -1
            pass

        try:
            record_id = self.insertRecord(artist, recordtitle, label, recordbib, "", releasedate)
            track_id  = self.insertTrack(record_id, comp_id, filename_track, lineup, mbzid, trackno, recordingdate)
            self.cursor.execute("""INSERT INTO transcription_info
             (melid, filename_sv, filename_solo, trackid, status, solotime, solostart_sec)
             VALUES (?, ?, ?, ?, ?, ?, ?)""",
             (melID, filename_sv, filename_solo, track_id, status, solotime, solostart_sec))
        except:
            record_id = -1
            track_id  = -1
            print("Could not insert track, record and/or transcription data")
            pass
        #OUT OF TRY

        try:
            performer   =   solo.metadata.soloinfo.performer
            title       =   solo.metadata.soloinfo.title
            titleaddon  =   solo.metadata.soloinfo.titleaddon
            solopart    =   solo.metadata.soloinfo.solopart
            if not solopart:
                solopart = 1
            instrument  =   solo.metadata.soloinfo.instrument
            style       =   solo.metadata.soloinfo.style
            avgtempo    =   solo.metadata.soloinfo.avgtempo
            tempoclass  =   solo.metadata.soloinfo.tempoclass
            rhythmfeel  =   solo.metadata.soloinfo.rhythmfeel
            key         =   str(solo.metadata.soloinfo.key)
            sig         =   str(solo.metadata.soloinfo.signature)
            changes     =   str(solo.metadata.soloinfo.chordchanges)
            chorus_count=   int(solo.metadata.soloinfo.choruscount)

            self.cursor.execute("""INSERT INTO solo_info
             (melid, trackid, compid, recordid, performer, title, titleaddon, solopart, instrument, style,
             avgtempo, tempoclass, rhythmfeel, key, signature, chord_changes, chorus_count)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",\
             (melID, track_id, comp_id, record_id, performer, title, titleaddon, solopart, instrument, style,\
              avgtempo, tempoclass, rhythmfeel, key, sig, changes, chorus_count))
        except Exception as e:
            #raise e
            print("Could not insert solo_info")
            pass

    def parseSoloInfo(self, row):
        try:
            try:
                solopart = int(row["solopart"])
            except:
                solopart = 1
            try:
                changes = str(row["chord_changes"])
            except:
                changes = ""
            try:
                chorus_count = int(row["chorus_count"])
            except:
                chorus_count = None

            si = SoloInfo(melid=row["melid"],
                          performer=str(row["performer"]),
                          title=str(row["title"]),
                          title_addon=str(row["titleaddon"]),
                          solo_part=solopart,
                          instrument=str(row["instrument"]),
                          style=str(row["style"]),
                          averageTempoBPM=float(row["avgtempo"]),
                          tempo_class=str(row["tempoclass"]),
                          rhythm_feel=str(row["rhythmfeel"]),
                          key=str(row["key"]),
                          chord_changes=changes,
                          chorus_count=chorus_count
                          )
        except:
            si = None

        if si != None:
            try:
                si.signature = str(row["signature"])
            except:
                pass

        return si

    def parseTranscriptionInfo(self, row):
        ti = None
        ri = None
        track_id = None
        try:
            solotime = str(row["solotime"]).replace(" ", "")
            elems = solotime.split("-")
            try:
                solostart = float(row["solostart_sec"])
            except:
                solostart = elems[0]
            if len(elems) > 1:
                soloend  = elems[1]
            else:
                soloend = "NA"
            ti = TranscriptionInfo(fileNameSolo= str(row["filename_solo"]), fileNameSV=str(row["filename_sv"]), status=str(row["status"]))
            ti.solotime  = solotime
            ti.solostart = solostart
            ti.soloend   = soloend
            track_id = row["trackid"]
        except Exception:
            print("Error during parseTranscriptionInfo")

        if track_id:
            ri, filename_track, comp_id  = self.readTrackAndRecordInfo(track_id)
            ti.filenametrack = filename_track
        return ti, ri, comp_id


    def readTrackAndRecordInfo(self, track_id):
        self.open_second()
        self.cursor2.execute("SELECT * FROM track_info WHERE trackid = (?)", (track_id,))
        ti_row = self.cursor2.fetchone()
        record_id = ti_row["recordid"]
        filename_track = ti_row["filename_track"]
        self.cursor2.execute("SELECT * FROM record_info WHERE recordid = (?)", (record_id,))
        ri_row = self.cursor2.fetchone()
        self.close_second()

        try:
            try:
                comp_id = int(ti_row["compid"])
            except:
                comp_id = -1
            try:
                trackno= int(ti_row["trackno"])
            except:
                trackno = None
            ri = RecordInfo(artist=str(ri_row["artist"]),
                            recordTitle=str(ri_row["recordtitle"]),
                            lineup=str(ti_row["lineup"]),
                            label=str(ri_row["label"]),
                            recordBib=str(ri_row["recordbib"]),
                            musicBrainzID=str(ti_row["mbzid"]),
                            trackNumber=trackno,
                            releaseDate=str(ri_row["releasedate"]),
                            recordingDate=str(ti_row["recordingdate"])
                            )
        except:
            ri = None

        return ri, filename_track, comp_id

    def readCompositionInfo(self, comp_id, ci_cache=None):
        if ci_cache != None:
            try:
                ci = ci_cache[comp_id]
                return ci
            except:
                pass

        self.open_second()
        self.cursor2.execute("SELECT * FROM composition_info WHERE compid = (?)", (comp_id,))
        row = self.cursor2.fetchone()
        try:
            ci = CompositionInfo(title=str(row["title"]),
                                 composer=str(row["composer"]),
                                 form=str(row["form"]),
                                 harmony_template=str(row["template"]),
                                 tonality_type=str(row["tonalitytype"]),
                                 genre=str(row["genre"])
                                 )
        except:
            ci = None
        return ci

    def readAllCompositionInfos(self, melids):
        self.open_second()
        query = """
            SELECT * FROM composition_info
            WHERE compid IN
            (
                SELECT compid FROM solo_info WHERE melid in ({})
            )""".format(",".join([str(v) for v in melids]))

        #self.cursor2.execute("SELECT compid FROM solo_info WHERE ({})".format(melid_clause))
        #comp_ids = [row["compid"] for row in self.cursor2]
        #compid_clause = "compid in ({})".format(",".join([str(v) for v in comp_ids]))

        self.cursor2.execute(query)
        ci_cache = {}
        #row = self.cursor2.fetchone()
        for row in self.cursor2:
            try:
                ci = CompositionInfo(title=str(row["title"]),
                                     composer=str(row["composer"]),
                                     form=str(row["form"]),
                                     harmony_template=str(row["template"]),
                                     tonality_type=str(row["tonalitytype"]),
                                     genre=str(row["genre"])
                                     )
            except:
                ci = None
            ci_cache[int(row["compid"])] = ci
        #print "ci_cache", [str(ci_cache[_]) for _ in ci_cache]
        self.close_second()
        return ci_cache

    def readSoloMetadata(self, melids=None):
        melid_clause = ""
        if melids == None:
            melids = self.getAllMelIDs()
        else:
            melids = self.prepareMelIDs(melids)
            melid_clause = "and solo_info.melid in ({})".format(",".join([str(v) for v in melids]))

        timer = Timer()
        smd = {}
        bad_ids = []
        timer.start()
        ci_cache = self.readAllCompositionInfos(melids)
        #print "Read all composition {} infos in {}".format(len(melids), timer.end())
        count = 0
        totalDur = 0
        query = "SELECT * FROM solo_info, transcription_info WHERE solo_info.melid = transcription_info.melid {}".format(melid_clause)
        self.cursor.execute(query)
        for row in self.cursor:
            melid = row["melid"]
            count += 1
            timer.start()
            try:
                si = self.parseSoloInfo(row)
            except:
                si = None
                bad_ids.append(melid)

            try:
                ti, ri, comp_id = self.parseTranscriptionInfo(row)
                ci = self.readCompositionInfo(comp_id, ci_cache)
            except:
                ti = None
                ri = None
                ci = None
                bad_ids.append(melid)

            totalDur += timer.end()
            smd[melid]= SoloMetaData(transcriptionInfo=ti, soloInfo=si, compositionInfo=ci, recordInfo=ri)
        self.verbose = False
        if self.verbose:
            print("readSoloMetadata:")
            print("--Total duration: {}".format(totalDur))
            print("--Mean duration: {}".format(totalDur/count))
            print("--Count: {}".format(count))
            print("--#Bad IDs: {}".format(len(set(bad_ids))))
        #print "\n".join(["{}: {}".format(k, smd[k]) for k in smd])
        self.verbose = False
        return smd

    def findSoloId(self, performer, title):
        self.cursor.execute("SELECT melid FROM transcription_info WHERE performer = (?) AND title = (?)", (performer, title))
        row = self.cursor.fetchone()
        if row:
            return row["melid"]
        return None

    def getMelIDsByFilenameSV(self, fileglob):
        query = "SELECT DISTINCT(melid) FROM transcription_info WHERE filename_sv LIKE '{}'".format(fileglob.replace("*", "%"))
        self.cursor.execute(query)
        return [row[0] for row in self.cursor]

    def getDisplayNamesByMelIDs(self, melids, table, field):
        display_names = []
        if not isinstance(melids, list):
            melids = [melids]
        for i in melids:
            self.cursor.execute("SELECT {} FROM {} WHERE melid=(?)".format(field, table), (i,))
            row =  self.cursor.fetchone()
            if row:
                display_names.append(str(row[field]))
        return display_names

    def getDisplayNamesByNestedSelect(self, query, table, field):
        display_names = []

        nested = "SELECT {} FROM {} WHERE melid IN ({})".format(field, table, query)
        self.cursor.execute(nested)

        for row in self.cursor:
            display_names.append(str(row[field]))
        return display_names
