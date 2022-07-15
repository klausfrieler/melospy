""" Class for Composition Info"""

from melospy.basic_representations.form_name import FormDefinition, FormName, FormPart
from melospy.basic_representations.jm_util import get_NA_str

tonality_types = ["FUNCTIONAL", "MODAL", "COLOR", "FREE", "BLUES", "JAZZ-BLUES", ""]
genres = ["TRADITIONAL", "BLUES", "GREAT AMERICAN SONGBOOK", "WORMS", "ORIGINAL", "RIFF", ""]

class CompositionInfo(object):
    """ Class for composition info, part of solo meta data"""

    def __init__(self, title="", composer="", form="", tonality_type="", genre="", harmony_template=""):
        self.setTitle(title)
        self.setComposer(composer)
        self.setForm(form)
        self.setGenre(genre)
        self.setTonalityType(tonality_type)
        self.setHarmonyTemplate(harmony_template)

    def clone(self):
        ret = CompositionInfo()
        ret.__dict__ = {k:self.__dict__[k] for k in self.__dict__}
        return ret

    def getComposer(self):
        return self.__composer

    def setComposer(self, composer):
        self.__composer = composer
        return self

    def getTitle(self):
        return self.__title

    def setTitle(self, title):
        self.__title = title
        return self

    def getTonalityType(self):
        return self.__tonalitytype

    def setTonalityType(self, tt):
        tt = tt.upper()
        if tt not in tonality_types:
            raise ValueError("Unknown tonality type: '{}'".format(tt))
        self.__tonalitytype = tt
        return self

    def getForm(self):
        if self.__form != None:
            if isinstance(self.__form, FormDefinition):
                return self.__form.getShortForm(withLengths = True)
            else:
                return self.__form
        return ""

    def setForm(self, form):
        if isinstance(form, list):
            try:
                tmp = FormDefinition(form)
                self.__form = tmp
            except Exception as e:
                raise ValueError("Form list has incorrect syntax.")
        elif isinstance(form, str):
            try:
                self.__form = FormDefinition.fromString(form)
            except Exception as e:
                #print "Form list has incorrect syntax."
                self.__form = form
        else:
            raise TypeError("Form must be a list of tuples or a string")
        return self

    def getGenre(self):
        return self.__genre

    def setGenre(self, val):
        val = val.upper()
        tmp = val.split("-")
        if len(tmp)>1 and tmp[1].upper() =="STANDARD":
            self.__genre = val
            return self
        val = val.replace("-", "")
        if val not in genres:
            raise ValueError("Unknown genre: {}".format(val))
        self.__genre = val
        return self

    def getHarmonyTemplate(self):
        return self.__harmonytemplate

    def setHarmonyTemplate(self, harmony_template):
        self.__harmonytemplate = harmony_template
        return self

    def __eq__(self, other):
        if isinstance(other, type(None)):
            return False
        for v in self.__dict__:
            if self.__dict__[v] != other.__dict__[v]:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)


    def __str__(self):
        return "\n".join([
          "Composition Info",
          "="*40,
          "Title:           " + get_NA_str(self.__title),
          "Composer:        " + get_NA_str(self.__composer),
          "Tonality Type:   " + get_NA_str(self.__tonalitytype.upper().capitalize()),
          "Genre:           " + get_NA_str(self.__genre.lower().capitalize()),
          "Form:            " + get_NA_str(self.__form),
          "Template:        " + get_NA_str(self.__harmonytemplate)])

    composer              = property(getComposer, setComposer)
    title                 = property(getTitle, setTitle)
    form                  = property(getForm, setForm)
    tonalitytype          = property(getTonalityType, setTonalityType)
    genre                 = property(getGenre, setGenre)
    harmonytemplate       = property(getHarmonyTemplate, setHarmonyTemplate)
