""" Class for ideas (for Ideational Flow/Midlevel Analysis (IFA/MLA)"""

import re

import melospy.basic_representations.jm_util as util


class Idea(object):
    """ Class for ideas"""

    main_types = {"line":["line"],
                  "lick":["lick"],
                 "melody":["melody"],
                 "theme":["theme"],
                 "quote":["quote"],
                 "rhythm":["rhythm"],
                 "fragment": ["fragment"],
                 "expressive": ["expressive"],
                 "void": ["void"]
                 }
    special_names = {"oscillation":"rhythm_mr",
                     "tickmark": "line_t_dsal",
                     "slide": "line_t_asdl",
                     "rabble": "line_t_alds",
                     "golfclub": "line_t_dlas",
                     "rhythm": "rhythm_si"
                     }

    wavy_subtypes   = {"a":["ascending", "ascending"],
                       "d":["descending", "descending"],
                       "h":["horizontal", "horizontal"],
                       "cx":["convex", "convex"],
                       "cv":["concave", "concave"]}

    tick_subtypes   = {"dsal":["tickmark", "ascending"],
                       "dlas":["golfclub", "descending"],
                       "asdl":["slide", "descending"],
                       "alds":["rabble", "ascending"]}


    line_subtypes   = {"a":"ascending",
                       "d":"descending",
                       "i":"interwoven",
                       "w":"wavy",
                       "t":"tick",
                       "cx": "convex",
                       "cv":"concave"}

    interwoven_subtypes = {"aa":["stairs up", "ascending"],
                           "dd":["stairs down", "descending"],
                           "ah":["bellow lower ascending", "ascending"],
                           "dh":["bellow lower descending", "descending"],
                           "ha":["bellow upper ascending", "ascending"],
                           "hd":["bellow upper descending", "descending"],
                           "hcx":["bellow roof", "convex"],
                           "hcv":["bellow eject", "concave"],
                           "cxh":["bellow lower convex", "convex"],
                           "cvh":["bellow lower concave", "concave"],
                           "wh":["bellow lower wavy", "horizontal"],
                           "hw":["bellow upper wavy", "horizontal"],
                           "ww":["wavy", "wavy"],
                           "da":["scissors close-open", "undefined"],
                           "ad":["scissors open-close", "undefined"]
                           }

    rhythm_subtypes = {"si":"single/irregular", "sr":"single/regular", "mi":"multi/irregular", "mr":"multi/regular"}
    lick_subtypes   = {"blues":"blues", "bebop":"bebop", "motif":"motif"}

    def is_valid_type_element(self, val, level="main"):
        if level == "main":
            if val in self.main_types or val in self.special_names:
                return True
            return False
        if level == "subtype":
            if val in list(self.line_subtypes.values()):
                return True
            if val in list(self.rhythm_subtypes.values()):
                return True
            if val in list(self.lick_subtypes.values()):
                return True
            return False
        if level == "subsubtype":
            for k in self.interwoven_subtypes:
                if val == self.interwoven_subtypes[k][0]:
                    return True
            for k in self.tick_subtypes:
                if val == self.tick_subtypes[k][0]:
                    return True
            for k in self.wavy_subtypes:
                if val == self.wavy_subtypes[k][0]:
                    return True
            return False
        return False
    def __init__(self, idea_label=None):
        self.label = idea_label
        self.type = ""
        self.subtype = ""
        self.subsubtype = ""
        self.specifier = ""
        self.glue = ""
        #self.connector = ""
        self.modifier = ""
        self.backref = 0
        self.void_prefix = None
        self.main_direction = "undefined"
        if isinstance(idea_label, Idea):
            idea_label = str(idea_label)
        if idea_label != None:
            if not self.parseLabel(idea_label):
                raise ValueError("Invalid idea label: {}".format(idea_label))

    def _parseConnector(self, connector):
        conn_re = r"([#]*)(\d*)"
        m = re.match(conn_re, connector)
        if not m:
            raise ValueError("Invalid connector")
        hashes = m.group(1)
        number = m.group(2)
        backref = 0
        if len(hashes) == 0:
            if len(number)> 0:
                raise ValueError("Invalid connector")
            else:
                backref = 0
        elif len(hashes)==1:
            if len(number) == 0:
                backref = 1
            else:
                backref = int(number)
        else:
            if len(number)==0:
                backref = len(hashes)
            else:
                raise ValueError("Invalid connector")
        return backref

    def _parseModifier(self, modifier):
        if len(modifier) == 0:
            return ""
        if len(modifier) > 1:
            raise ValueError("Invalid modifier")
        return modifier

    def _parseType(self, type_str):
        #print "="*60
        #print "Parsing: {}".format(type_str)
        main_direction = "undefined"
        type_str = type_str.lower()
        if type_str == "line_w":
            type_str = "line_w_h"

        if type_str in self.special_names:
            #print "Found: {}-> {}".format(type_str, self.special_names[type_str])
            type_str = self.special_names[type_str]
        parts = type_str.split("_")
        if len(parts)<1 or len(parts)>3:
            raise ValueError("Invalid type label")

        main_type = parts[0]
        if main_type not in self.main_types:
            raise ValueError("Invalid main type")
        #print "Maintype: {}".format(main_type)
        subtype =""
        if len(parts)>1:
            subtype = parts[1]
            if main_type == "line":
                if not subtype in self.line_subtypes:
                    raise ValueError("Invalid line subtype")
                subtype = self.line_subtypes[subtype]
                main_direction = subtype

            elif main_type=="rhythm":
                if not subtype in self.rhythm_subtypes:
                    raise ValueError("Invalid rhythm subtype: {}".format(subtype))
                subtype = self.rhythm_subtypes[subtype]
                main_direction = "horizontal"
            elif main_type=="lick":
                if not subtype in self.lick_subtypes:
                    raise ValueError("Invalid lick subtype")
                subtype = self.lick_subtypes[subtype]
            else:
                raise ValueError("Invalid subtype")

        if main_type == "line" and subtype == "":
            raise ValueError("Missing line subtype")
        #print "Subtype: {}".format(subtype)

        subsubtype = ""
        if len(parts) > 2 :
            subsubtype = parts[2]

            if main_type == "line" and subtype == "tick":

                if not subsubtype in self.tick_subtypes:
                    raise ValueError("Invalid line tick subsubtype")

                main_direction = self.tick_subtypes[subsubtype][1]
                subsubtype = self.tick_subtypes[subsubtype][0]

            elif main_type == "line" and subtype == "wavy":

                wavy_subtypes = dict(list(self.tick_subtypes.items()) + list(self.wavy_subtypes.items()))

                if not subsubtype in wavy_subtypes:
                    raise ValueError("Invalid line wavy subsubtype")
                #print "Wavy line:", subsubtype
                main_direction = wavy_subtypes[subsubtype][1]
                subsubtype = wavy_subtypes[subsubtype][0]
                #print "Wavy line 2:", main_direction, subsubtype

            elif main_type == "line" and subtype == "interwoven":
                if not subsubtype in self.interwoven_subtypes:
                    raise ValueError("Invalid line interwoven subsubtype")
                main_direction = self.interwoven_subtypes[subsubtype][1]
                subsubtype = self.interwoven_subtypes[subsubtype][0]
            else:
                raise ValueError("Invalid subsubtype")

        if main_type == "line" and subtype in ["interwoven", "tick"] and subsubtype == "":
            raise ValueError("Missing line subsubtype")

        #if main_type == "rhythm":
        #    subtype, subsubtype  = subtype.split("/")

        #print "Subsubtype: {}".format(subsubtype)
        return (main_type, subtype, subsubtype, main_direction)

    def parseLabel(self, label, only_parsing=False):
        #print "parseLabel called with", label
        try:
            vals = self._parseLabel(label)
            for v in vals:
                self.__dict__[v] = vals[v]
        except:
            vals = self.from_type_string(label)
            #print "VAls[{}]".format(vals)
            if len(vals)>0:
                for v in vals:
                    self.__dict__[v] = vals[v]
            else:
                return False
        return True

    def _parseLabel(self, label):
        #print "_parseLabel called with", label

        ret = dict()
        label = util.chomp(label)
        orig_label = label

        parts = label.split("->")
        if len(parts) <= 0 or len(parts)>2:
            raise ValueError("Invalid label")

        void_prefix= False
        if len(parts) == 2:
            label = parts[1]
            void_prefix = True
        else:
            label = parts[0]

        parts = label.split(":")
        if len(parts)>2:
            raise ValueError("Invalid label")

        specifier = ""
        if len(parts) == 2:
            label = parts[0].lower()
            specifier = parts[1]

        idea_re = r"^([~]?)([#]*\d*)([\*\+\-=]?)([a-z_/]+)$"
        m = re.match(idea_re, label)
        if not m:
            raise ValueError("Invalid label")

        glue = True if m.group(1)=="~" else False

        connector = m.group(2)
        backref = self._parseConnector(connector)

        modifier = m.group(3)
        modifier = self._parseModifier(modifier)

        if modifier== "" and backref > 0:
            modifier = "*"
        if modifier != "" and backref == 0:
            backref = 1
        if modifier=='0':
            #print "modifier:", modifier
            #print "label:", orig_label
            pass

        ret["backref"] = backref
        ret["glue"] = glue
        ret["label"] = orig_label
        ret["modifier"] = modifier
        ret["void_prefix"] = void_prefix
        ret["specifier"] = specifier

        tmp_type = m.group(4)
        ret["type"], ret["subtype"], ret["subsubtype"], ret["main_direction"] = self._parseType(tmp_type)
        return ret

    def type_list(self):
        tmp = [self.type]
        if len(self.subtype)>0:
            tmp.append(self.subtype)
        if len(self.subsubtype)>0:
            tmp.append(self.subsubtype)
        return tmp

    def type_string(self):
        return "-".join(self.type_list())

    def from_type_string(self, type_string):
        if type_string == "":
            return {}
        elems = type_string.split("-")
        ret = {}
        if len(elems) >= 1:
            if self.is_valid_type_element(elems[0], level="main"):
                ret["type"] = elems[0]
            else:
                return {}
        if len(elems) >= 2:
            if self.is_valid_type_element(elems[1], level="subtype"):
                ret["subtype"] = elems[1]
            else:
                return {}
        if len(elems) >= 3:
            if self.is_valid_type_element(elems[2], level="subsubtype"):
                ret["subsubtype"] = elems[2]
            else:
                return {}
        ret["backref"] = ""
        ret["glue"] = ""
        ret["label"] = type_string
        ret["modifier"] = ""
        ret["void_prefix"] = ""
        ret["specifier"] = ""
        return ret

    def getMainDirection(self, reduced=True):
        md = self.main_direction
        if reduced:
            if md == "convex":
                md = "horizontal"
            if md == "concave":
                md = "horizontal"
        return md

    def mainly_equal(self, idea2):
        if not isinstance(idea2, Idea):
            return False
        return self.type == idea2.type and self.subtype==idea2.subtype and self.subsubtype==idea2.subsubtype

    def __eq__(self, idea2):
        if not isinstance(idea2, Idea):
            return False
        return  self.__dict__ == idea2.__dict__

    def __ne__(self, idea2):
        return not self.__eq__(idea2)

    def __str__(self, short_form=True):
        if short_form:
            return "{}".format(self.label)

        return "<{}>:{}, mod:'{}', backref:{}, glued:{}, spec:'{}', void prefix:{}".format(self.label, self.type_string(), self.modifier, self.backref, self.glue, self.specifier, self.void_appendix)
