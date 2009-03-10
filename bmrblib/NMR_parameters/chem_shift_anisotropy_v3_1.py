###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Module docstring.
"""The v3.1 chemical shift anisotropy data saveframe category.

See http://www.bmrb.wisc.edu/dictionary/3.1html_frame/frame_SaveFramePage.html#chem_shift_anisotropy
"""

# relax module imports.
from bmrblib.misc import translate
from bmrblib.NMR_parameters.chem_shift_anisotropy import ChemShiftAnisotropySaveframe, ChemShiftAnisotropy, CSAnisotropyExperiment, CSAnisotropySoftware, CSAnisotropy


class ChemShiftAnisotropySaveframe_v3_1(ChemShiftAnisotropySaveframe):
    """The v3.1 chemical shift anisotropy data saveframe class."""

    def add_tag_categories(self):
        """Create the v3.1 tag categories."""

        # The tag category objects.
        self.Chem_shift_anisotropy = ChemShiftAnisotropy_v3_1(self)
        self.CS_anisotropy_experiment = CSAnisotropyExperiment_v3_1(self)
        self.CS_anisotropy_software = CSAnisotropySoftware_v3_1(self)
        self.CS_anisotropy = CSAnisotropy_v3_1(self)


class ChemShiftAnisotropy_v3_1(ChemShiftAnisotropy):
    """v3.1 ChemShiftAnisotropy tag category."""

    def tag_setup(self, tag_category_label=None, sep=None):
        # Execute the base class tag_setup() method.
        ChemShiftAnisotropy.tag_setup(self, tag_category_label='Chem_shift_anisotropy', sep=sep)

        # Tag names for the relaxation data.
        self.tag_names['SfCategory'] = 'Sf_category'
        self.tag_names['ChemShiftAnisotropyID'] = 'ID'
        self.tag_names['SampleConditionListLabel'] = 'Sample_condition_list_label'


class CSAnisotropyExperiment_v3_1(CSAnisotropyExperiment):
    """v3.1 CSAnisotropyExperiment tag category."""

    def tag_setup(self, tag_category_label=None, sep=None):
        # Execute the base class tag_setup() method.
        CSAnisotropyExperiment.tag_setup(self, tag_category_label='CS_anisotropy_experiment', sep=sep)


class CSAnisotropySoftware_v3_1(CSAnisotropySoftware):
    """v3.1 CSAnisotropySoftware tag category."""

    def tag_setup(self, tag_category_label=None, sep=None):
        # Execute the base class tag_setup() method.
        CSAnisotropySoftware.tag_setup(self, tag_category_label='CS_anisotropy_software', sep=sep)


class CSAnisotropy_v3_1(CSAnisotropy):
    """v3.1 CSAnisotropy tag category."""

    def tag_setup(self, tag_category_label=None, sep=None):
        # Execute the base class tag_setup() method.
        CSAnisotropy.tag_setup(self, tag_category_label='CS_anisotropy', sep=sep)

        # Tag names for the relaxation data.
        self.tag_names['CSAnisotropyID'] = 'ID'
        self.tag_names['CompIndexID'] = 'Comp_index_ID'
        self.tag_names['CompID'] = 'Comp_ID'
        self.tag_names['AtomID'] = 'Atom_ID'
        self.tag_names['Val'] = 'Val'
        self.tag_names['ValErr'] = 'Val_err'
