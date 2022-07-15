""" Class implementation of ConfigParameter"""
from melospy.basic_representations.jm_util import get_safe_value_from_dict, safe_set


class ConfigParameter(object):
    """base class for parameter settings"""
    field_names = []

    def __init__(self):
        #nothing  to do, actually
        pass

    @staticmethod
    def fromDict(params, allowNone=False):
        if not isinstance(params, dict):
            raise TypeError("Expected dictionary for 'params', got {}".format(type(params)))
        cp = ConfigParameter()

        for e in params:
            if len(ConfigParameter.field_names) > 0 :
                if e not in ConfigParameter.field_names:
                    raise TypeError("Invalid field name:{}".format(e))
            cp.setValue(e, params[e], type(params[e]), allowNone)
        return cp

    def setValue(self, name, val, typelist=None, allowNone=False):
        safe_set(self, name, val, typelist, allowNone)

    def setValueWithDomainCheck(self, name, val, allowed, case_sensitive=True):
        if case_sensitive == False:
            tmp_val = val.lower()
        else:
            tmp_val = val

        if tmp_val not in allowed:
            raise ValueError("Invalid value:{}. Allowed: {}".format(val, allowed))
        safe_set(self, name, val)

    def getValue(self, name, default=None):
        return get_safe_value_from_dict(self.__dict__, name, default)

    def __str__(self):
        return str(self.__dict__)

    def __rep__(self):
        return str(self.__dict__)

    def __getitem__(self, name):
        return self.__dict__[name]
