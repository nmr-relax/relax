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
"""The v3.1 Heteronuclear NOE data saveframe category.

This file is part of the U{BMRB library<https://gna.org/projects/bmrblib>}.

See http://www.bmrb.wisc.edu/dictionary/3.1html/SaveFramePage.html#heteronucl_NOEs.
"""

# relax module imports.
from bmrblib.thermodynamics.model_free import ModelFreeSaveframe, ModelFreeList, ModelFreeExperiment, ModelFreeSoftware, ModelFree


class ModelFreeSaveframe_v3_1(ModelFreeSaveframe):
    """The v3.1 Model_free data saveframe class."""

    # Class variables.
    sf_label = 'order_parameters'

    def add_tag_categories(self):
        """Create the v3.1 tag categories."""

        # The tag category objects.
        self.tag_categories.append(ModelFreeList_v3_1(self))
        self.tag_categories.append(ModelFreeExperiment_v3_1(self))
        self.tag_categories.append(ModelFreeSoftware_v3_1(self))
        self.tag_categories.append(ModelFree_v3_1(self))



class ModelFreeList_v3_1(ModelFreeList):
    """v3.1 ModelFreeList tag category."""

    def __init__(self, sf):
        """Setup the ModelFreeList_v3_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(ModelFreeList_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Order_parameter_list'

        # Change tag names.
        self['SfCategory'].tag_name =               'Sf_category'
        self['SfFramecode'].tag_name =              'Sf_framecode'
        self['ModelFreeListID'].tag_name =          'ID'
        self['SampleConditionListLabel'].tag_name = 'Sample_condition_list_label'
        self['TaueValUnits'].tag_name =             'Tau_e_val_units'
        self['TaufValUnits'].tag_name =             'Tau_f_val_units'
        self['TausValUnits'].tag_name =             'Tau_s_val_units'



class ModelFreeExperiment_v3_1(ModelFreeExperiment):
    """v3.1 ModelFreeExperiment tag category."""

    def __init__(self, sf):
        """Setup the ModelFreeExperiment_v3_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(ModelFreeExperiment_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Order_parameter_experiment'



class ModelFreeSoftware_v3_1(ModelFreeSoftware):
    """v3.1 ModelFreeSoftware tag category."""

    def __init__(self, sf):
        """Setup the ModelFreeSoftware_v3_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(ModelFreeSoftware_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Order_parameter_software'



class ModelFree_v3_1(ModelFree):
    """v3.1 ModelFree tag category."""

    def __init__(self, sf):
        """Setup the ModelFree_v3_1 tag category.

        @param sf:  The saveframe object.
        @type sf:   saveframe instance
        """

        # Initialise the baseclass.
        super(ModelFree_v3_1, self).__init__(sf)

        # The category name.
        self.tag_category_label = 'Order_param'

        # Change the tag names.
        self['ModelFreeID'].tag_name =          'ID'
        self['CompIndexID'].tag_name =          'Comp_index_ID'
        self['CompID'].tag_name =               'Comp_ID'
        self['AtomID'].tag_name =               'Atom_ID'
        self['AtomType'].tag_name =             'Atom_type'
        self['AtomIsotopeNumber'].tag_name =    'Atom_isotope_number'
        self['S2Val'].tag_name =                'Order_param_val'
        self['S2ValErr'].tag_name =             'Order_param_val_fit_err'
        self['S2fVal'].tag_name =               'Sf2_val'
        self['S2fValErr'].tag_name =            'Sf2_val_fit_err'
        self['S2sVal'].tag_name =               'Ss2_val'
        self['S2sValErr'].tag_name =            'Ss2_val_fit_err'
        self['TauEVal'].tag_name =              'Tau_e_val'
        self['TauEValErr'].tag_name =           'Tau_e_val_fit_err'
        self['TauFVal'].tag_name =              'Tau_f_val'
        self['TauFValErr'].tag_name =           'Tau_f_val_fit_err'
        self['TauSVal'].tag_name =              'Tau_s_val'
        self['TauSValErr'].tag_name =           'Tau_s_val_fit_err'
        self['RexVal'].tag_name =               'Rex_val'
        self['RexValErr'].tag_name =            'Rex_val_fit_err'
        self['ChiSquaredVal'].tag_name =        'Chi_squared_val'

        # Set up the local_tm and bond length structures.
        self['LocalTauCVal'].tag_name =         'Local_tau_c_val'
        self['LocalTauCVal'].var_name =         'local_tm'
        self['LocalTauCValErr'].tag_name =      'Local_tau_c_val_fit_err'
        self['LocalTauCValErr'].var_name =      'local_tm_err'
        self['BondLengthVal'].tag_name =        'Bond_length_val'
        self['BondLengthVal'].var_name =        'bond_length'
