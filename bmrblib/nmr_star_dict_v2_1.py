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
"""The base classes for the NMR-STAR dictionary support within relax.

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.
"""

# relax module imports.
from bmrblib.assembly_supercategory.entity_v2_1 import EntitySaveframe_v2_1
from bmrblib.base_classes import MissingSaveframe
from bmrblib.citations.citations import CitationsSaveframe
from bmrblib.experimental_details.experiment import ExperimentSaveframe
from bmrblib.experimental_details.method import MethodSaveframe
from bmrblib.experimental_details.nmr_spectrometer import NMRSpectrometerSaveframe
from bmrblib.experimental_details.sample_conditions_v2_1 import SampleConditionsSaveframe_v2_1
from bmrblib.experimental_details.software import SoftwareSaveframe
from bmrblib.kinetics.relaxation import Relaxation_v2_1
from bmrblib.NMR_parameters.chem_shift_anisotropy import ChemShiftAnisotropySaveframe
from bmrblib.nmr_star_dict import NMR_STAR
from bmrblib.thermodynamics.model_free import ModelFreeSaveframe
from bmrblib.pystarlib.File import File


class NMR_STAR_v2_1(NMR_STAR):
    """The v2.1 NMR-STAR dictionary."""

    def create_saveframes(self):
        """Create all the saveframe objects."""

        # Initialise Supergroup 2:  The citations.
        self.citations = CitationsSaveframe(self.data.datanodes)

        # Initialise Supergroup 3:  The molecular assembly saveframe API.
        self.entity = EntitySaveframe_v2_1(self.data.datanodes)

        # Initialise Supergroup 4:  The experimental descriptions saveframe API.
        self.experiment = ExperimentSaveframe(self.data.datanodes)
        self.method = MethodSaveframe(self.data.datanodes)
        self.nmr_spectrometer = NMRSpectrometerSaveframe(self.data.datanodes)
        self.sample_conditions = SampleConditionsSaveframe_v2_1(self.data.datanodes)
        self.software = SoftwareSaveframe(self.data.datanodes)

        # Initialise Supergroup 5:  The NMR parameters saveframe API.
        self.chem_shift_anisotropy = ChemShiftAnisotropySaveframe(self.data.datanodes)

        # Initialise Supergroup 6:  The kinetic data saveframe API.
        self.relaxation = Relaxation_v2_1(self.data.datanodes)

        # Initialise Supergroup 7:  The thermodynamics saveframe API.
        self.model_free = ModelFreeSaveframe(self.data.datanodes)

        # Initialise Supergroup 8:  The structure determination saveframes.
        self.tensor = MissingSaveframe('Tensor')
