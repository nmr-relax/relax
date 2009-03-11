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
from bmrblib.thermodynamics.order_parameters import OrderParameterSaveframe, OrderParameterList, OrderParameterExperiment, OrderParameterSoftware, OrderParameter


class OrderParameterSaveframe_v3_1(OrderParameterSaveframe):
    """The v3.1 Order parameters data saveframe class."""

    def add_tag_categories(self):
        """Create the v3.1 tag categories."""

        # The tag category objects.
        self.order_parameter_list = OrderParameterList_v3_1(self)
        self.order_parameter_experiment = OrderParameterExperiment_v3_1(self)
        self.order_parameter_software = OrderParameterSoftware_v3_1(self)
        self.order_parameter = OrderParameter_v3_1(self)

    def specific_setup(self):
        """Method called by self.add() to set up any version specific data."""

        self.cat_name = ['order_parameters']


class OrderParameterList_v3_1(OrderParameterList):
    """v3.1 OrderParameterList tag category."""

    def tag_setup(self, tag_category_label=None, sep=None):
        # Execute the base class tag_setup() method.
        OrderParameterList.tag_setup(self, tag_category_label='Order_parameter_list', sep=sep)

        # Tag names for the relaxation data.
        self.tag_names['SfCategory'] = 'Sf_category'
        self.tag_names['OrderParameterListID'] = 'ID'
        self.tag_names['SampleConditionListLabel'] = 'Sample_condition_list_label'


class OrderParameterExperiment_v3_1(OrderParameterExperiment):
    """v3.1 OrderParameterExperiment tag category."""

    def tag_setup(self, tag_category_label=None, sep=None):
        # Execute the base class tag_setup() method.
        OrderParameterExperiment.tag_setup(self, tag_category_label='Order_parameter_experiment', sep=sep)


class OrderParameterSoftware_v3_1(OrderParameterSoftware):
    """v3.1 OrderParameterSoftware tag category."""

    def tag_setup(self, tag_category_label=None, sep=None):
        # Execute the base class tag_setup() method.
        OrderParameterSoftware.tag_setup(self, tag_category_label='Order_parameter_software', sep=sep)


class OrderParameter_v3_1(OrderParameter):
    """v3.1 OrderParameter tag category."""

    def tag_setup(self, tag_category_label=None, sep=None):
        # Execute the base class tag_setup() method.
        OrderParameter.tag_setup(self, tag_category_label='Order_param', sep=sep)

        # Tag names for the relaxation data.
        self.tag_names['OrderParamID'] = 'ID'
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
