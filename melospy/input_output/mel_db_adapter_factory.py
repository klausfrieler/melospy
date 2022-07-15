""" Class implementation of MelDBAdapterFactory"""

from melospy.input_output.mel_db_sqlite3_adapter import *
from melospy.input_output.mel_db_sqlite3_adapter2 import *
from melospy.tools.commandline_tools.dbinfo import *


class MelDBAdapterFactory(object):

    def __init__(self, dbinfo):
        self.dbinfo = dbinfo
        if dbinfo.content_type in ["sv", "wjazzd", "omnibook", "popsong"]:
            self._set_version(dbinfo)
        else:
            self.major = 1

    def _set_version(self, dbinfo):
        if dbinfo == None:
            raise ValueError("Invalid DBInfo object given")
        if not dbinfo.version:
            #self.major = self._query_version_from_db()
            try:
                self.major = self._query_version_from_db()
            except:
                print("Could not determine DB version")
                self.major = 1
        else:
            self.major = int(self.dbinfo.version["major"])

    def _query_version_from_db(self):
        major = None
        with MelDBSqliteAdapter(self.dbinfo.path) as mdb:
            dbinfo = mdb.readDBInfo()
            major = dbinfo["major"]
        return major

    def create(self, proc_hook=None, verbose=False):
        if self.dbinfo == None:
            raise RuntimeError("Cannot create DB adapter")

        dbadapter = None

        if self.major > 1:
            dbadapter = MelDBSqliteAdapter2(self.dbinfo.path, self.dbinfo.version, verbose=verbose, proc_hook=proc_hook)
        else:
            dbadapter = MelDBSqliteAdapter(self.dbinfo.path, self.dbinfo.version, verbose=verbose, proc_hook=proc_hook)
        if verbose:
            print("Created ", type(dbadapter))
        return dbadapter
