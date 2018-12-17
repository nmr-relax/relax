#############################################################################
#                                                                           #
# The BMRB library.                                                         #
#                                                                           #
# Copyright (C) 2009-2013 Edward d'Auvergne                                 #
#                                                                           #
# This program is free software: you can redistribute it and/or modify      #
# it under the terms of the GNU General Public License as published by      #
# the Free Software Foundation, either version 3 of the License, or         #
# (at your option) any later version.                                       #
#                                                                           #
# This program is distributed in the hope that it will be useful,           #
# but WITHOUT ANY WARRANTY; without even the implied warranty of            #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the             #
# GNU General Public License for more details.                              #
#                                                                           #
# You should have received a copy of the GNU General Public License         #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.     #
#                                                                           #
#############################################################################

# Module docstring.
"""The NMR-STAR dictionary API for version 3.1.

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.

The v3.1 NMR-STAR dictionary is documented at U{http://www.bmrb.wisc.edu/dictionary/}.
"""

# relax module imports.
from bmrblib.assembly_supercategory.entity_v3_1 import EntitySaveframe_v3_1
from bmrblib.citations.citations_v3_1 import CitationsSaveframe_v3_1
from bmrblib.experimental_details.experiment_v3_1 import ExperimentSaveframe_v3_1
from bmrblib.experimental_details.method_v3_1 import MethodSaveframe_v3_1
from bmrblib.experimental_details.nmr_spectrometer_v3_1 import NMRSpectrometerSaveframe_v3_1
from bmrblib.experimental_details.sample_conditions_v3_1 import SampleConditionsSaveframe_v3_1
from bmrblib.experimental_details.software_v3_1 import SoftwareSaveframe_v3_1
from bmrblib.kinetics.relaxation import Relaxation_v3_1
from bmrblib.NMR_parameters.chem_shift_anisotropy_v3_1 import ChemShiftAnisotropySaveframe_v3_1
from bmrblib.structure.tensor import TensorSaveframe
from bmrblib.thermodynamics.model_free_v3_1 import ModelFreeSaveframe_v3_1
from bmrblib.nmr_star_dict import NMR_STAR


class NMR_STAR_v3_1(NMR_STAR):
    """The v3.1 NMR-STAR dictionary."""

    def create_saveframes(self):
        """Create all the saveframe objects."""

        # Initialise Supergroup 2:  The citations.
        self.citations = CitationsSaveframe_v3_1(self.data.datanodes)

        # Initialise Supergroup 3:  The molecular assembly saveframe API.
        self.entity = EntitySaveframe_v3_1(self.data.datanodes)

        # Initialise Supergroup 4:  The experimental descriptions saveframe API.
        self.experiment = ExperimentSaveframe_v3_1(self.data.datanodes)
        self.method = MethodSaveframe_v3_1(self.data.datanodes)
        self.nmr_spectrometer = NMRSpectrometerSaveframe_v3_1(self.data.datanodes)
        self.sample_conditions = SampleConditionsSaveframe_v3_1(self.data.datanodes)
        self.software = SoftwareSaveframe_v3_1(self.data.datanodes)

        # Initialise Supergroup 5:  The NMR parameters saveframe API.
        self.chem_shift_anisotropy = ChemShiftAnisotropySaveframe_v3_1(self.data.datanodes)

        # Initialise Supergroup 6:  The kinetic data saveframe API.
        self.relaxation = Relaxation_v3_1(self.data.datanodes)

        # Initialise Supergroup 7:  The thermodynamics saveframe API.
        self.model_free = ModelFreeSaveframe_v3_1(self.data.datanodes)

        # Initialise Supergroup 8:  The structure determination saveframes.
        self.tensor = TensorSaveframe(self.data.datanodes)
