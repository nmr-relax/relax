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
"""The Heteronuclear T2 data saveframe category.

For example, see http://www.bmrb.wisc.edu/dictionary/3.1html/SaveFramePage.html#heteronucl_T2_relaxation.
"""

# relax module imports.
from bmrblib.tag_category import TagCategory
from pystarlib.SaveFrame import SaveFrame
from pystarlib.TagTable import TagTable


class HeteronuclT2Saveframe:
    """The Heteronuclear T2 data saveframe class."""

    # Saveframe variables.
    label = 'T2'


    def __init__(self, datanodes):
        """Initialise the class, placing the pystarlib data nodes into the namespace.

        @param datanodes:   The pystarlib data nodes object.
        @type datanodes:    list
        """

        # Place the data nodes into the namespace.
        self.datanodes = datanodes

        # The number of relaxation data sets.
        self.r1_inc = 0

        # Add the specific tag category objects.
        self.add_tag_categories()


    def add(self, frq=None, res_nums=None, res_names=None, atom_names=None, data=None, errors=None):
        """Add relaxation data to the data nodes.

        @keyword frq:           The spectrometer proton frequency, in Hz.
        @type frq:              float
        @keyword res_nums:      The residue number list.
        @type res_nums:         list of int
        @keyword res_names:     The residue name list.
        @type res_names:        list of str
        @keyword atom_names:    The atom name list.
        @type atom_names:       list of str
        @keyword data:          The relaxation data.
        @type data:             list of float
        @keyword errors:        The errors associated with the relaxation data.
        @type errors:           list of float
        """

        # Place the args into the namespace.
        self.frq = frq
        self.res_nums = res_nums
        self.res_names = res_names
        self.atom_names = atom_names
        self.data = data
        self.errors = errors

        # Set up the R1 specific variables.
        self.r1_inc = self.r1_inc + 1
        ri_inc = self.r1_inc

        # Initialise the save frame.
        self.frame = SaveFrame(title='heteronuclear_'+self.label+'_list_'+`ri_inc`)

        # Create the tag categories.
        self.heteronuclT2list.create()
        self.heteronuclT2experiment.create()
        self.heteronuclT2software.create()
        self.T2.create()

        # Add the saveframe to the data nodes.
        self.datanodes.append(self.frame)


    def add_tag_categories(self):
        """Create the v3.1 tag categories."""

        # The tag category objects.
        self.heteronuclT2list = HeteronuclT2List(self)
        self.heteronuclT2experiment = HeteronuclT2Experiment(self)
        self.heteronuclT2software = HeteronuclT2Software(self)
        self.T2 = T2(self)


class HeteronuclT2List(TagCategory):
    """Base class for the HeteronuclT2List tag category."""


    def create(self):
        """Create the HeteronuclT2List tag category."""

        # The save frame category.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.create_tag_label(self.tag_names['SfCategory'])], tagvalues=[[self.sf.label+'_relaxation']]))

        # Sample info.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.create_tag_label(self.tag_names['SampleConditionListLabel'])], tagvalues=[['$conditions_1']]))

        # NMR info.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.create_tag_label(self.tag_names['SpectrometerFrequency1H'])], tagvalues=[[str(self.sf.frq/1e6)]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.create_tag_label(self.tag_names['T2CoherenceType'])], tagvalues=[[self.variables['coherence']]]))
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.create_tag_label(self.tag_names['T2ValUnits'])], tagvalues=[['1/s']]))


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
        self.tag_names['T2CoherenceType'] = 'T2_coherence_type'
        self.tag_names['T2ValUnits'] = 'T2_value_units'

        # Class variables.
        self.variables['coherence'] = 'Ny'


class HeteronuclT2Experiment(TagCategory):
    """Base class for the HeteronuclT2Experiment tag category."""

    def create(self, frame=None):
        """Create the HeteronuclT2Experiment tag category."""

        # Sample info.
        self.sf.frame.tagtables.append(TagTable(free=True, tagnames=[self.create_tag_label(self.tag_names['SampleLabel'])], tagvalues=[['$sample_1']]))


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


class HeteronuclT2Software(TagCategory):
    """Base class for the HeteronuclT2Software tag category."""

    def create(self):
        """Create the HeteronuclT2Software tag category."""


class T2(TagCategory):
    """Base class for the T2 tag category."""

    def create(self):
        """Create the T2 tag category."""

        # The relaxation tag names.
        tag_names = []
        missing = []
        for key in ['SeqID', 'CompID', 'AtomID', 'Val', 'ValErr']:
            if not self.tag_names.has_key(key):
                missing.append(key)
            else:
                tag_names.append(self.create_tag_label(self.tag_names[key]))

        # The tag values.
        tag_values = []
        if 'SeqID' not in missing:
            tag_values.append(self.sf.res_nums)
        if 'CompID' not in missing:
            tag_values.append(self.sf.res_names)
        if 'AtomID' not in missing:
            tag_values.append(self.sf.atom_names)
        if 'Val' not in missing:
            tag_values.append(self.sf.data)
        if 'ValErr' not in missing:
            tag_values.append(self.sf.errors)

        # Add the data.
        table = TagTable(tagnames=tag_names, tagvalues=tag_values)

        # Add the tagtable to the save frame.
        self.sf.frame.tagtables.append(table)


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
        self.tag_names['SeqID'] = 'Residue_seq_code'
        self.tag_names['CompID'] = 'Residue_label'
        self.tag_names['AtomID'] = 'Atom_name'
        self.tag_names['Val'] = self.sf.label+'_value'
        self.tag_names['ValErr'] = self.sf.label+'_value_error'
