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
"""The Heteronuclear NOE data saveframe category.

For example, see http://www.bmrb.wisc.edu/dictionary/3.1html/SaveFramePage.html#heteronucl_NOEs.
"""

# relax module imports.
from bmrblib.base_classes import TagCategory
from bmrblib.misc import no_missing, translate
from bmrblib.kinetics.relax_base import HeteronuclRxList, RelaxSaveframe, Rx
from bmrblib.pystarlib.SaveFrame import SaveFrame
from bmrblib.pystarlib.TagTable import TagTable


class HeteronuclNOESaveframe(RelaxSaveframe):
    """The Heteronuclear NOE data saveframe class."""

    # Saveframe variables.
    label = 'NOE'


    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Place the data nodes into the namespace.
        self.datanodes = datanodes

        # The number of relaxation data sets.
        self.noe_inc = 0

        # Add the specific tag category objects.
        self.add_tag_categories()


    def add(self, frq=None, res_nums=None, res_names=None, atom_names=None, isotope=None, data=None, errors=None):
        """Add relaxation data to the data nodes.

        @keyword frq:           The spectrometer proton frequency, in Hz.
        @type frq:              float
        @keyword res_nums:      The residue number list.
        @type res_nums:         list of int
        @keyword res_names:     The residue name list.
        @type res_names:        list of str
        @keyword atom_names:    The atom name list.
        @type atom_names:       list of str
        @keyword isotope:       The isotope type list, ie 15 for '15N'.
        @type isotope:          list of int
        @keyword data:          The relaxation data.
        @type data:             list of float
        @keyword errors:        The errors associated with the relaxation data.
        @type errors:           list of float
        """

        # Check the ID info.
        no_missing(res_nums, 'residue numbers of the ' + repr(int(frq*1e-6)) + ' MHz NOE data')
        no_missing(res_names, 'residue names of the ' + repr(int(frq*1e-6)) + ' MHz NOE data')
        no_missing(atom_names, 'atom names of the ' + repr(int(frq*1e-6)) + ' MHz NOE data')

        # The number of elements.
        self.N = len(res_nums)

        # Place the args into the namespace.
        self.frq = frq
        self.res_nums = translate(res_nums)
        self.res_names = translate(res_names)
        self.atom_names = translate(atom_names)
        self.isotope = translate(isotope)
        self.data = translate(data)
        self.errors = translate(errors)

        # Set up the NOE specific variables.
        self.noe_inc = self.noe_inc + 1
        self.rx_inc_list = translate([self.noe_inc] * self.N)
        self.generate_data_ids(self.N)

        # Set up the version specific variables.
        self.specific_setup()

        # Initialise the save frame.
        self.frame = SaveFrame(title='heteronuclear_'+self.label+'_list_'+repr(self.noe_inc))

        # Create the tag categories.
        self.heteronuclRxlist.create()
        self.heteronuclRxexperiment.create()
        self.heteronuclRxsoftware.create()
        self.Rx.create()

        # Add the saveframe to the data nodes.
        self.datanodes.append(self.frame)


    def add_tag_categories(self):
        """Create the tag categories."""

        # The tag category objects.
        self.heteronuclRxlist = HeteronuclNOEList(self)
        self.heteronuclRxexperiment = HeteronuclNOEExperiment(self)
        self.heteronuclRxsoftware = HeteronuclNOESoftware(self)
        self.Rx = HeteronuclNOE(self)


class HeteronuclNOEList(HeteronuclRxList):
    """Base class for the HeteronuclNOEList tag category."""

    def create(self):
        """Create the HeteronuclNOEList tag category."""

        # The save frame category.
        self.sf.frame.tagtables.append(self.create_tag_table([['SfCategory', 'cat_name']], free=True))

        # NOE ID number.
        if 'HeteronuclNOEListID' in self.tag_names:
            self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['HeteronuclNOEListID']], tagvalues=[[str(self.sf.noe_inc)]]))

        # Sample info.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SampleConditionListLabel']], tagvalues=[['$conditions_1']]))

        # NMR info.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SpectrometerFrequency1H']], tagvalues=[[str(self.sf.frq/1e6)]]))


    def tag_setup(self, tag_category_label=None, sep=None):
        """Replacement method for setting up the tag names.

        @keyword tag_category_label:    The tag name prefix specific for the tag category.
        @type tag_category_label:       None or str
        @keyword sep:                   The string separating the tag name prefix and suffix.
        @type sep:                      str
        """

        # Execute the base class tag_setup() method.
        TagCategory.tag_setup(self, tag_category_label=tag_category_label, sep=sep)

        # Tag names for the relaxation data.
        self.tag_names['SfCategory'] = 'Saveframe_category'
        self.tag_names['SampleConditionListLabel'] = 'Sample_conditions_label'
        self.tag_names['SpectrometerFrequency1H'] = 'Spectrometer_frequency_1H'


class HeteronuclNOEExperiment(TagCategory):
    """Base class for the HeteronuclNOEExperiment tag category."""

    def create(self):
        """Create the HeteronuclNOEExperiment tag category."""

        # Sample info.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.tag_names_full['SampleLabel']], tagvalues=[['$sample_1']]))


    def tag_setup(self, tag_category_label=None, sep=None):
        """Replacement method for setting up the tag names.

        @keyword tag_category_label:    The tag name prefix specific for the tag category.
        @type tag_category_label:       None or str
        @keyword sep:                   The string separating the tag name prefix and suffix.
        @type sep:                      str
        """

        # Execute the base class tag_setup() method.
        TagCategory.tag_setup(self, tag_category_label=tag_category_label, sep=sep)

        # Tag names for the relaxation data.
        self.tag_names['SampleLabel'] = 'Sample_label'


class HeteronuclNOESoftware(TagCategory):
    """Base class for the HeteronuclNOESoftware tag category."""

    def create(self):
        """Create the HeteronuclNOESoftware tag category."""


class HeteronuclNOE(Rx):
    """Base class for the HeteronuclNOE tag category."""
