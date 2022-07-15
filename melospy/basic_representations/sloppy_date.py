""" Class for sloppy date"""
from datetime import date, datetime

#dummy call to strptime due to some known bug in Spyder

throwaway = datetime.strptime('20110101', '%Y%m%d')

class SloppyDate(object):
    """ Sloppy Date wraps around standard date object, since we oft need dates which missing information.
        We want to reflect that instead of assuming dummy dates
    """ 
    def __init__(self, year = None, month = None, day = None):
        self.setDate(year, month, day)
        self.__year   = year
        self.__month  = month
        self.__day    = day

    @staticmethod
    def fromString(datestr):
        if len(datestr) == 0:
            return SloppyDate()
        fmtstr = "%d.%m.%Y"
        year, month, day  = None, None, None
        try:
            tmpdate  = datetime.strptime(datestr, fmtstr).date()
            year, month, day = tmpdate.year, tmpdate.month, tmpdate.day
        except Exception as e:
            try:
                tmpdate  = datetime.strptime(datestr, "%m.%Y").date()
                year, month = tmpdate.year, tmpdate.month
            except Exception as e:
                try:
                    tmpdate  = datetime.strptime(datestr, "%Y").date()
                    year = tmpdate.year
                except Exception:
                    raise Exception("'{}' does not match sloppy date format.".format(datestr))
        return SloppyDate(year, month, day)

    def setYear(self, year):
        try: 
            self.setDate(year, self.__month, self.__day)
        except Exception:
            raise Exception("Invalid year given.")
        self.__year = year

    def getYear(self):
        return self.__year

    def setMonth(self, month):
        try: 
            self.setDate(self.__year, month, self.__day)
        except Exception:
            raise Exception("Invalid month given.")
        self.__month = month

    def getMonth(self):
        return self.__month

    def setDay(self, day):
        try: 
            self.setDate(self.__year, self.__month, day)
        except Exception:
            raise Exception("Invalid day given.")
        self.__day = day

    def getDay(self):
        return self.__day
        
    def setDate(self, year, month, day):
        if year != None:                
            if month == None: 
                if day != None:
                    raise ValueError("Day cannot be given without month")
                else:
                    self.__date   = date(year, 1, 1) 
            else:
                if day == None: 
                    self.__date   = date(year, month, 1) 
                else:
                    self.__date   = date(year, month, day) 
        else:
            if month != None or day != None:
                raise ValueError("Month and day cannot be given without year")
            else:
                self.__date = None

    def getDate(self):
        return self.__date

    def __eq__(self, other): 
        if not isinstance(other, SloppyDate): return False
        return self.__date == other.__date

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        if self.__year == None:
            return ''
        if self.__day == None:
            if self.__month == None:
                return self.__date.strftime("%Y")
            else:
                return self.__date.strftime("%b %Y")
        else:
              return self.__date.strftime("%d.%m.%Y")
        raise Exception("Something weird happened")
        
    year  = property(getYear, setYear) 
    month = property(getMonth, setMonth) 
    day   = property(getDay, setDay) 
    date  = property(getDate)
