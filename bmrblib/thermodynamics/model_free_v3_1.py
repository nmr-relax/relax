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
"""The v3.1 Heteronuclear NOE data saveframe category.

See http://www.bmrb.wisc.edu/dictionary/3.1html/SaveFramePage.html#heteronucl_NOEs.
"""

# relax module imports.
from bmrblib.thermodynamics.model_free import ModelFreeSaveframe, ModelFreeList, ModelFreeExperiment, ModelFreeSoftware, ModelFree


class ModelFreeSaveframe_v3_1(ModelFreeSaveframe):
    """The v3.1 Model_free data saveframe class."""

    def add_tag_categories(self):
        """Create the v3.1 tag categories."""

        # The tag category objects.
        self.model_free_list = ModelFreeList_v3_1(self)
        self.model_free_experiment = ModelFreeExperiment_v3_1(self)
        self.model_free_software = ModelFreeSoftware_v3_1(self)
        self.model_free = ModelFree_v3_1(self)

    def specific_setup(self):
        """Method called by self.add() to set up any version specific data."""

        self.cat_name = ['order_parameters']


class ModelFreeList_v3_1(ModelFreeList):
    """v3.1 ModelFreeList tag category."""

    def tag_setup(self, tag_category_label=None, sep=None):
        """Replacement method for setting up the tag names.

        @keyword tag_category_label:    The tag name prefix specific for the tag category.
        @type tag_category_label:       None or str
        @keyword sep:                   The string separating the tag name prefix and suffix.
        @type sep:                      str
        """

        # Category label.
        if not tag_category_label:
            tag_category_label='Order_parameter_list'

        # Execute the base class tag_setup() method.
        ModelFreeList.tag_setup(self, tag_category_label=tag_category_label, sep=sep)

        # Tag names for the relaxation data.
        self.tag_names['SfCategory'] = 'Sf_category'
        self.tag_names['ModelFreeListID'] = 'ID'
        self.tag_names['SampleConditionListLabel'] = 'Sample_condition_list_label'


class ModelFreeExperiment_v3_1(ModelFreeExperiment):
    """v3.1 ModelFreeExperiment tag category."""

    def tag_setup(self, tag_category_label=None, sep=None):
        """Replacement method for setting up the tag names.

        @keyword tag_category_label:    The tag name prefix specific for the tag category.
        @type tag_category_label:       None or str
        @keyword sep:                   The string separating the tag name prefix and suffix.
        @type sep:                      str
        """

        # Category label.
        if not tag_category_label:
            tag_category_label='Order_parameter_experiment'

        # Execute the base class tag_setup() method.
        ModelFreeExperiment.tag_setup(self, tag_category_label=tag_category_label, sep=sep)


class ModelFreeSoftware_v3_1(ModelFreeSoftware):
    """v3.1 ModelFreeSoftware tag category."""

    def tag_setup(self, tag_category_label=None, sep=None):
        """Replacement method for setting up the tag names.

        @keyword tag_category_label:    The tag name prefix specific for the tag category.
        @type tag_category_label:       None or str
        @keyword sep:                   The string separating the tag name prefix and suffix.
        @type sep:                      str
        """

        # Category label.
        if not tag_category_label:
            tag_category_label='Order_parameter_software'

        # Execute the base class tag_setup() method.
        ModelFreeSoftware.tag_setup(self, tag_category_label=tag_category_label, sep=sep)


class ModelFree_v3_1(ModelFree):
    """v3.1 ModelFree tag category."""

    def tag_setup(self, tag_category_label=None, sep=None):
        """Replacement method for setting up the tag names.

        @keyword tag_category_label:    The tag name prefix specific for the tag category.
        @type tag_category_label:       None or str
        @keyword sep:                   The string separating the tag name prefix and suffix.
        @type sep:                      str
        """

        # Category label.
        if not tag_category_label:
            tag_category_label='Order_param'

        # Execute the base class tag_setup() method.
        ModelFree.tag_setup(self, tag_category_label=tag_category_label, sep=sep)

        # Tag names for the relaxation data.
        self.tag_names['ModelFreeID'] = 'ID'
        self.tag_names['CompIndexID'] = 'Comp_index_ID'
        self.tag_names['CompID'] = 'Comp_ID'
        self.tag_names['AtomID'] = 'Atom_ID'
        self.tag_names['S2Val'] = 'S2_val'
        self.tag_names['S2ValErr'] = 'S2_val_err'
        self.tag_names['S2fVal'] = 'S2f_val'
        self.tag_names['S2fValErr'] = 'S2f_val_err'
        self.tag_names['S2sVal'] = 'S2s_val'
        self.tag_names['S2sValErr'] = 'S2s_val_err'
        self.tag_names['TauEVal'] = 'Tau_e_val'
        self.tag_names['TauEValErr'] = 'Tau_e_val_err'
        self.tag_names['TauFVal'] = 'Tau_f_val'
        self.tag_names['TauFValErr'] = 'Tau_f_val_err'
        self.tag_names['TauSVal'] = 'Tau_s_val'
        self.tag_names['TauSValErr'] = 'Tau_s_val_err'
        self.tag_names['RexVal'] = 'Rex_val'
        self.tag_names['RexValErr'] = 'Rex_val_err'
        self.tag_names['ChiSquaredVal'] = 'Chi_squared_val'
