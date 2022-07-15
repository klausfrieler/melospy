""" IntSpan Class, integer spans as sets of consecutive integer
    Taken from http://pydoc.net/Python/IntSpan/0.505/intspan/
"""    

import copy
from itertools import count, groupby


class IntSpan(set):
    def __init__(self, initial=None):
        super(IntSpan, self).__init__()
        if initial:
            self.update(initial)
            
    def copy(self):
        return copy.copy(self)
        
    def update(self, items):
        super(IntSpan, self).update(self._parse_range(items))
        return self

    def clear(self):
        super(IntSpan, self).clear()
        return self
        
    def discard(self, items):
        for item in self._parse_range(items):
            super(IntSpan, self).discard(item)
        return self
            
    def remove(self, items):
        for item in self._parse_range(items):
            super(IntSpan, self).remove(item)
        return self
            
    def add(self, items):
        for item in self._parse_range(items):
            super(IntSpan, self).add(item)
        return self
    
    def issubset(self, items):
        return super(IntSpan, self).issubset(self._parse_range(items))
    
    def issuperset(self, items):
        return super(IntSpan, self).issuperset(self._parse_range(items))
    
    def union(self, items):
        return IntSpan(super(IntSpan, self).union(self._parse_range(items)))

    def intersection(self, items):
        return IntSpan(super(IntSpan, self).intersection(self._parse_range(items)))
    
    def difference(self, items):
        return IntSpan(super(IntSpan, self).difference(self._parse_range(items)))
    
    def symmetric_difference(self, items):
        return IntSpan(super(IntSpan, self).symmetric_difference(self._parse_range(items)))

    def coverage(self, items):
        litems  = len(IntSpan(items))
        lisec   = len(self.intersection(items))
        if litems == 0:
            raise ValueError("IntSpan of items '{}' is empty".format(items))
        cover = float(lisec)/float(litems)
        if cover > 1.0:
            cover = 1.0
        return cover
    __le__  = issubset
    __ge__  = issuperset 
    __or__  = union
    __and__ = intersection
    __sub__ = difference
    __xor__ = symmetric_difference
    
    def __ior__(self, items):
        return super(IntSpan, self).__ior__(self._parse_range(items))
        
    def __iand__(self, items):
        return super(IntSpan, self).__iand__(self._parse_range(items))

    def __isub__(self, items):
        return super(IntSpan, self).__isub__(self._parse_range(items))
        
    def __ixor__(self, items):
        return super(IntSpan, self).__ixor__(self._parse_range(items))
    
    def __eq__(self, items):
        return super(IntSpan, self).__eq__(self._parse_range(items))
        
    def __iter__(self):
        """
        Iterate in ascending order.
        """
        return iter(sorted(super(IntSpan, self).__iter__()))
    
    def pop(self):
        min_item = min(self)
        self.discard(min_item)
        return min_item
    
        # this method required only for PyPy, which otherwise gets the wrong
        # answer (unordered)
    @staticmethod
    def from_start_length(start, l):        
        if l < 0:
            return IntSpan(list(range(start+l, start)))    
        return IntSpan(list(range(start, start + l)))    

    @staticmethod
    def from_start_end(start, end):        
        if end < start:
            start, end = end, start
        return IntSpan(list(range(start, end+1)))    

    @staticmethod
    def _parse_range(datum):
        if isinstance(datum, str):
            result = []
            for part in datum.split(','):
                if '-' in part:
                    start, stop = part.split('-')
                    result.extend(list(range(int(start), int(stop)+1)))
                else:
                    result.append(int(part))
            return result
        else:
            return datum if hasattr(datum, '__iter__') else [ datum ]
        
    @staticmethod
    def _as_range(iterable): 
        l = list(iterable)
        if len(l) > 1:
            return '{0}-{1}'.format(l[0], l[-1])
        else:
            return '{0}'.format(l[0])
    
    @staticmethod
    def _start_duration(iterable):
        l = list(iterable)
        return (l[0], l[-1]-l[0]+1)        
        #return IntSpan(IntSpan._as_range(iterable))
        
    def as_start_duration_patches(self):
        items = sorted(self)
        ret = []
        for _, g in groupby(items, key=lambda n, c=count(): n-next(c)):
            ret.append(self._start_duration(g))
        return ret
        
    def __getitem__(self, i):        
        return sorted(self)[i]

    def __repr__(self):        
        return 'IntSpan({0!r})'.format(self.__str__())
    
    def __str__(self):
        items = sorted(self)
        return ','.join(self._as_range(g) for _, g in groupby(items, key=lambda n, c=count(): n-next(c)))

# see Jeff Mercado's answer to http://codereview.stackexchange.com/questions/5196/grouping-consecutive-numbers-into-ranges-in-python-3-2
# see also: http://stackoverflow.com/questions/2927213/python-finding-n-consecutive-numbers-in-a-list
