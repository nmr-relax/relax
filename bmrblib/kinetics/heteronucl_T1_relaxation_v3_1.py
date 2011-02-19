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
"""The v3.1 Heteronuclear T1 data saveframe category.

See http://www.bmrb.wisc.edu/dictionary/3.1html/SaveFramePage.html#heteronucl_T1_relaxation.
"""

# relax module imports.
from bmrblib.misc import translate
from bmrblib.kinetics.heteronucl_T1_relaxation import HeteronuclT1Saveframe, HeteronuclT1List, HeteronuclT1Experiment, HeteronuclT1Software, T1


class HeteronuclT1Saveframe_v3_1(HeteronuclT1Saveframe):
    """The v3.1 Heteronuclear T1 data saveframe class."""

    def add_tag_categories(self):
        """Create the v3.1 tag categories."""

        # The tag category objects.
        self.heteronuclRxlist = HeteronuclT1List_v3_1(self)
        self.heteronuclRxexperiment = HeteronuclT1Experiment_v3_1(self)
        self.heteronuclRxsoftware = HeteronuclT1Software_v3_1(self)
        self.Rx = T1_v3_1(self)


    def specific_setup(self):
        """Method called by self.add() to set up any version specific data."""

        # The category name.
        self.cat_name = ['heteronucl_T1_relaxation']


class HeteronuclT1List_v3_1(HeteronuclT1List):
    """v3.1 HeteronuclT1List tag category."""

    def tag_setup(self, tag_category_label=None, sep=None):
        # Execute the base class tag_setup() method.
        HeteronuclT1List.tag_setup(self, tag_category_label='Heteronucl_T1_list', sep=sep)

        # Tag names for the relaxation data.
        self.tag_names['SfCategory'] = 'Sf_category'
        self.tag_names['HeteronuclT1ListID'] = 'ID'
        self.tag_names['SampleConditionListLabel'] = 'Sample_condition_list_label'


class HeteronuclT1Experiment_v3_1(HeteronuclT1Experiment):
    """v3.1 HeteronuclT1Experiment tag category."""

    def tag_setup(self, tag_category_label=None, sep=None):
        # Execute the base class tag_setup() method.
        HeteronuclT1Experiment.tag_setup(self, tag_category_label='Heteronucl_T1_experiment', sep=sep)


class HeteronuclT1Software_v3_1(HeteronuclT1Software):
    """v3.1 HeteronuclT1Software tag category."""

    def tag_setup(self, tag_category_label=None, sep=None):
        # Execute the base class tag_setup() method.
        HeteronuclT1Software.tag_setup(self, tag_category_label='Heteronucl_T1_software', sep=sep)


class T1_v3_1(T1):
    """v3.1 T1 tag category."""

    def tag_setup(self, tag_category_label=None, sep=None):
        # Execute the base class tag_setup() method.
        T1.tag_setup(self, tag_category_label='T1', sep=sep)

        # Tag names for the relaxation data.
        self.tag_names['RxID'] = 'ID'
        self.tag_names['CompIndexID'] = 'Comp_index_ID'
        self.tag_names['CompID'] = 'Comp_ID'
        self.tag_names['AtomID'] = 'Atom_ID'
        self.tag_names['Val'] = 'Val'
        self.tag_names['ValErr'] = 'Val_err'
