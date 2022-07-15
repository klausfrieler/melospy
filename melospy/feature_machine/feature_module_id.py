""" id module - just used as forwarder of input data """

from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class MelopyFeatureModuleId(MelopyFeatureModuleBase):

    def __init__(self):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "id")
        # define module parameters
        self.addInputParameter(MelopyFeatureModuleParameter("inputVec", True))
        self.addOutputParameter(MelopyFeatureModuleParameter("outputVec"))

    def process(self):
        self.checkInputParameters()
        self.setParameterValue("outputVec", self.getParameterValue("inputVec"))
