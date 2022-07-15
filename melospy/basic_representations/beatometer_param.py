""" Class implementation of Configuration values for Beatometer settings"""

from melospy.basic_representations.config_param import *
from melospy.basic_representations.jm_util import safe_set


class Sigma(ConfigParameter):
    def __init__(self, sigma=.03):
        self.setValue("sigma", sigma, float)

def_sigma = Sigma()

def setDefaultSigma(sigma):
    try:
        tmp = def_sigma.sigma
    except:
        raise RuntimeError("Default Sigma not created yet")
    def_sigma.setValue("sigma", sigma, float, False)

class WeightRules(ConfigParameter):
      """Weight Rules settings for GaussBeat class"""

      def __init__(self, method="gauss-standard", params=None):

        self.setValueWithDomainCheck("method", method, ["gauss-standard", "const"])
        if params == None:
            if method == "gauss-standard":
                params = {"baseAccent":1, "a_min":2, "a_maj":3, "sigma":def_sigma.sigma}
        self.setValue("params", params, allowNone=True)
        try:
            for k in params:
                self.setValue(k, params[k])
        except:
            pass

class GaussBeatParameters(ConfigParameter):
      """Parameter settings for GaussBeat class"""

      def __init__(self, sigma=None, deltaT=.01,
                   weight_rules=None, subjective_presence=2.0,
                   min_ioi=None, domain="folk", min_tempo=1.,
                   spontaneous_tempo=.5, beta=2., max_grad_cut=.2):

        if weight_rules == None:
            weight_rules= WeightRules()

        if sigma == "global" or sigma == None:
            sigma = def_sigma.sigma

        if min_ioi == "dynamic" or min_ioi == None :
            min_ioi = 2 * sigma

        self.setValue("sigma", sigma, (float))
        self.setValue("weight_rules", weight_rules, (WeightRules))
        self.setValue("deltaT", deltaT, (float))
        self.setValue("subjective_presence", subjective_presence, (float))
        self.setValue("min_ioi", min_ioi, (float))
        self.setValue("beta", beta, (float))
        self.setValue("min_tempo", min_tempo, (float))
        self.setValue("max_grad_cut", max_grad_cut, (float))
        self.setValue("spontaneous_tempo", spontaneous_tempo, (float))

        self.setValueWithDomainCheck("domain", domain.lower(), ["uniform", "folk", "jazz"])

class BeatometerParameters(ConfigParameter):
    """Beatometer parameter settings"""

    def __init__(self, method="gaussification",
                       params=None, window_size=6.0, hop_size=1.0,
                       glue_sigma=.1, glue_threshold=1.8,
                       single_meter=False, propagate=True):

        self.setValueWithDomainCheck("method", method.lower(), ["gaussification", "dummy"])
        if params == None and method == "gaussification":
            params = GaussBeatParameters()
        self.setValue("params", params, ConfigParameter)
        self.setValue("window_size", window_size, (float))
        self.setValue("hop_size", hop_size, (float))
        self.setValue("glue_sigma", glue_sigma, (float))
        self.setValue("glue_threshold", glue_threshold, (float))
        self.setValue("single_meter",   single_meter, bool)
        self.setValue("propagate",   propagate, bool)
        for v in params.__dict__:
            self.setValue(v, params[v])

    @staticmethod
    def fromDict(params):
        bmp = BeatometerParameters()
        for v in params:
            bmp.setValue(v, params[v])
        try:
            for v in params["gauss"]:
                self.setValue(v, params[v])
        except:
            pass
        return bmp
