""" General source module """

from melospy.feature_machine.feature_module_base import MelopyFeatureModuleBase
from melospy.feature_machine.feature_module_parameter import MelopyFeatureModuleParameter


class MelopyFeatureModuleSource(MelopyFeatureModuleBase):

    def __init__(self, ):
        """ Initialize module """
        MelopyFeatureModuleBase.__init__(self, "source")
        # define module parameters
        self.addInputParameter(MelopyFeatureModuleParameter("param", False, "pitch"))
        self.addInputParameter(MelopyFeatureModuleParameter("aggregationOver", False, None))
        self.addInputParameter(MelopyFeatureModuleParameter("optParam", False, None))
        self.addInputParameter(MelopyFeatureModuleParameter("filterFunction", False, None))
        self.addOutputParameter(MelopyFeatureModuleParameter("outputVec"))

    def process(self, exporter):
        self.checkInputParameters()
        filterFunction = self.getParameterValue("filterFunction")
        if filterFunction is None:
            vec = exporter.export(self.getParameterValue("param"), \
                                    self.getParameterValue("aggregationOver"), self.getParameterValue("optParam"))
            if not isinstance(vec, list):
                vec = [vec]
            self.setParameterValue("outputVec", vec)
        else:
            # TODO: write filter functions (triller filter etc) in new class, import it here and add some else-branches...
            # TODO: use it like
            #             self.setParameterValue("outputVec", filterClass.filterFuncXY(exporter.export(self.getParameterValue("param"), \
#                                                self.getParameterValue("aggregationOver"),self.getParameterValue("optionalParametersForExporter"))))

            raise Exception("No other filter is yet defined ...")
