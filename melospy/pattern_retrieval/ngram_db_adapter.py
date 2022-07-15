""" Class implementation of NGramDBAdapter, part of the NGram-Database subproject"""

import sqlite3 as sqlite3
import time

from melospy.pattern_retrieval.ngram_database import *
from melospy.pattern_retrieval.ngram_refrep import *


class NGramDBAdapter(object):

    def __init__(self, filename = ":memory:", ngramdb = None):
        """ Initialize module """
        self.__filename  = filename
        self.setNGramDatabase(ngramdb)

    def getFilename(self):
        return self.__filename

    def getNGramDatabase(self):
        return self.__ndb

    def getCursor(self):
        return self.cursor

    def getConnection(self):
        return self.conn

    def setNGramRefRep(self, ngramrefrep):
        if ngramrefrep and not isinstance(ngramrefrep, NGramRefRepository):
            raise TypeError("Expected NGramRefRepository, got :{}".format(type(ngramrefrep)))
        self.__nrep = ngramrefrep

    def setNGramDatabase(self, ngramdb):
        if ngramdb and not isinstance(ngramdb, NGramDatabase):
            raise TypeError("Expected NGramDatabse, got :{}".format(type(ngramdb)))
        self.__ndb= ngramdb
        if ngramdb:
            self.setNGramRefRep(ngramdb.getRep())

    def dropTables(self):
        self.conn.executescript("""
            DROP TABLE IF EXISTS codebook;
            DROP TABLE IF EXISTS repository;
            DROP TABLE IF EXISTS repository_keys;
            DROP TABLE IF EXISTS ngrams;
            DROP TABLE IF EXISTS ngram_pos;
            DROP TABLE IF EXISTS metadata;
            VACUUM;
            """)
        print("Tables dropped")


    def createDatabase(self, withIndex = False):
        self.dropTables()
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS codebook(
              code   INTEGER PRIMARY KEY,
              value  TEXT
            );

            CREATE TABLE  IF NOT EXISTS repository(
              rowid   INTEGER PRIMARY KEY AUTOINCREMENT,
              seqid   INTEGER,
              eventid INTEGER,
              code    INTEGER,
              FOREIGN KEY(code) REFERENCES codebook(code)
            );

            CREATE TABLE IF NOT EXISTS repository_keys(
              seqid  INTEGER PRIMARY KEY,
              key    TEXT
            );

            CREATE TABLE  IF NOT EXISTS ngrams(
              ngramid INTEGER PRIMARY KEY,
              tag     TEXT,
              freq    INTEGER,
              N       INTEGER
            );

            CREATE TABLE  IF NOT EXISTS ngram_pos(
              seqid     INTEGER,
              startid   INTEGER,
              ngramid   INTEGER,
              FOREIGN KEY(seqid) REFERENCES repository(seqid),
              FOREIGN KEY(ngramid) REFERENCES ngrams(ngramid)
            );

            CREATE TABLE  IF NOT EXISTS metadata(
              pruned        INTEGER,
              transform     TEXT
            );
        """)
        print("Database created")
        if withIndex:
            self.dropIndices()
            self.createIndices()

    def createIndices(self):
        self.cursor.executescript("""
            CREATE INDEX IF NOT EXISTS posind ON ngram_pos (ngramid);
            CREATE INDEX IF NOT EXISTS ngramdind ON ngrams (ngramid, N);
            CREATE INDEX IF NOT EXISTS repind ON repository (seqid);

        """)
        print("Indices created")

    def dropIndices(self):
        self.cursor.executescript("""
            DROP INDEX IF EXISTS posind;
            DROP INDEX IF EXISTS nrgamind;
            DROP INDEX IF EXISTS repind;

        """)
        print("Indices dropped")

    def rebuildIndices(self):
        self.dropIndices()
        self.createIndices()

    def readDatabase(self, rebuild = False):
        if self.__ndb:
            del self.__ndb
        ndb = self.readNGramDatabase(rebuild = rebuild)
        self.setNGramDatabase(ndb)
        return ndb

    def writeDatabase(self):
        print("Writing database")
        if not self.__ndb:
            raise RuntimeError("No data to fill into database.")
        self.insertCodebook()
        self.insertRepository()
        self.insertNGrams()
        self.insertMetadata()

    def insertMetadata(self):
        #print tmp
        self.conn.execute("INSERT INTO metadata (pruned, transform) VALUES (?,?)", (self.__ndb.getPruned(), self.__ndb.getTransformation()))

    def readMetadata(self):
        self.cursor.execute("SELECT * FROM metadata")
        row = self.cursor.fetchone()
        return row["pruned"], row["transform"]

    def insertCodebook(self):
        tmp = [(int(k), str(self.__nrep.codebook[k])) for k in self.__nrep.codebook]
        #print tmp
        self.conn.executemany("INSERT INTO codebook (code, value) VALUES (?,?)", tmp)

    def printCodebook(self):
        self.cursor.execute("SELECT * FROM codebook")
        for row in self.cursor:
            print("Code: {}, Value: {}".format(row["code"], row["value"]))

    def readCodebook(self):
        codebook = {}
        self.cursor.execute("SELECT * FROM codebook")
        for row in self.cursor:
            try:
                codebook[row["code"]] = eval(row["value"])
            except Exception:
                codebook[row["code"]] = str(row["value"])
            #finally:
            #    raise RuntimeError("Someting deeply wrong")
        return codebook

    def insertRepository(self):
        for seqid in range(len(self.__nrep)):
            seq = self.__nrep.getCodedSequence(seqid)
            key = self.__nrep.getKeyFromId(seqid)
            tmp = [(seqid, i, seq[i]) for i in range(len(seq))]
            self.conn.executemany("INSERT INTO repository (seqid, eventid, code) VALUES (?,?,?)", tmp)
            self.conn.execute("INSERT INTO repository_keys VALUES (?,?)", (seqid, key))

    def printRepository(self, limit = 0):
        if limit>0:
            self.cursor.execute("SELECT * FROM repository LIMIT {}".format(limit))
        else:
            self.cursor.execute("SELECT * FROM repository")
        for row in self.cursor:
            print("Rowid:{}, Seqid: {}, EventId:{}, Code:{}".format(row["rowid"], row["seqid"], row["eventid"], row["code"]))
        self.cursor.execute("SELECT * FROM repository_keys")
        for row in self.cursor:
            print("Seqid: {}, Key:{}".format(row["seqid"], row["key"]))

    def readRepository(self, codebook = None, stringify = False):
        if not codebook:
            codebook = self.readCodebook()
        self.cursor.execute("SELECT DISTINCT seqid FROM repository")
        seqid   = [row[0] for row in self.cursor]
        nr      = NGramRefRepository()
        rep     = []
        keys    = []
        for s in seqid:
            self.cursor.execute("SELECT * FROM repository WHERE seqid=?", (s,))
            if stringify:
                seq = "".join([str(codebook[row["code"]]) for row in self.cursor])
            else:
                seq = [codebook[row["code"]] for row in self.cursor]
            self.cursor.execute("SELECT DISTINCT key FROM repository_keys WHERE seqid=?", (s,))
            key =  [str(row[0]) for row in self.cursor][0]
            rep.append(seq)
            keys.append(key)
        nr.extend(rep, keys)
        return nr

    def insertNGrams(self):
        ngramid = 0
        for nl in self.__ndb:
            for n in nl:
                ngramid += 1
                tmp = (ngramid, n.getTag(), n.getFreq(), n.N)
                self.insertNGramPositions(n, ngramid)
                self.conn.execute("INSERT INTO ngrams (ngramid, tag, freq, N) VALUES (?,?,?,?)", tmp)

    def insertNGramPositions(self, ngram, ngramid):
        tmp = [(n.getSeqId(), n.getStartId(), ngramid) for n in ngram]
        self.conn.executemany("INSERT INTO ngram_pos VALUES (?,?,?)", tmp)


    def printNGrams(self, limit = 0):
        if limit>0:
            self.cursor.execute("SELECT * FROM ngrams LIMIT {}".format(limit))
        else:
            self.cursor.execute("SELECT * FROM ngrams")
        for row in self.cursor:
            print("ngramid:{}, tag: {}, freq:{}, N:{}".format(row["ngramid"], row["tag"], row["freq"], row["N"]))

    def readNGramPositions(self, ngramid, N = -1):
        self.cursor.execute("SELECT * FROM ngram_pos WHERE ngramid = ?", (ngramid,))
        ngrampos = [NGramPosition(row["seqid"], row["startid"], N)  for row in self.cursor]
        #print "Found ", len(ngrampos), " positioms for id=", ngramid, " N=", N
        #print "First pos:", ngrampos[0]
        return ngrampos

    def readNGram(self, ngramid, rep = None):
        self.cursor.execute("SELECT N, tag FROM ngrams WHERE ngramid=?", (ngramid,))
        N, tag = [(row["N"], row["tag"]) for row in self.cursor][0]
        #print "Found Ngram with  id=", ngramid, " for N=", N, " and tag=", tag
        n = NGram(N, rep, tag=tag)
        npos = self.readNGramPositions(ngramid, N)
        n.extend(npos)
        return n

    def readNGramList(self, N, rep = None):
        start = time.process_time()
        self.cursor.execute("SELECT ngramid FROM ngrams WHERE N=?", (N,))
        ngramids = [row[0] for row in self.cursor]
        #print "Found ", len(ngramids), " ngramids for N=", N
        nl = NGramList(N, rep)
        for ngramid in ngramids:
            ng = self.readNGram(ngramid, rep)
            #print "Read NGRam {} in {} s".format(ngramid, round(time.process_time()-start,3))
            #start = time.process_time()
            #print "NGRam:", ng
            nl.unsafe_add(ng)
        print("Read NGRamList {} in {} s".format(N, round(time.process_time()-start, 3)))
        return nl

    def readNGramList2(self, N, rep = None):
        #start = time.process_time()
        self.cursor.execute("""
            SELECT  ngram_pos.seqid AS seqid,
                    ngram_pos.startid AS startid,
                    ngrams.tag AS tag,
                    ngrams.ngramid AS ngramid
            FROM ngram_pos, ngrams
            WHERE
                ngrams.ngramid = ngram_pos.ngramid
            AND
                ngrams.ngramid IN
                (SELECT ngramid FROM ngrams WHERE N=?)
            ORDER BY ngrams.ngramid ASC;
            """, (N,))
        #print "SQL executed in {} s".format(round(time.process_time()-start,3))
        start = time.process_time()

        nl          = NGramList(N, rep)
        npos        = []
        old_id      = -1
        ng          = None
        i           = 0
        ngram_count = 0

        for row in self.cursor:
            #print i, row["ngramid"], row["seqid"], row["startid"]
            ngramid = row["ngramid"]
            #print "oldid: {} newid: {}".format(old_id, ngramid)
            if ngramid != old_id:
                if old_id >-1:
                    nl.add(ng)
                ng = NGram(N, rep, tag=row["tag"])
                old_id = ngramid
                ngram_count += 1
            ng.unsafe_add(NGramPosition(row["seqid"], row["startid"], N))
            i +=1
        nl.add(ng)
        ngram_count += 1
        #print "Read NGramList N={} with {} elements in {} NGrams in {} s".format(N, i, ngram_count, round(time.process_time()-start,3))
        return nl


    def readNGramDatabase(self, rebuild = False, refrep = None, codebook=None):
        start = time.process_time()
        if not refrep:
            refrep = self.readRepository(codebook = codebook)
            print("Read repository in {} s".format(round(time.process_time()-start, 3)))
            start = time.process_time()
        maxN = self.findMaxN()
        pruned, transform = self.readMetadata()
        #print "Found maxN  in {} s".format(round(time.process_time()-start,3))
        #start = time.process_time()

        if rebuild:
            ndb = NGramDatabase(refrep, maxN = maxN)
            if pruned>0:
                ndb.prune(pruned+1)
            ndb.setTransformation(transform)
            return ndb

        ndb = NGramDatabase(maxN = maxN)
        #print "Read ", len(ngramids), " ngramids"
        for N in range(1, maxN+1):
            nl = self.readNGramList2(N, refrep)
            #print "Read NGram list {} in {} s".format(N, round(time.process_time()-start,3))
            #start = time.process_time()
            ndb.add(nl)
        ndb.setRep(refrep)
        ndb.setPositionFreq()
        ndb.setPruned(pruned)
        ndb.setTransformation(transform)
        return ndb

    def findMaxN(self):
        self.cursor.execute("SELECT DISTINCT N FROM ngrams ORDER BY N DESC LIMIT 1")
        return self.cursor.fetchone()["N"]

    def open(self):
        #print "Open database"
        self.conn = sqlite3.connect(self.__filename)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def close(self):
        #print "Close database"
        try:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()
            del self.cursor
            del self.conn
        except:
            pass

    def __str__(self):
        return "Not Implemented"

    def __enter__(self):
        #print "__enter__"
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        #print "__exit__"
        self.close()

    def __del__(self):
        #print "__del__"
        self.close()
        return self


    filename    = property(getFilename)
    db          = property(getNGramDatabase)
