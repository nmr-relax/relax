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
from bmrblib.misc import translate
from bmrblib.kinetics.heteronucl_NOEs import HeteronuclNOESaveframe, HeteronuclNOEList, HeteronuclNOEExperiment, HeteronuclNOESoftware, HeteronuclNOE


class HeteronuclNOESaveframe_v3_1(HeteronuclNOESaveframe):
    """The v3.1 Heteronuclear NOE data saveframe class."""

    def add_tag_categories(self):
        """Create the v3.1 tag categories."""

        # The tag category objects.
        self.heteronuclRxlist = HeteronuclNOEList_v3_1(self)
        self.heteronuclRxexperiment = HeteronuclNOEExperiment_v3_1(self)
        self.heteronuclRxsoftware = HeteronuclNOESoftware_v3_1(self)
        self.Rx = HeteronuclNOE_v3_1(self)


    def specific_setup(self):
        """Method called by self.add() to set up any version specific data."""

        # The category name.
        self.cat_name = ['heteronucl_NOEs']


class HeteronuclNOEList_v3_1(HeteronuclNOEList):
    """v3.1 HeteronuclNOEList tag category."""

    def tag_setup(self, tag_category_label=None, sep=None):
        # Execute the base class tag_setup() method.
        HeteronuclNOEList.tag_setup(self, tag_category_label='Heteronucl_NOE_list', sep=sep)

        # Tag names for the relaxation data.
        self.tag_names['SfCategory'] = 'Sf_category'
        self.tag_names['HeteronuclNOEListID'] = 'ID'
        self.tag_names['SampleConditionListLabel'] = 'Sample_condition_list_label'


class HeteronuclNOEExperiment_v3_1(HeteronuclNOEExperiment):
    """v3.1 HeteronuclNOEExperiment tag category."""

    def tag_setup(self, tag_category_label=None, sep=None):
        # Execute the base class tag_setup() method.
        HeteronuclNOEExperiment.tag_setup(self, tag_category_label='Heteronucl_NOE_experiment', sep=sep)


class HeteronuclNOESoftware_v3_1(HeteronuclNOESoftware):
    """v3.1 HeteronuclNOESoftware tag category."""

    def tag_setup(self, tag_category_label=None, sep=None):
        # Execute the base class tag_setup() method.
        HeteronuclNOESoftware.tag_setup(self, tag_category_label='Heteronucl_NOE_software', sep=sep)


class HeteronuclNOE_v3_1(HeteronuclNOE):
    """v3.1 HeteronuclNOE tag category."""

    def tag_setup(self, tag_category_label=None, sep=None):
        # Execute the base class tag_setup() method.
        HeteronuclNOE.tag_setup(self, tag_category_label='Heteronucl_NOE', sep=sep)

        # Tag names for the relaxation data.
        self.tag_names['RxID'] = 'ID'
        self.tag_names['CompIndexID'] = 'Comp_index_ID'
        self.tag_names['CompID'] = 'Comp_ID'
        self.tag_names['AtomID'] = 'Atom_ID'
        self.tag_names['Val'] = 'Val'
        self.tag_names['ValErr'] = 'Val_err'
