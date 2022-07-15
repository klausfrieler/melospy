""" Class implementation of MelDBSqliteAdapter"""

import os
import re
import sqlite3 as sqlite3
import time
from datetime import datetime

from melospy.basic_representations.annotated_beat_track import *
from melospy.basic_representations.esac_info import *
from melospy.basic_representations.esac_meta_data import EsacMetaData
from melospy.basic_representations.melody import *
from melospy.basic_representations.popsong_meta_data import *
from melospy.basic_representations.solo import *


class MelDBSqliteAdapter(object):

    def __init__(self, filename = ":memory:", version={"major":1, "minor":0}, verbose=False, proc_hook=None):
        """ Initialize module """
        self.__filename = filename
        self.verbose = verbose
        if proc_hook == None:
            self.proc_hook = jm_util.void
        else:
            self.proc_hook = proc_hook
        self.version = version

    def getFilename(self):
        return self.__filename

    def getCursor(self):
        return self.cursor

    def getConnection(self):
        return self.conn

    def dropTables(self):
        self.cursor.executescript("""
            DROP TABLE IF EXISTS melody;
            DROP TABLE IF EXISTS beats;
            DROP TABLE IF EXISTS sections;
            DROP TABLE IF EXISTS melody_type;
            DROP TABLE IF EXISTS transcription_info;
            DROP TABLE IF EXISTS record_info;
            DROP TABLE IF EXISTS composition_info;
            DROP TABLE IF EXISTS solo_info;
            DROP TABLE IF EXISTS popsong_info;
            DROP TABLE IF EXISTS esac_info;
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
              chorus_id  INTEGER,
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
              filename_track    TEXT,
              solotime          TEXT,
              status            TEXT,
              FOREIGN KEY(melid) REFERENCES melody(melid)
            );

            CREATE TABLE  IF NOT EXISTS solo_info(
              melid         INTEGER,
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
              FOREIGN KEY(melid) REFERENCES melody(melid)
            );

            CREATE TABLE  IF NOT EXISTS record_info(
              melid         INTEGER,
              artist        TEXT,
              recordtitle   TEXT,
              lineup        TEXT,
              label         TEXT,
              recordbib     TEXT,
              mbzid         TEXT,
              trackno       INTEGER,
              releasedate   TEXT,
              recordingdate TEXT,
              FOREIGN KEY(melid) REFERENCES melody(melid)
            );

            CREATE TABLE  IF NOT EXISTS composition_info(
              melid         INTEGER,
              composer      TEXT,
              form          TEXT,
              tonalitytype  TEXT,
              genre         TEXT,
              FOREIGN KEY(melid) REFERENCES melody(melid)
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
            DROP INDEX IF EXISTS sectind;
            DROP INDEX IF EXISTS typeind;

        """)
        if self.verbose:
            print("Indices dropped")

    def rebuildIndices(self):
        self.dropIndices()
        self.createIndices()

    def setDBConfigs(self):
        pass

    def setMetadataSource(self, srcname):
        self.metadatasrc = srcname

    def setBulkConfigs(self):
        self.cursor.executescript("""
            PRAGMA main.page_size=4096;
            PRAGMA main.cache_size=10000;
            PRAGMA main.locking_mode=EXCLUSIVE;
            PRAGMA main.synchronous=NORMAL;
            PRAGMA main.journal_mode=WAL;
        """)
    def restoreConfigs(self):
        self.cursor.executescript("""
            PRAGMA main.page_size=1024;
            PRAGMA main.cache_size=2000;
            PRAGMA main.locking_mode=NORMAL;
            PRAGMA main.synchronous=FULL;
            PRAGMA main.journal_mode=DELETE;
        """)

    def getAllMelIDs(self):
        self.cursor.execute("SELECT DISTINCT melid FROM melody")
        return [int(row["melid"]) for row in self.cursor]

    def getMelIdClause(self, table, melids=None):
        if melids == None:
            return "SELECT * FROM {}".format(table)
        if not isinstance(melids, list):
            melids = [melids]
        melid_str = ",".join([str(v) for v in melids])
        query = "SELECT * FROM {} WHERE melid IN ({})".format(table, melid_str)
        return query

    def readDatabase(self):
        return self.readSongs()

    def readSongs(self, melids=None):
        self.cursor.execute("SELECT DISTINCT type FROM melody_type")
        types = [row["type"] for row in self.cursor]
        if len(types) > 1:
            raise RuntimeError("Melody databases of mixed type not supported yet")
        if types[0] == "SOLO":
            solos = self.readSolos(melids)
        elif types[0] == "POPSONG":
            solos = self.readPopSongs(melids)
        else:
            solos = self.readEsacSongs(melids)

        return solos

    def writeDatabase(self, melodies):
        if self.verbose:
            print("Writing database...")
        for mel in melodies:
            self.insertMelody(mel)

    def bulkInsert(self, bucket):
        self.setBulkConfigs()
        if self.verbose:
            print("BulkInsert of {} items. Bear with me.".format(len(bucket)))
        i = 1
        factor = int(round((len(bucket)/20.0)/10.0)*10.0)
        if factor == 0:
            factor = 1
        start = time.process_time()

        for mel in bucket:
            if mel[1][0:3] == "esa":
                self.insertEsacSong(mel[0], mel[0].__dict__["esacinfo"])
            elif mel[1][0:5] == "mcsv1":
                self.insertPopSong(mel[0])
            else:
                self.insertSolo(mel[0])
            if i % factor == 0:
                if self.verbose:
                    print("{} items now... in {} s".format(i, round(time.process_time()-start, 3)))
                start = time.process_time()
            i +=1
        melcount = self.getMelodyCount()
        if self.verbose:
            print("{} melodies now in DB {}".format(melcount, self.filename))
        self.restoreConfigs()

    def getMelodyCount(self):
        self.cursor.execute("SELECT COUNT(DISTINCT(melid)) FROM melody")
        return self.cursor.fetchone()[0]

    def getEventCount(self):
        self.cursor.execute("SELECT COUNT(DISTINCT(melid)) FROM melody")
        return self.cursor.fetchone()[0]

    def findFreeID(self, table, id_field):
        self.cursor.execute("SELECT DISTINCT {} FROM {} ORDER BY {} ASC".format(id_field, table, id_field))

        ids = [row[id_field] for row in self.cursor]

        if len(ids) == 0:
            return 1
        if ids[0]>1:
            return 1
        for i in range(len(ids)-1):
            if ids[i+1]-ids[i]>1:
                return i+1
        return len(ids)+1

    def findFreeMelID(self):
        return self.findFreeID("melody", "melid")

    def getMaxMelID(self):
        self.cursor.execute("SELECT DISTINCT melid FROM melody")
        maxId = 0
        for row in self.cursor:
            if row["melid"]>maxId:
                maxId = row["melid"]
        return maxId

    def insertMelody(self, melody, melID=None):
        if melID == None:
            melID = self.findFreeMelID()
        tmp = [(melID,\
            e.getOnset(),\
            e.getPitch(),\
            e.getDuration(),\
            e.getPeriod(),\
            e.getDivision(),\
            e.getBar(),\
            e.getBeat(),\
            e.getTatum(),\
            e.getSubtatum(),\
            e.getMeterInfo().getNumerator(),\
            e.getMeterInfo().getDenominator(),\
            str(e.getMeterInfo().getBeatProportions()),\
            e.getBeatDuration(),\
            str(e.getBeatInfo().getTatumProportions()),
            e.getAnnotatedF0Modulation(),
            e.getLoudnessField("max", None),
            e.getLoudnessField("median", None),
            e.getLoudnessField("stddev", None),
            e.getLoudnessField("rel_peak_pos", None),
            e.getLoudnessField("temp_centroid", None),
            e.getLoudnessField("s2b", None),
            e.getF0ModulationField("range_cents", None),
            e.getF0ModulationField("freq_hz", None),
            e.getF0ModulationField("median_dev", None)
            ) for e in melody]
        self.cursor.executemany("INSERT INTO melody (melid, onset, pitch, duration, period, division, bar, beat, tatum, subtatum, num, denom, beatprops, beatdur, tatumprops, f0_mod, loud_max, loud_med, loud_sd, loud_relpos, loud_cent, loud_s2b, f0_range, f0_freq_hz, f0_med_dev) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, ?, ?, ?, ?)", tmp)
        return melID

    def insertSolo(self, solo):
        melID = self.insertMelody(solo)
        self.insertSoloMetadata(solo, melID)
        self.insertBeatTrack(solo, melID)
        self.insertSoloSections(solo, melID)
        self.insertMelodyType("SOLO", melID)
        return melID

    def insertEsacSong(self, solo, esacinfo):
        melID = self.insertMelody(solo)
        self.insertEsacMetadata(esacinfo, solo.leastCommonTatum(), melID)
        self.insertEsacSections(solo, melID)
        self.insertMelodyType("ESAC", melID)
        return melID

    def insertEsacMetadata(self, esacinfo, lcm_tatum, melID):
        if esacinfo== None:
            return
        ei = esacinfo
        m = re.match("[A-Z]+[0-9]+", ei.esacid)
        tunefamily = m.group(0) if m is not None else ""
        self.cursor.execute("""
            INSERT INTO esac_info (melid, collection, title, esacid, key,
                       unit, signature, region, function, comment,
                                   source, cnr, tunefamily, text, melstring, lcm_tatum)
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (melID, str(ei.collection), str(ei.title), ei.esacid, ei.key, ei.unit, ei.signature, str(ei.region), str(ei.function), str(ei.comment), str(ei.source), str(ei.cnr), tunefamily, str(ei.text), ei.melstring, lcm_tatum))

    def insertPopSong(self, song):
        melID = self.insertMelody(song)
        self.insertPopSongMetadata(song.getPopSongInfo(), melID)
        self.insertPhraseSections(song, melID)
        self.insertMelodyType("POPSONG", melID)
        return melID

    def insertPopSongMetadata(self, popsong_info, melID):
        if popsong_info == None:
            return
        pi = popsong_info

        self.cursor.execute("""
            INSERT INTO popsong_info (melid, artist, title,
                                      avgtempo, tempoclass, signature,
                                      key, filename, chordchanges,
                                      year, country, style)
                                   VALUES (?, ?, ?,
                                           ?, ?, ?,
                                           ?, ?, ?,
                                           ?, ?, ?)
            """, (melID, str(pi.artist), str(pi.title),\
                pi.avgtempo, pi.tempoclass, str(pi.signature),\
                str(pi.key), pi.filename, pi.chordchanges,\
                pi.year, pi.country, str(pi.style)))

    def insertMelodyType(self, type, melID):
        if type != "SOLO" and type != "ESAC" and type != "POPSONG":
            raise ValueError("Unknown melody type: {}".format(type))
        self.cursor.execute("INSERT INTO melody_type (melid, type) VALUES (?, ?)", (melID, type))

    def readMelodyType(self, melID):
        self.cursor.execute("SELECT type FROM melody_type WHERE melid=(?)", (melID, ))
        row = self.cursor.fetchone()
        return row["type"]

    def insertDBInfo(self, content_type="", version="1.0", release="1.0"):
        if isinstance(version, str):
            tmp = version.split(".")
            if len(tmp) == 0:
                tmp = [1, 0]
            if len(tmp) < 2:
                tmp.append("0")
            version = {"major":int(tmp[0]), "minor":int(tmp[1])}
        if content_type == "sv":
            self.insertWJazzDInfo(version, release)
        elif content_type == "esac":
            self.insertEsacDBInfo(version, release)
        elif content_type == "omnibook":
            self.insertOmniDBInfo(version, release)
        elif content_type == "popsong":
            self.insertPopsongDBInfo(version, release)

    def insertWJazzDInfo(self, version, release):
        try:
            major = version["major"]
            minor = version["minor"]
            name = "Weimar Jazz Database (WJazzD)"
            creator = "The Jazzomat Research Project (c) 2012-2017"
            license = "The Weimar Jazz Database is made available under the Open Database License: http://opendatacommons.org/licenses/odbl/1.0/. Any rights in individual contents of the database are licensed under the Database Contents License: http://opendatacommons.org/licenses/dbcl/1.0/ - See more at: http://opendatacommons.org/licenses/odbl/#sthash.u61y95w0.dpuf"
            status = "FINAL"
            date_of_creation = datetime.datetime.now().isoformat()
            print("New WJazzD  v{}.{} Release {} created at {}".format(major, minor, release, date_of_creation))
            self.cursor.execute("""INSERT INTO db_info
             (name, major, minor, release, created, creator, license, status)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
             (name,  major, minor, release, date_of_creation, creator, license, status))
        except Exception as e:
            raise e
            pass

    def insertOmniDBInfo(self, version, release):
        try:
            major = version["major"]
            minor = version["minor"]
            name = "OmnibookDB"
            creator = "Dan Shanahan/The Jazzomat Research Project (c) 2017"
            license = "The OmnibookDB is made available under the Open Database License: http://opendatacommons.org/licenses/odbl/1.0/. Any rights in individual contents of the database are licensed under the Database Contents License: http://opendatacommons.org/licenses/dbcl/1.0/ - See more at: http://opendatacommons.org/licenses/odbl/#sthash.u61y95w0.dpuf"
            status = "FINAL"
            date_of_creation = datetime.datetime.now().isoformat()
            print("New OmnibookDB v{}.{} Release {} created at {}".format(major, minor, release, date_of_creation))
            self.cursor.execute("""INSERT INTO db_info
             (name, major, minor, release, created, creator, license, status)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
             (name,  major, minor, release, date_of_creation, creator, license, status))
        except Exception as e:
            raise e
            pass


    def insertEsACDBInfo(self, version, release):
        try:
            major = version["major"]
            minor = version["minor"]
            name = "EsAC Database (Jazzomat Version)"
            creator = "The Jazzomat Research Project"
            license = "Unknown License"
            status = "FINAL"
            date_of_creation = datetime.datetime.now().isoformat()
            print("New EsACDB v{}.{} Release {} created at {}".format(major, minor, release, date_of_creation))
            self.cursor.execute("""INSERT INTO db_info
             (name, major, minor, release, created, creator, license, status)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
             (name,  major, minor, release, date_of_creation, creator, license, status))
        except Exception as e:
            raise e
            pass

    def insertPopsongDBInfo(self, version, release):
        try:
            major = version["major"]
            minor = version["minor"]
            name = "Pop Daniel"
            creator = "???"
            license = "Propietary"
            status = "FINAL"
            date_of_creation = datetime.datetime.now().isoformat()
            print("New PopsongDaniel DB v{}.{} Release {} created at {}".format(major, minor, release, date_of_creation))
            self.cursor.execute("""INSERT INTO db_info
             (name, major, minor, release, created, creator, license, status)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
             (name,  major, minor, release, date_of_creation, creator, license, status))
        except Exception as e:
            raise e
            pass
    def insertSoloMetadata(self, solo, melID):
        try:
            filenameSV      =   os.path.basename(solo.metadata.transinfo.filenamesv)
            filenameTrack   =   solo.metadata.transinfo.filenametrack
            filenameSolo    =   solo.metadata.transinfo.filenamesolo
            solotime        =   solo.metadata.transinfo.solotime
            status          =   solo.metadata.transinfo.status

            self.cursor.execute("""INSERT INTO transcription_info
             (melid, filename_sv, filename_solo, filename_track, status, solotime)
             VALUES (?, ?, ?, ?, ?, ?)""",
             (melID, filenameSV, filenameSolo, filenameTrack, status, solotime))
        except Exception as e:
            #raise e
            pass
        try:
            performer   =   solo.metadata.soloinfo.performer
            title       =   solo.metadata.soloinfo.title
            titleaddon  =   solo.metadata.soloinfo.titleaddon
            solopart    =   solo.metadata.soloinfo.solopart
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
             (melid, performer, title, titleaddon, solopart, instrument, style,
             avgtempo, tempoclass, rhythmfeel, key, signature, chord_changes, chorus_count)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",\
             (melID, performer, title, titleaddon, solopart, instrument, style,\
              avgtempo, tempoclass, rhythmfeel, key, sig, changes, chorus_count))
        except Exception as e:
            #raise e
            print("Could not insert solo_info")
            pass
        try:
            artist          =   solo.metadata.recordinfo.artist
            recordtitle     =   solo.metadata.recordinfo.recordtitle
            lineup          =   solo.metadata.recordinfo.lineup
            label           =   solo.metadata.recordinfo.label
            recordbib       =   solo.metadata.recordinfo.recordbib
            mbzid           =   solo.metadata.recordinfo.musicbrainzid
            trackno         =   (solo.metadata.recordinfo.tracknumber)
            releasedate     =   str(solo.metadata.recordinfo.releasedate)
            recordingdate   =   str(solo.metadata.recordinfo.recordingdate)

            self.cursor.execute("""INSERT INTO record_info
             (melid, artist, recordtitle, lineup, label,
             recordbib, mbzid, trackno, releasedate, recordingdate)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",\
             (melID, artist, recordtitle, lineup, label,\
             recordbib, mbzid, trackno, releasedate, recordingdate))
        except Exception as e:
            #raise e
            pass
        try:
            composer        =   solo.metadata.compinfo.composer
            if isinstance(solo.metadata.compinfo.form, FormDefinition):
                form =  solo.metadata.compinfo.form.getShortForm(withLengths=True)
            else:
                form = solo.metadata.compinfo.form
            tonalitytype    =   solo.metadata.compinfo.tonalitytype
            genre           =   solo.metadata.compinfo.genre
            self.cursor.execute("""INSERT INTO composition_info
             (melid, composer, form, tonalitytype, genre)
             VALUES (?, ?, ?, ?, ?)""",\
             (melID, composer, form, tonalitytype, genre))
        except Exception:
            #raise e
            pass

    def insertBeatTrack(self, melody, melID):
        beattrack = melody.getBeatTrack()
        if not beattrack or len(beattrack) == 0:
            return
        if isinstance(beattrack, AnnotatedBeatTrack):
            #beattrack.calcSignatureChanges()
            #print beattrack.getSignatureChanges()
            tmp = [(melID, b.getOnset(), b.getBar(), b.getBeat(), b.signature_change, get_NA_str(b.chord, ""), b.getFormString(), b.bass_pitch, b.chorus_id) for b in beattrack]
            self.cursor.executemany("INSERT INTO beats (melid, onset, bar, beat, signature, chord, form, bass_pitch, chorus_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", tmp)

        else:
            tmp = [(melID, b.getOnset()) for b in beattrack]
            self.cursor.executemany("INSERT INTO beats (melid, onset) VALUES (?,?)", tmp)

    def isSectionPresent(self, melID, sectType):
        self.cursor.execute("SELECT * FROM sections WHERE melid = (?)", (melID,))
        types= [row["type"] for row in self.cursor]
        if sectType in types:
            return True
        return False

    def insertSection(self, section, melID, sectType):
        if section == None:
            #print "None found for ", melID, sectType
            return
        if self.isSectionPresent(melID, sectType):
            raise RuntimeError("Section '{}' for  melody {} already present".format(sectType, melID))
        tmp = [(melID, sectType, s.getStartID(), s.getEndID(), str(s.getValue())) for s in section]
        self.cursor.executemany("INSERT INTO sections (melid, type, start, end, value) VALUES (?,?,?,?,?)", tmp)

    def insertPhraseSections(self, melody, melID):
        sect = melody.getPhraseSections()
        self.insertSection(sect, melID, "PHRASE")

    def insertChordSections(self, melody, melID):
        sect = melody.getChordSections()
        self.insertSection(sect, melID, "CHORD")

    def insertChorusSections(self, melody, melID):
        sect = melody.getChorusSections()
        self.insertSection(sect, melID, "CHORUS")

    def insertFormSections(self, melody, melID):
        sect = melody.getFormSections()
        self.insertSection(sect, melID, "FORM")

    def insertKeySections(self, melody, melID):
        sect = melody.getKeySections()
        self.insertSection(sect, melID, "KEY")

    def insertIFASections(self, melody, melID):
        sect = melody.getIFASections()
        self.insertSection(sect, melID, "IDEA")

    def insertSoloSections(self, solo, melID):
        self.insertPhraseSections(solo, melID)
        self.insertChordSections(solo, melID)
        self.insertChorusSections(solo, melID)
        self.insertFormSections(solo, melID)
        self.insertKeySections(solo, melID)
        if solo.hasIFASections():
            self.insertIFASections(solo, melID)

    def insertEsacSections(self, solo, melID):
        self.insertPhraseSections(solo, melID)
        self.insertChordSections(solo, melID)
        self.insertKeySections(solo, melID)

    def prepareMelIDs(self, melids=None):
        if melids == None:
            melids = self.getAllMelIDs()
        if not isinstance(melids, list):
            melids = [melids]
        return melids

    def parseMelodyEvent(self, row, simplifyBeatProps=False):
        loudness = None
        try:
            loudness = Loudness.fromStruct([row["loud_max"], row["loud_med"], row["loud_sd"], row["loud_relpos"], row["loud_cent"], row["loud_s2b"]])
        except:
            pass

        f0_mod = None
        try:
            f0_mod = F0Modulation(row["f0_mod"], row["f0_range"], row["f0_freq_hz"], row["f0_med_dev"])
        except:
            f0_mod = F0Modulation("")

        num, denom = row["num"], row["denom"]
        if simplifyBeatProps:
            if denom >= 8 and num !=9 and num % 2 == 1:
                mi = MeterInfo(num, denom, num)
            else:
                mi = MeterInfo(num, denom, None)
        else:
            mi = MeterInfo(row["num"], row["denom"], eval(row["beatprops"]))
        bi = BeatInfo(row["division"], row["beatdur"], eval(row["tatumprops"]))
        mc = MetricalContext(bi, mi)
        mp = MetricalPosition(row["bar"], row["beat"], row["tatum"], row["subtatum"], mc)
        mne = MetricalNoteEvent(row["onset"], row["pitch"], mp, row["duration"], loudness=loudness, modulation=f0_mod)
        return mne

    def readMelodies(self, melids=None, simplifyBeatProps=False):
        query   = self.getMelIdClause("melody", melids)
        melids = self.prepareMelIDs(melids)
        timer = Timer()

        self.cursor.execute(query)
        mel_list = {}
        for melid in melids:
            mel_list[melid] = Melody()
        bad_ids = []
        count = 0
        totalDur = 0
        #timer.end("readMelodies: Preparation done")
        old_id = -1
        num_mel = 0
        for row in self.cursor:
            melid = row["melid"]
            count += 1

            if melid != old_id:
                num_mel +=1
                self.proc_hook(num_mel, len(melids), "")
                old_id = melid
            # mne = self.3(row, simplifyBeatProps)
            # print mne
            try:
                timer.start()
                mne = self.parseMelodyEvent(row, simplifyBeatProps)
                mel_list[melid].append(mne)
                totalDur += timer.end()
            except:
                bad_ids.append(melid)

        if self.verbose:
            print("="*60)
            print("readMelodies:")
            print("-- Total duration: {}".format(totalDur))
            print("-- Mean duration: {}".format(totalDur/count))
            print("-- #Events: {}".format(count))
            print("-- #Bad Events: {}".format(len(bad_ids)))
            print("="*60)
        return mel_list


    def castSectionValue(self, val, sectType):
        if sectType == "PHRASE":
            try:
                val = int(val)
            except:
                val = 1
        elif sectType == "CHORD":
            return Chord(val)
        elif sectType == "CHORUS":
            return int(val)
        elif sectType == "FORM":
            return FormName(val)
        elif sectType == "IDEA":
            return Idea(val)
        elif sectType == "KEY":
            try:
                key = Key.fromString(val)
            except:
                key = Key(val.split(" ")[0])
            return key
        else:
            raise ValueError("Unknown Section Type: {}".format(sectType))
        return val

    def readSection(self, melID, sectType):
        self.cursor.execute("SELECT * FROM sections WHERE melid = (?) AND type=(?)", (melID, sectType))
        sl = SectionList()
        for row in self.cursor:
            sect = Section(sectType, self.castSectionValue(str(row["value"]), sectType), row["start"], row["end"])
            sl.append(sect)
        if len(sl):
            return sl
        return None

    def readSections(self, melids=None, sectType=None, with_parse=True):
        sect_types = []
        if sectType == None:
            self.cursor.execute("SELECT DISTINCT type FROM sections")
            for row in self.cursor:
                sect_types.append(str(row["type"]))
            query = self.getMelIdClause("sections", melids)
        else:
            sect_types.append(sectType)
            query = self.getMelIdClause("sections", melids)
            if melids == None:
                query = "{} WHERE type = '{}'".format(query, sectType)
            else:
                query = "{} AND type = '{}'".format(query, sectType)

        melids = self.prepareMelIDs(melids)

        self.cursor.execute(query)

        sll = {}
        for melid in melids:
            sll[melid] =  {}
            for st in sect_types:
                if with_parse:
                    sll[melid][st] = SectionList(sectionType=st)
                else:
                    sll[melid][st] = []

        for row in self.cursor:
            melid = row["melid"]
            sectType = row["type"]
            if with_parse:
                val = self.castSectionValue(str(row["value"]), sectType)
                sect = Section(sectType, val, row["start"], row["end"])
            else:
                sect = (row["value"], row["start"], row["end"])
            #print "melid, sect", melid, sectType, sect
            sll[melid][sectType].append(sect)

        return sll

    def _parse_beattrack_entry(self, row):
        bar = get_safe_value_from_dict(row, "bar", "")
        beat = get_safe_value_from_dict(row, "beat", "")
        form = get_safe_value_from_dict(row, "form", "")
        chord = get_safe_value_from_dict(row, "chord", "")
        bass_pitch = get_safe_value_from_dict(row, "bass_pitch",  "")
        chorus_id = get_safe_value_from_dict(row, "chorus_id",  "")
        sig = get_safe_value_from_dict(row, "signature", "")
        abe = AnnotatedBeatEvent(row["onset"], None, form, chord, bass_pitch, chorus_id)

        return abe, sig, bar, beat

    def readBeatTracks(self, melids=None):
        query = self.getMelIdClause("beats", melids)
        melids = self.prepareMelIDs(melids)
        self.cursor.execute(query)
        beat_tracks =  {}
        sig_list = {}
        bar_offsets = {}
        beat_offsets = {}
        for mid in melids:
            beat_tracks[mid] = AnnotatedBeatTrack()
            sig_list[mid] = []
            bar_offsets[mid] = None
            beat_offsets[mid] = None
        for row in self.cursor:
            melid = row["melid"]
            abe, sig, bar, beat = self._parse_beattrack_entry(row)
            beat_tracks[melid].append(abe)
            sig_list[melid].append(sig)
            if bar_offsets[melid] is None:
                bar_offsets[melid] = bar
            if beat_offsets[melid] is None:
                beat_offsets[melid] = beat
            #beat_tracks[melid].append(RhythmEvent(row["onset"]))
        for melid in melids:
            if melid in sig_list and len("".join(sig_list[melid])) > 0:
                #print "Added metrical position with bar offset {} and  beat offset: {} for melid {}".format(bar_offsets[melid], beat_offsets[melid], melid)
                beat_tracks[melid] = beat_tracks[melid].metricalPositionsFromSignatures(sig_list[melid], bar_offset=bar_offsets[melid], beat_offset=beat_offsets[melid])
        return beat_tracks

    def readBeatTrack(self, melID):
        """ CURRENTLY UNUSED """
        self.cursor.execute("SELECT * FROM beats WHERE melid = (?)", (melID,))
        bt = AnnotatedBeatTrack()
        for row in self.cursor:
            abe, sig = self._parse_beattrack_entry(row)
            bt.append(abe)
            sig_list.append(sig)

        if len("".join(sig_list)) > 0:
            bt.metricalPositionsFromSignatures(sig_list)
        if len(bt):
            return bt
        return None

    def readDBInfo(self):
        self.cursor.execute("SELECT * FROM db_info LIMIT 1")
        dbinfo = {}
        row =  self.cursor.fetchone()
        if row:
            dbinfo = dict(row)
        return dbinfo

    def parseSection(self, sections, sectType, withCheck=True):
        sl = SectionList(sectType)
        for entry in sections[sectType]:
            #entry of form
            #row["value"], row["start"], row["end"])
            val = self.castSectionValue(entry[0], sectType)
            sect = Section(sectType, val, entry[1], entry[2])
            sl.append(sect, withCheck=withCheck)
        return sl

    def safeSectionParse(self, sections, sectType, default=None, withCheck=True):
        try:
            sect  = self.parseSection(sections, sectType, withCheck)
        except:
            sect = default
        return sect

    def readSolos(self, melids=None):
        t = Timer()
        t.start()
        melodies    = self.readMelodies(melids)
        t.start()
        smd         = self.readSoloMetadata(melids)
        t.start()
        sections    = self.readSections(melids, with_parse=False)
        t.start()
        bts         = self.readBeatTracks(melids)
        melids      = self.prepareMelIDs(melids)
        solos = {}
        bad_ids = []

        for i, mid in enumerate(melids):
            ps  = self.safeSectionParse(sections[mid], "PHRASE")
            cs  = self.safeSectionParse(sections[mid], "CHORD")
            chs = self.safeSectionParse(sections[mid], "CHORUS")
            fs  = self.safeSectionParse(sections[mid], "FORM", withCheck=False)
            #do we have Key sections annotations?
            try:
                ks  = self.parseSection(sections[mid], "KEY")
            except:
                #if not, try to use key from metadata
                try:
                    key = smd[mid].getField("key")
                    if not key.empty():
                        ks = SectionList("KEY")
                        ks.append(Section("KEY", key, 0, len(melodies[mid])-1))
                except:
                    ks = None
            #do we have IFA annotations?
            try:
                ifs  = self.safeSectionParse(sections[mid], "IDEA")
                if len(ifs) == 0:
                    ifs = None
            except:
                ifs = None
            #try to get a valid solo object
            try:
                s = Solo(melody=melodies[mid],
                         metadata=smd[mid],
                         beatTrack=bts[mid],
                         phrases=ps,
                         form=fs,
                         chorus=chs,
                         chords=cs,
                         keys=ks,
                         ideas=ifs)
            except:
                bad_ids.append(mid)
                s = None

            if s.metadata.soloinfo.choruscount == None:
               s.metadata.soloinfo.choruscount =  s.getChorusCount()

            solos[mid] = s
        if self.verbose:
            print("#offending solos: {}".format(len(bad_ids)))
        return solos

    def readEsacSongs(self, melids=None):
        melids      = self.prepareMelIDs(melids)
        melodies    = self.readMelodies(melids)
        eis         = self.readEsacMetadata(melids)
        sections    = self.readSections(melids, with_parse=False)
        songs = {}
        bad_ids = []

        for i, melid in enumerate(melids):
            ps  = self.safeSectionParse(sections[melid], "PHRASE")
            cs  = self.safeSectionParse(sections[melid], "CHORDS")
            try:
                ks  = self.parseSection(sections[melid], "KEY")
            except:
                try:
                    key = Key.fromString(eis[melid].getField("key"))
                    if not key.empty():
                        ks = SectionList("KEY")
                        ks.append(Section("KEY", key, 0, len(melodies[melid])-1))
                except:
                    ks = None
            try:
                solo = Solo(melody=melodies[melid], phrases=ps, chords=cs, keys=ks)
                key = solo.estimateKey(suggested_root=eis[melid].getEsacInfo().getKey())
                #print "Estimated key: {}, Orig: {}".format(key, eis[melid].getEsacInfo().getKey())

                eis[melid].__dict__["key"] = key
                solo.__dict__["esacinfo"] = eis[melid]
                songs[melid] = solo
            except:
                bad_ids.append(melid)
                songs[melid] = None

        if self.verbose:
            print("#offending songs: {}".format(len(bad_ids)))
        return songs


    def readPopSongs(self, melids=None):
        melids      = self.prepareMelIDs(melids)
        melodies    = self.readMelodies(melids)
        pmd         = self.readPopSongsMetadata(melids)

        sections    = self.readSections(melids, with_parse=False)
        songs = {}
        bad_ids = []
        for i, mid in enumerate(melids):
            ps  = self.safeSectionParse(sections[mid], "PHRASE")
            try:
                s = Song(melody=melodies[mid], metadata=pmd[mid], phrases=ps)
                songs[mid] = s
            except:
                #print mid, ps.getEndID(), len(melodies[mid])
                bad_ids.append(mid)
                songs[mid] = None
        if self.verbose:
            print("#offending songs: {}".format(len(bad_ids)))
        return songs


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

            si = SoloInfo(performer=str(row["performer"]),
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
        try:
            solotime = str(row["solotime"]).replace(" ", "")
            elems = solotime.split("-")
            solostart = elems[0]
            if len(elems)>1:
                soloend  = elems[1]
            else:
                soloend = "NA"
            ti = TranscriptionInfo(fileNameSV=str(row["filename_sv"]), status=str(row["status"]))
            ti.solotime  = solotime
            ti.solostart = solostart
            ti.soloend   = soloend

        except Exception as e:
            #print "parseTranscriptionInfo: Error"
            #print type(row), row, row["artist"]
            ti = None
        return ti

    def parseCompositionInfo(self, row):
        try:
            ci = CompositionInfo(composer=str(row["composer"]),
                                 form=str(row["form"]),
                                 tonality_type=str(row["tonalitytype"]),
                                 genre=str(row["genre"])
                                 )
        except:
            ci = None
        return ci

    def parseRecordInfo(self, row):
        try:
            try:
                trackno= int(row["trackno"])
            except:
                trackno= None
            ri = RecordInfo(artist=str(row["artist"]),
                                 recordTitle=str(row["recordtitle"]),
                                 lineup=str(row["lineup"]),
                                 label=str(row["label"]),
                                 recordBib=str(row["recordbib"]),
                                 musicBrainzID=str(row["mbzid"]),
                                 trackNumber=trackno,
                                 releaseDate=str(row["releasedate"]),
                                 recordingDate=str(row["recordingdate"])
                                 )
        except:
            ri = None
        return ri

    def readEsacMetadata(self, melids=None):
        timer = Timer()
        query = self.getMelIdClause("esac_info", melids)
        melids = self.prepareMelIDs(melids)
        self.cursor.execute(query)
        esac_metadata = {}
        bad_ids = []
        count = 0
        totalDur = 0

        for row in self.cursor:
            melid = row["melid"]
            count += 1
            timer.start()

            try:
                esac_info = EsacInfo(
                             collection=row["collection"],
                             melid=row["melid"],
                             esacid=row["esacid"],
                             key = row["key"],
                             unit = row["unit"],
                             signature = row["signature"],
                             title = row["title"],
                             region = row["region"],
                             function = row["function"],
                             comment = row["comment"],
                             cnr = row["cnr"],
                             source = row["source"],
                             tunefamily = row["tunefamily"],
                             text = row["text"],
                             melstring = row["melstring"])
            except:
                esac_info = None
                bad_ids.append(melid)
                continue

            totalDur += timer.end()
            esac_metadata[melid] = EsacMetaData(esac_info)

        if self.verbose:
            print("readEsacMetadata:")
            print("--Mean duration: {}".format(totalDur / count))
            print("--Count: {}".format(count))
            print("--#Bad IDs: {}".format(len(bad_ids)))

        return esac_metadata

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

        count = 0
        totalDur = 0
        query = "SELECT * FROM solo_info, composition_info, record_info, transcription_info WHERE solo_info.melid = composition_info.melid and solo_info.melid = record_info.melid and solo_info.melid = transcription_info.melid {}".format(melid_clause)
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
                ci = self.parseCompositionInfo(row)
            except:
                ci = None
                bad_ids.append(melid)

            ri = self.parseRecordInfo(row)
            try:
                ri = self.parseRecordInfo(row)
            except:
                ri = None
                bad_ids.append(melid)
            try:
                ti = self.parseTranscriptionInfo(row)
            except:
                ti = None
                bad_ids.append(melid)

            totalDur += timer.end()
            smd[melid]= SoloMetaData(transcriptionInfo=ti, soloInfo=si, compositionInfo=ci, recordInfo=ri)

        if self.verbose:
            print("readSoloMetadata:")
            print("--Mean duration: {}".format(totalDur/count))
            print("--Count: {}".format(count))
            print("--#Bad IDs: {}".format(len(set(bad_ids))))

        return smd

    def readPopSongsMetadata(self, melids=None):
        timer = Timer()
        query = self.getMelIdClause("popsong_info", melids)
        melids = self.prepareMelIDs(melids)
        self.cursor.execute(query)
        mds = {}
        bad_ids = []
        count = 0
        totalDur = 0
        #timer.end("Preparation done")
        for row in self.cursor:
            melid = row["melid"]
            count += 1
            timer.start()
            try:
                pi = PopSongInfo(filename=row["filename"],
                             artist=row["artist"],
                             avgTempoBPM = float(row["avgtempo"]),
                             title = row["title"],
                             style = row["style"],
                             tempo_class = row["tempoclass"],
                             key = row["key"],
                             chord_changes = row["chordchanges"],
                             mainSignature = row["signature"],
                             year = row["year"],
                             country = row["country"]
                             )
                pmd = PopSongMetaData(pi)
            except:
                pmd = None
                bad_ids.append(melid)
                continue
            totalDur += timer.end()
            mds[melid]= pmd
        if self.verbose:
            print("readPopsongMetadata:")
            print("--Mean duration: {}".format(totalDur/count))
            print("--Count: {}".format(count))
            print("--#Bad IDs: {}".format(len(bad_ids)))
        return mds


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

    def query(self, query):
        if query.upper().count("DROP")>0 or query.upper().count("DELETE")>0 or query.upper().count("UPDATE")>0 or query.upper().count("ALTER")>0 or query.upper().count("INSERT")>0:
            raise ValueError("Illegal query:" + query)
        self.cursor.execute(query)
        return [row for row in self.cursor]


    def open(self):
        self.conn = sqlite3.connect(self.__filename)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def close(self):
        try:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()
            del self.cursor
            del self.conn
        except:
            pass

    def open_second(self):
        self.conn2 = sqlite3.connect(self.__filename)
        self.conn2.row_factory = sqlite3.Row
        self.cursor2 = self.conn2.cursor()

    def close_second(self):
        try:
            self.conn2.commit()
            self.cursor2.close()
            self.conn2.close()
            del self.cursor2
            del self.conn2
        except:
            pass


    def __str__(self):
        return "Not Implemented"

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __del__(self):
        self.close()
        return self


    filename = property(getFilename)
